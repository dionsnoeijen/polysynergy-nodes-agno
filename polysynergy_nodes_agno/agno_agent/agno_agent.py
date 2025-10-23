import uuid
from textwrap import dedent
from typing import Literal, cast, Any

from agno.agent import Agent
from agno.db import BaseDb
from agno.db.base import SessionType
from agno.models.base import Model
from agno.team import Team
from agno.media import Image, Audio, Video

from polysynergy_node_runner.setup_context.dock_property import dock_text_area, dock_property, dock_dict
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_error import NodeError
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.path_settings import PathSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

from polysynergy_nodes_agno.agno_agent.utils.extract_props_from_settings import extract_props_from_settings
from polysynergy_nodes_agno.agno_agent.utils.find_connected_service import find_connected_service
from polysynergy_nodes_agno.agno_agent.utils.find_connected_db_settings import find_connected_db_settings
from polysynergy_nodes_agno.agno_agent.utils.find_connected_path_tools import find_connected_path_tools
from polysynergy_nodes_agno.agno_agent.utils.find_connected_settings import find_connected_settings
from polysynergy_nodes_agno.agno_agent.utils.find_connected_tools import find_connected_tools
from polysynergy_nodes_agno.agno_agent.utils.find_connected_guardrails import find_connected_guardrails
from polysynergy_nodes_agno.agno_agent.utils.has_connected_agent_or_team import has_connected_agent_or_team
from polysynergy_nodes_agno.agno_agent.utils.find_connected_prompt import find_connected_prompt
from polysynergy_nodes_agno.agno_agent.utils.send_chat_stream_event import send_chat_stream_event
from polysynergy_nodes_agno.agno_agent.utils.create_tool_hook import create_tool_hook
from polysynergy_nodes_agno.agno_agent.utils.build_tool_mapping import build_tool_mapping
from polysynergy_nodes_agno.agno_agent.utils.generate_presigned_urls import generate_presigned_urls_for_files
from polysynergy_nodes_agno.agno_agent.utils.download_images_as_base64 import download_images_as_base64


@node(
    name="Agno Agent",
    category="agno_agent",
    icon="agno.svg",
)
class AgnoAgent(ServiceNode):

    avatar: str = NodeVariableSettings(
        label="Avatar",
        dock=dock_property(metadata={"custom": "openai_avatar"}),
        metadata={"custom": "openai_avatar"},
    )

    model: Model | None = NodeVariableSettings(
        label="Model",
        has_in=True
    )
    
    db: BaseDb | None = NodeVariableSettings(
        label="Db",
        has_in=True,
        info="Storage backend for conversation history (e.g., DynamoDB, SQLite)"
    )

    debug_mode: bool = NodeVariableSettings(
        dock=True,
        node=False,
        info="Enable debug logs for this agent."
    )

    debug_level: str = NodeVariableSettings(
        node=False,
        dock=dock_property(select_values={"1": "1", "2": "2"}),
        info="Debug verbosity level: 1 = basic, 2 = detailed."
    )

    # Removed monitoring - AgentOS handles this in v2

    telemetry: bool = NodeVariableSettings(
        dock=True,
        info="If True, enables minimal telemetry for usage analytics and diagnostics.",
        node=False
    )

    show_full_reasoning: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Show the full reasoning process from reasoning models (o1, o3-mini, gpt-5-mini, DeepSeek-R1, etc.)",
        node=False
    )

    # INPUT

    agent_or_team: Agent | Team | None = NodeVariableSettings(
        has_in=True,
        info="Specify whether this tool is for an agent or a team.",
    )

    prompt: str = NodeVariableSettings(
        label="Prompt",
        dock=True,
        has_in=True,
        info="The prompt or task description for the agent to execute."
    )

    files: list | None = NodeVariableSettings(
        label="Files",
        dock=True,
        has_in=True,
        info="List of file URLs/paths for the agent to process (images, audio, video, documents)."
    )

    guardrails: list | Any | None = NodeVariableSettings(
        label="Guardrails",
        dock=True,
        has_in=True,
        info="List of guardrails to validate agent inputs (PII detection, prompt injection, moderation, etc.)"
    )

    agent_name: str | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="The name of the agent, visible in the chat.",
    )

    user_id: str | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="Default user ID to associate with this agent during runs."
    )

    user: dict | None = NodeVariableSettings(
        label="User Context",
        dock=True,
        has_in=True,
        info="Full user context (name, email, role, etc.) - automatically injected into agent instructions"
    )

    session_id: str | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="Unique session ID to group messages. Leave empty to auto-generate."
    )

    session_name: str | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="Optional name for the session, useful for debugging or display."
    )

    role: str | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="If this agent is part of a team, this is its role."
    )

    # Removed introduction - not supported in Agno v2

    description: str | None = NodeVariableSettings(
        dock=dock_text_area(rich=True),
        has_in=True,
        info="A description of the agent, added to the start of the system message."
    )

    instructions: str | None = NodeVariableSettings(
        dock=dock_text_area(rich=True),
        has_in=True,
        info="Instructions for the agent. Can be a string, list, or callable."
    )

    # Removed goal - not supported in Agno v2

    expected_output: str | None = NodeVariableSettings(
        dock=dock_text_area(),
        has_in=True,
        info="The expected output from the agent, included in the prompt."
    )

    retries: int = NodeVariableSettings(
        group="response",
        dock=True,
        default=0,
        info="Number of times to retry the agent if an error occurs.",
        node=False
    )

    delay_between_retries: int = NodeVariableSettings(
        group="response",
        dock=True,
        info="Time in seconds to wait between retries.",
        default=1,
        node=False
    )

    exponential_backoff: bool = NodeVariableSettings(
        group="response",
        dock=True,
        info="If true, the delay between retries will double after each attempt.",
        node=False
    )

    # SETTINGS

    settings: dict = NodeVariableSettings(
        dock=dock_dict(
            enabled=False,
            key_label="Setting name",
            value_label="Setting value",
            in_switch=False,
            out_switch=False,
            type_field=False,
            in_switch_default=True,
            out_switch_default=False,
            info="Custom settings for the agent. Can include tool configurations or other parameters."
        ),
        info="Additional settings for the agent, such as tool configurations or custom parameters.",
        has_in=True,
        default=[
            {
                "handle": "context",
                "has_in": True,
                "has_out": False,
                "published": False,
                "type": "polysynergy_nodes_agno.agent.agent_settings_context.AgentSettingsContext",
                "value": "polysynergy_nodes_agno.agent.agent_settings_context.AgentSettingsContext",
            },
            {
                "handle": "knowledge",
                "has_in": True,
                "has_out": False,
                "published": False,
                "type": "polysynergy_nodes_agno.agent.agent_settings_knowledge.AgentSettingsKnowledge",
                "value": "polysynergy_nodes_agno.agent.agent_settings_knowledge.AgentSettingsKnowledge",
            },
            {
                "handle": "messaging",
                "has_in": True,
                "has_out": False,
                "published": False,
                "type": "polysynergy_nodes_agno.agent.agent_settings_messaging.AgentSettingsMessaging",
                "value": "polysynergy_nodes_agno.agent.agent_settings_messaging.AgentSettingsMessaging",
            },
            {
                "handle": "reasoning",
                "has_in": True,
                "has_out": False,
                "published": False,
                "type": "polysynergy_nodes_agno.agent.agent_settings_reasoning.AgentSettingsReasoning",
                "value": "polysynergy_nodes_agno.agent.agent_settings_reasoning.AgentSettingsReasoning",
            },
            {
                "handle": "response_model",
                "has_in": True,
                "has_out": False,
                "published": False,
                "type": "polysynergy_nodes_agno.agent.agent_settings_response_model.AgentSettingsResponseModel",
                "value": "polysynergy_nodes_agno.agent.agent_settings_response_model.AgentSettingsResponseModel",
            },
            {
                "handle": "session",
                "has_in": True,
                "has_out": False,
                "published": False,
                "type": "polysynergy_nodes_agno.agent.agent_settings_session.AgentSettingsSession",
                "value": "polysynergy_nodes_agno.agent.agent_settings_session.AgentSettingsSession",
            },
            {
                "handle": "storage",
                "has_in": True,
                "has_out": False,
                "published": False,
                "type": "polysynergy_nodes_agno.agent.agent_settings_storage.AgentSettingsStorage",
                "value": "polysynergy_nodes_agno.agent.agent_settings_storage.AgentSettingsStorage",
            },
            {
                "handle": "streaming",
                "has_in": True,
                "has_out": False,
                "published": False,
                "type": "polysynergy_nodes_agno.agent.agent_settings_streaming.AgentSettingsStreaming",
                "value": "polysynergy_nodes_agno.agent.agent_settings_streaming.AgentSettingsStreaming",
            },
            {
                "handle": "team",
                "has_in": True,
                "has_out": False,
                "published": False,
                "type": "polysynergy_nodes_agno.agent.agent_settings_team.AgentSettingsTeam",
                "value": "polysynergy_nodes_agno.agent.agent_settings_team.AgentSettingsTeam",
            },
            {
                "handle": "tools",
                "has_in": True,
                "has_out": False,
                "published": False,
                "type": "polysynergy_nodes_agno.agent.agent_settings_tools.AgentSettingsTools",
                "value": "polysynergy_nodes_agno.agent.agent_settings_tools.AgentSettingsTools",
            },
            {
                "handle": "workflow",
                "has_in": True,
                "has_out": False,
                "published": False,
                "type": "polysynergy_nodes_agno.agent.agent_settings_workflow.AgentSettingsWorkflow",
                "value": "polysynergy_nodes_agno.agent.agent_settings_workflow.AgentSettingsWorkflow",
            }
        ]
    )

    instance: Agent = NodeVariableSettings(
        label="Agent Instance",
        info="Instance of the agent created by this node.",
        has_in=True,
        has_out=True,
        type="polysynergy_nodes_agno.agent.agno_agent.AgnoAgent"
    )

    # OUTGOING

    tools: bool = NodeVariableSettings(
        has_out=True,
        out_type_override="agno.agent.agent.Agent",
        info="List of tools available to the model. Tools can be functions, Toolkits, or dict definitions.",
    )

    path_tools: str | None = NodeVariableSettings(
        label="Flow Tools",
        has_out=True,
        default=[],
        info="Flow tools that execute subflows as agent tools."
    )

    # METRICS

    metrics: dict = NodeVariableSettings(
        dock=False,
        has_out=True,
        info="Metrics collected during agent execution, such as response time or token usage."
    )

    # HUMAN-IN-THE-LOOP STATE

    _paused_run_response: any = None  # Private - not serialized to DynamoDB
    # Agno agents maintain their own state, so we don't need to store the run_response

    user_input_data: dict | bool | None = NodeVariableSettings(
        label="User Input Data",
        dock=True,
        has_in=True,
        has_out=False,
        info="User's input to resume paused execution (dict for input, bool for confirmation)"
    )

    pause_reason: str | None = NodeVariableSettings(
        label="Pause Reason",
        dock=False,
        has_out=True,
        info="Why execution paused: 'confirmation', 'user_input', 'external_tool'"
    )

    pause_info: dict | None = NodeVariableSettings(
        label="Pause Info",
        dock=False,
        has_out=True,
        info="Details about the pause (type, schema, message) for UI display"
    )

    # OUTPUT

    true_path: bool | str = PathSettings("Answer", info="This is the path for successful execution.")
    false_path: bool | str | dict = PathSettings("Error", info="This is the path for errors during execution.")

    async def _setup(self):
        model = await find_connected_service(self, "model", Model)

        if not model:
            raise ValueError("No model connected. Please connect a Model node.")

        db = await find_connected_service(self, "db", BaseDb)
        storage_settings = find_connected_db_settings(self)

        settings = await find_connected_settings(self)
        tool_info_list = await find_connected_tools(self)
        path_tools = find_connected_path_tools(self)

        raw_level = self.debug_level or "1"  # default naar "1" als None of lege string
        debug_level = cast(Literal[1, 2], int(raw_level))

        return model, db, storage_settings, settings, tool_info_list, path_tools, debug_level

    async def _create_agent(self):
        (model,
         db,
         storage_settings,
         settings,
         tool_info_list,
         path_tools,
         debug_level
         ) = await self._setup()

        props = extract_props_from_settings(settings)
        props.update(storage_settings)

        # Auto-disable streaming if no prompt node is connected
        # (streaming only makes sense for interactive chat)
        if 'stream' not in props:
            # Check if there's a prompt node connected (regardless of data)
            has_prompt_node = False
            for conn in self.get_in_connections():
                source_node = self.state.get_node_by_id(conn.source_node_id)
                if source_node and source_node.path == 'polysynergy_nodes.play.prompt.Prompt':
                    has_prompt_node = True
                    break

            if has_prompt_node:
                # Prompt connected → enable streaming for interactive chat
                props['stream'] = True
                print("[Agent] Prompt node connected, auto-enabled streaming")
            else:
                # No prompt connected → disable streaming
                props['stream'] = False
                print("[Agent] No prompt node connected, auto-disabled streaming")

        # Debug logging
        print(f"DB settings: {storage_settings}")
        print(f"enable_user_memories in props: {props.get('enable_user_memories', 'NOT FOUND')}")
        print(f"DEBUG: response_model in props: {props.get('response_model', 'NOT FOUND')}")
        if 'response_model' in props:
            print(f"DEBUG: response_model type: {type(props['response_model'])}")
            print(f"DEBUG: response_model value: {props['response_model']}")

        # Build tool instances and mapping using utility
        tool_instances, function_name_to_node_id, mcp_toolkits = await build_tool_mapping(tool_info_list, path_tools)

        # Create tool hook using utility
        tool_hook = create_tool_hook(self.context, function_name_to_node_id, mcp_toolkits)

        # Get connected guardrails
        guardrails = find_connected_guardrails(self)

        # Check for connected prompt node - prompt overrides manual settings
        prompt_data = find_connected_prompt(self)
        final_user_id = self.user_id
        final_session_id = self.session_id
        final_session_name = self.session_name
        final_files = self.files or []

        if prompt_data:
            final_user_id = prompt_data['user_id']
            final_session_id = prompt_data['session_id']
            final_session_name = prompt_data['session_name']
            final_files = prompt_data.get('files', []) or []
            print(f'PROMPT OVERRIDE: user_id={final_user_id}, session_id={final_session_id}, session_name={final_session_name}, files={len(final_files)} items')
        else:
            print(f'MANUAL SETTINGS: user_id={final_user_id}, session_id={final_session_id}, session_name={final_session_name}, files={len(final_files)} items')
            
        # Generate defaults if needed for DB history to work
        if db and not final_session_id:
            final_session_id = str(uuid.uuid4())
            print(f'GENERATED SESSION ID: {final_session_id}')
        if db and not final_user_id:
            final_user_id = "default_user"
            print(f'USING DEFAULT USER ID: {final_user_id}')

        try:
            self.instance = Agent(
                id=self.id,
                model=model,
                db=db,
                name=self.agent_name,
                user_id=final_user_id,
                session_id=final_session_id,
                role=self.role,
                description=dedent(self.description) if self.description else None,
                instructions=dedent(self.instructions) if self.instructions else None,
                expected_output=dedent(self.expected_output) if self.expected_output else None,
                retries=self.retries,
                delay_between_retries=self.delay_between_retries,
                exponential_backoff=self.exponential_backoff,
                tools=tool_instances or [],
                debug_mode=self.debug_mode,
                debug_level=debug_level,
                telemetry=self.telemetry,
                tool_hooks=[tool_hook],
                pre_hooks=guardrails if guardrails else [],
                events_to_skip=[],
                **props  # stream=True comes from props (set as default on line 382)
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise

    async def provide_instance(self) -> Agent:
        await self._create_agent()
        return self.instance

    async def _handle_pause(self, run_response):
        """Handle agent pause - store state and prepare pause info for UI"""
        print(f"[HITL] Agent execution paused - awaiting user input")

        # Store the paused run response for resume (private - not serialized to DynamoDB)
        self._paused_run_response = run_response

        pause_info = {
            "paused": True,
            "run_id": getattr(run_response, 'run_id', None)
        }

        # Detect pause type and extract relevant info
        if hasattr(run_response, 'tools_requiring_confirmation') and run_response.tools_requiring_confirmation:
            self.pause_reason = "confirmation"
            tools_info = []
            for tool in run_response.tools_requiring_confirmation:
                tools_info.append({
                    "tool_name": tool.tool_name,
                    "tool_args": tool.tool_args if hasattr(tool, 'tool_args') else None
                })
            pause_info["type"] = "confirmation"
            pause_info["tools"] = tools_info
            pause_info["message"] = f"Approve {len(tools_info)} tool call(s)?"
            print(f"[HITL] Waiting for confirmation on {len(tools_info)} tool(s): {[t['tool_name'] for t in tools_info]}")

        elif hasattr(run_response, 'user_input_schema') and run_response.user_input_schema:
            self.pause_reason = "user_input"
            input_fields = []
            for field in run_response.user_input_schema:
                input_fields.append({
                    "name": field.name if hasattr(field, 'name') else None,
                    "description": field.description if hasattr(field, 'description') else None,
                    "type": field.type if hasattr(field, 'type') else None,
                    "required": field.required if hasattr(field, 'required') else True
                })
            pause_info["type"] = "user_input"
            pause_info["schema"] = input_fields
            pause_info["message"] = "Agent needs user input"
            print(f"[HITL] Waiting for user input: {len(input_fields)} field(s)")

        elif hasattr(run_response, 'tools_awaiting_external_execution') and run_response.tools_awaiting_external_execution:
            self.pause_reason = "external_tool"
            tools_info = []
            for tool in run_response.tools_awaiting_external_execution:
                tools_info.append({
                    "tool_name": tool.tool_name,
                    "tool_args": tool.tool_args if hasattr(tool, 'tool_args') else None
                })
            pause_info["type"] = "external_tool"
            pause_info["tools"] = tools_info
            pause_info["message"] = f"Execute {len(tools_info)} external tool(s)"
            print(f"[HITL] Waiting for external execution of {len(tools_info)} tool(s)")
        else:
            self.pause_reason = "unknown"
            pause_info["type"] = "unknown"
            pause_info["message"] = "Agent paused for unknown reason"
            print(f"[HITL] Agent paused but reason unclear")

        self.pause_info = pause_info

        # Send pause event to chat UI via Redis
        # IMPORTANT: Frontend expects run_id at top level, not in pause_data!
        send_chat_stream_event(
            flow_id=self.context.node_setup_version_id,
            run_id=self.context.run_id,
            node_id=self.id,
            event={
                "event": "AgentPaused",
                "run_id": pause_info.get("run_id"),  # ← Frontend expects this at top level
                "pause_type": pause_info["type"],
                "pause_message": pause_info["message"],
                "pause_data": {
                    k: v for k, v in pause_info.items()
                    if k not in ["paused", "run_id", "type", "message"]
                }
            },
            agent_role="single",
            is_member_agent=False
        )
        print(f"[HITL] Sent AgentPaused event to chat UI with run_id={pause_info.get('run_id')}")

        # DO NOT set true_path or false_path
        # This causes connections to become killers and flow stops
        # Flow will save state to DynamoDB and exit

    async def _handle_resume(self):
        """Resume paused agent execution with user input

        IMPORTANT: HITL in PolySynergy requires a DB (DynamoDBAgentStorage/LocalAgentStorage)!

        Why? In a normal Agno application, you can use:
            run_response = agent.run("...")
            if run_response.is_paused:
                # ... get user input
                agent.continue_run(run_response=run_response)  # <-- run_response stays in memory

        But in PolySynergy, the flow pauses and resumes via DynamoDB:
            1. Agent pauses → flow stops → state saved to DynamoDB → process exits
            2. User responds → NEW process starts → state loaded from DynamoDB
            3. The run_response object is GONE (cannot be serialized to DynamoDB)

        Solution: Use run_id instead of run_response:
            agent.continue_run(run_id="...", updated_tools=[...])

        This requires the agent to have a DB where it stores runs, so it can load
        the paused run by run_id when resuming.
        """
        print(f"[HITL] Resuming with pause reason: {self.pause_reason}")

        try:
            # CRITICAL: Rebuild agent instance before resuming
            # The agent instance doesn't exist after flow resumes from DynamoDB
            # Check if instance is actually an Agent object, not a serialized string
            if not isinstance(self.instance, Agent):
                print(f"[HITL] Agent instance invalid (type: {type(self.instance)}), rebuilding...")
                await self._create_agent()
                print(f"[HITL] Agent instance rebuilt successfully")

            # CHECK: Agent must have a DB connected for HITL to work
            if not self.instance.db:
                error_msg = (
                    "HITL (Human-in-the-Loop) requires a database to store and resume paused runs.\n\n"
                    "Why? PolySynergy flows pause and resume in separate processes:\n"
                    "  1. Agent pauses → flow stops → state saved to DynamoDB → process exits\n"
                    "  2. User responds → NEW process starts → state loaded from DynamoDB\n"
                    "  3. The run_response object is gone (cannot be serialized)\n\n"
                    "Solution: Connect a DB node to your agent:\n"
                    "  • LocalAgentStorage (for development/testing)\n"
                    "  • DynamoDBAgentStorage (for production)\n\n"
                    "Then rebuild your flow to regenerate the executable."
                )
                print(f"[HITL] ERROR: {error_msg}")
                self.false_path = error_msg
                self.true_path = False
                return

            # Handle different resume types based on pause reason
            if self.pause_reason == "confirmation":
                # User provided boolean confirmation
                confirmed = bool(self.user_input_data)
                print(f"[HITL] User confirmation: {confirmed}")

                # Agno agent maintains its own state and knows about the pending tools
                # We just need to set the confirmation status
                # The agent's run state includes the tools_requiring_confirmation

            elif self.pause_reason == "user_input":
                # User provided input data as dict
                if not isinstance(self.user_input_data, dict):
                    raise ValueError(f"Expected dict for user_input, got {type(self.user_input_data)}")
                print(f"[HITL] User input data: {self.user_input_data}")
                # Agno will handle user_input when we continue

            elif self.pause_reason == "external_tool":
                # User executed external tools and provided results
                if not isinstance(self.user_input_data, dict):
                    raise ValueError(f"Expected dict for external tool results, got {type(self.user_input_data)}")
                print(f"[HITL] External tool results provided")
                # Agno agent maintains state of tools awaiting external execution

            # Continue the agent run
            # The agent maintains its own run state via DB (DynamoDB/LocalAgentStorage)
            print(f"[HITL] Calling acontinue_run on agent instance...")

            # Agno v2: acontinue_run() can be called with run_id + updated_tools
            # This allows us to update the tool confirmation status
            #
            # When we pass run_id instead of run_response:
            # 1. Agent loads the paused run from its DB using the run_id
            # 2. If we pass updated_tools, those replace the tools in the loaded run
            # 3. Agent checks tool.confirmed flag to execute or reject tools

            # Get the paused run_id from pause_info
            paused_run_id = self.pause_info.get('run_id') if self.pause_info else None
            if not paused_run_id:
                raise ValueError("[HITL] No run_id found in pause_info - cannot resume")

            print(f"[HITL] Resuming run_id: {paused_run_id}")

            # For confirmation pause: we need to update tools with confirmed status
            # Get the session from the agent's DB to access the stored runs
            session = self.instance.db.get_session(
                session_id=self.instance.session_id,
                session_type=SessionType.AGENT,  # Single agent session
                user_id=self.instance.user_id
            )

            if not session or not session.runs:
                raise ValueError(f"[HITL] No session or runs found in DB for session_id={self.instance.session_id}")

            # Find the paused run in the session
            paused_run = next((r for r in session.runs if r.run_id == paused_run_id), None)
            if not paused_run:
                raise ValueError(f"[HITL] Paused run {paused_run_id} not found in session")

            print(f"[HITL] Found paused run with {len(paused_run.tools) if paused_run.tools else 0} tools")

            # Update tool confirmation status based on user input
            if self.pause_reason == "confirmation":
                confirmed = bool(self.user_input_data)
                print(f"[HITL] Setting tool confirmation to: {confirmed}")

                # Update all tools requiring confirmation
                if paused_run.tools:
                    for tool in paused_run.tools:
                        if hasattr(tool, 'requires_confirmation') and tool.requires_confirmation:
                            tool.confirmed = confirmed
                            print(f"[HITL] Updated tool '{tool.tool_name}': confirmed={confirmed}")

                # Save the updated session back to DB
                await self.instance.db.upsert_session(session)
                print(f"[HITL] Saved updated session to DB")

                # Now call acontinue_run with the updated run
                # Pass the updated tools to ensure confirmation status is used
                stream = self.instance.acontinue_run(
                    run_id=paused_run_id,
                    updated_tools=paused_run.tools,
                    show_full_reasoning=self.show_full_reasoning
                )
            else:
                # For other pause types, just call with run_id
                stream = self.instance.acontinue_run(
                    run_id=paused_run_id,
                    show_full_reasoning=self.show_full_reasoning
                )

            # Collect the response from the stream
            async def _collect_response(event_stream):
                final_response = None
                accumulated_content = []
                async for event in event_stream:
                    # Send chat events for resumed agent responses
                    event_type = getattr(event, 'event', None) or getattr(event, 'type', None)

                    if event_type in [
                        "RunContent",
                        "RunCompleted",
                        "RunStarted",
                        "ToolCallStarted",
                        "ToolCallCompleted",
                        "RunResponseContent",
                        "RunResponse",
                        "AgentRunResponseContent",
                        "ReasoningContent",  # Reasoning model thinking
                        "RunReasoningContent",  # Run-specific reasoning
                    ]:
                        node_id = self.id
                    else:
                        node_id = None

                    send_chat_stream_event(
                        flow_id=self.context.node_setup_version_id,
                        run_id=self.context.run_id,
                        node_id=node_id,
                        event=event,
                        agent_role="single",
                        is_member_agent=False
                    )

                    # Store FINAL response events (not intermediate content)
                    if event_type in ['RunResponse', 'AgentRunResponse', 'RunCompleted']:
                        if hasattr(event, 'run_response'):
                            final_response = event.run_response

                    # Accumulate streaming content as fallback
                    if hasattr(event, 'content') and event_type == 'RunContent':
                        accumulated_content.append(event.content)

                # Use final response or accumulated content
                if final_response is None and accumulated_content:
                    # Join all content pieces
                    combined_content = ''.join(str(c) for c in accumulated_content)
                    # Create a simple response object
                    class SimpleResponse:
                        def __init__(self, content):
                            self.content = content
                    final_response = SimpleResponse(combined_content)

                return final_response

            continued_response = await _collect_response(stream)

            print(f"[HITL] Resume completed, processing response")

            # Process the continued response
            if hasattr(continued_response, 'content'):
                content = continued_response.content
                if hasattr(content, 'model_dump_json'):
                    self.true_path = content.model_dump_json()
                    print(f"[HITL] Converted Pydantic model to JSON string: {self.true_path}")
                else:
                    self.true_path = content
            else:
                print(f"[HITL] Response has no content attribute, using str: {str(continued_response)}")
                self.true_path = str(continued_response)

            self.false_path = False

            # Clear pause state
            self._paused_run_response = None
            self.pause_reason = None
            self.pause_info = None

        except Exception as e:
            print(f"[HITL] Error during resume: {e}")
            import traceback
            traceback.print_exc()
            self.false_path = NodeError.format(e, True)
            self.true_path = False

    async def execute(self):
        # RESUME PATH: Check if we're resuming from a paused state
        # Note: _paused_run_response won't be available after DynamoDB restore (it's private)
        # But we can detect resume by checking if pause_reason is set AND user_input_data is provided
        if self.pause_reason and self.user_input_data is not None:
            print(f"[HITL] Resuming paused agent execution with user input")
            await self._handle_resume()
            return

        # if this is part of a team, or a sub for another agent
        # that team or agent will handle the execution
        if has_connected_agent_or_team(self):
            print("Agent is connected to team/agent - skipping execution")
            return

        # Get files and user context from prompt data BEFORE creating agent
        prompt_data = find_connected_prompt(self)
        print(f"DEBUG: prompt_data = {prompt_data}")
        agent_files = []
        final_user_context = None

        if prompt_data:
            agent_files = prompt_data.get('files', []) or []
            print(f"DEBUG: Got {len(agent_files)} files from prompt_data: {agent_files}")
            # Use user_context from prompt if available (Portal sets this)
            final_user_context = prompt_data.get('user_context')
            if final_user_context:
                print(f"DEBUG: Got user_context from prompt: {final_user_context}")
        else:
            agent_files = self.files or []
            print(f"DEBUG: Got {len(agent_files)} files from self.files: {agent_files}")

        # Fall back to manual user setting if no prompt context
        if not final_user_context and self.user:
            final_user_context = self.user
            print(f"DEBUG: Using manual user setting: {final_user_context}")

        # Enhance instructions with user context if available
        user_context = ""
        if final_user_context:
            user_name = final_user_context.get('name', 'Unknown User')
            user_email = final_user_context.get('email', '')
            user_role = final_user_context.get('role', '')

            user_context = f"\n\nYou are currently assisting: {user_name}"
            if user_email:
                user_context += f" ({user_email})"
            if user_role:
                user_context += f"\nTheir role: {user_role}"
            user_context += "\n"
            print(f"Enhanced agent instructions with user context for: {user_name}")

        # Enhance instructions with file context if files are available
        files_context = ""
        if agent_files:
            file_list = "\n".join([f"- {path}" for path in agent_files])
            files_context = f"""

Available files in this session:
{file_list}

IMPORTANT: When calling tools with file parameters, you MUST use the exact file paths listed above.
Do NOT invent or simplify filenames. Use the complete path as shown.
"""
            print(f"Enhanced agent instructions with {len(agent_files)} file paths")

        # Combine original instructions with enhancements
        if user_context or files_context:
            original_instructions = self.instructions or ""
            self.instructions = original_instructions + user_context + files_context

        await self._create_agent()

        if not self.prompt:
            print("No prompt provided")
            self.false_path = "No prompt provided for agent execution"
            return

        print(f"About to run agent with prompt: {self.prompt[:100]}...")
        if agent_files:
            print(f"Agent will process {len(agent_files)} files: {agent_files}")

        # Separate images from other files
        image_paths = []
        other_file_paths = []

        for file_path in agent_files:
            file_path_lower = file_path.lower()
            if any(file_path_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
                image_paths.append(file_path)
            else:
                other_file_paths.append(file_path)

        # Download images as base64 (OpenAI cannot access presigned S3 URLs)
        images = []
        if image_paths:
            print(f"DEBUG: Downloading {len(image_paths)} images as base64...")
            base64_images = download_images_as_base64(image_paths)
            for img_data in base64_images:
                print(f"DEBUG: Adding base64 image: {img_data['path']} ({img_data['mime_type']})")
                images.append(Image(url=img_data['base64']))
            print(f"DEBUG: Successfully converted {len(images)} images to base64")

        # Convert other files to presigned URLs
        agent_file_urls = generate_presigned_urls_for_files(other_file_paths) if other_file_paths else []
        print(f"DEBUG: Generated {len(agent_file_urls)} presigned URLs for non-image files")

        # Parse non-image files by type
        audio = []
        videos = []
        files = []

        for i, file_path in enumerate(other_file_paths):
            file_url = agent_file_urls[i] if i < len(agent_file_urls) else file_path
            file_path_lower = file_path.lower()

            if any(file_path_lower.endswith(ext) for ext in ['.mp3', '.wav', '.m4a', '.flac', '.aac']):
                audio.append(Audio(url=file_url))
            elif any(file_path_lower.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']):
                videos.append(Video(url=file_url))
            else:
                files.append(file_url)

        print(f"Files categorized - images: {len(images)}, audio: {len(audio)}, videos: {len(videos)}, files: {len(files)}")
        print(f"DEBUG: About to call arun with images={[str(img.url) for img in images]}")

        try:
            # Get stream setting from instance (set based on prompt node connection)
            should_stream = getattr(self.instance, 'stream', False)
            print(f"[Agent execute] Using stream={should_stream}")

            if should_stream:
                # In Agno v2, arun returns AsyncIterator when stream=True
                stream = self.instance.arun(
                    self.prompt,
                    images=images if images else None,
                    audio=audio if audio else None,
                    videos=videos if videos else None,
                    files=files if files else None,
                    show_full_reasoning=self.show_full_reasoning
                )
            else:
                # When stream=False, arun returns a coroutine that resolves to RunOutput
                response = await self.instance.arun(
                    self.prompt,
                    images=images if images else None,
                    audio=audio if audio else None,
                    videos=videos if videos else None,
                    files=files if files else None,
                    show_full_reasoning=self.show_full_reasoning
                )
                # Process non-streaming response
                if hasattr(response, 'content'):
                    content = response.content
                    if hasattr(content, 'model_dump_json'):
                        self.true_path = content.model_dump_json()
                        print(f"[Agent] Converted Pydantic model to JSON string: {self.true_path}")
                    else:
                        self.true_path = content
                else:
                    print(f"Response has no content attribute, using str: {str(response)}")
                    self.true_path = str(response)
                self.false_path = False
                return

            async def _collect_response(event_stream):
                final_response = None
                accumulated_content = []
                event_count = 0
                async for event in event_stream:
                    event_count += 1

                    # Send chat events for agent responses
                    # Check if event has the necessary attributes
                    event_type = getattr(event, 'event', None) or getattr(event, 'type', None)

                    # In Agno v2, the event types are different
                    if event_type in [
                        "RunContent",
                        "RunCompleted",
                        "RunStarted",
                        "ToolCallStarted",
                        "ToolCallCompleted",
                        "RunResponseContent",
                        "RunResponse",
                        "AgentRunResponseContent",
                        "ReasoningContent",  # Reasoning model thinking
                        "RunReasoningContent",  # Run-specific reasoning
                    ]:
                        node_id = self.id  # Use the agent node's own ID
                    else:
                        node_id = None

                    send_chat_stream_event(
                        flow_id=self.context.node_setup_version_id,
                        run_id=self.context.run_id,
                        node_id=node_id,
                        event=event,
                        agent_role="single",
                        is_member_agent=False
                    )

                    # Store FINAL response events (not intermediate content)
                    if event_type in ['RunResponse', 'AgentRunResponse', 'RunCompleted']:
                        if hasattr(event, 'run_response'):
                            final_response = event.run_response

                    # Accumulate streaming content as fallback
                    if hasattr(event, 'content') and event_type == 'RunContent':
                        accumulated_content.append(event.content)

                # Use final response or accumulated content
                if final_response is None and accumulated_content:
                    # Join all content pieces
                    combined_content = ''.join(str(c) for c in accumulated_content)
                    # Create a simple response object
                    class SimpleResponse:
                        def __init__(self, content):
                            self.content = content
                    final_response = SimpleResponse(combined_content)

                return final_response

            response = await _collect_response(stream)

            # PAUSE DETECTION: Check if agent paused for human input
            if hasattr(response, 'is_paused') and response.is_paused:
                await self._handle_pause(response)
                return  # Exit without setting paths → flow pauses

            # Extract content from the final response
            if hasattr(response, 'content'):
                content = response.content
                # If content is a Pydantic model, convert to JSON string
                if hasattr(content, 'model_dump_json'):
                    self.true_path = content.model_dump_json()
                    print(f"Converted Pydantic model to JSON string: {self.true_path}")
                else:
                    self.true_path = content
            else:
                print(f"Response has no content attribute, using str: {str(response)}")
                self.true_path = str(response)
        except Exception as e:
            self.false_path = NodeError.format(e, True)
            return
