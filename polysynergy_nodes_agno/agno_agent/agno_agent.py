import uuid
from textwrap import dedent
from typing import Literal, cast

from agno.agent import Agent
from agno.db import BaseDb
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
from polysynergy_nodes_agno.agno_agent.utils.has_connected_agent_or_team import has_connected_agent_or_team
from polysynergy_nodes_agno.agno_agent.utils.find_connected_prompt import find_connected_prompt
from polysynergy_nodes_agno.agno_agent.utils.send_chat_stream_event import send_chat_stream_event
from polysynergy_nodes_agno.agno_agent.utils.create_tool_hook import create_tool_hook
from polysynergy_nodes_agno.agno_agent.utils.build_tool_mapping import build_tool_mapping
from polysynergy_nodes_agno.agno_agent.utils.generate_presigned_urls import generate_presigned_urls_for_files


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
                events_to_skip=[],
                stream=True,
                **props
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise

    async def provide_instance(self) -> Agent:
        await self._create_agent()
        return self.instance

    async def execute(self):

        # if this is part of a team, or a sub for another agent
        # that team or agent will handle the execution
        if has_connected_agent_or_team(self):
            print("Agent is connected to team/agent - skipping execution")
            return

        # Get files from prompt data BEFORE creating agent
        prompt_data = find_connected_prompt(self)
        print(f"DEBUG: prompt_data = {prompt_data}")
        agent_files = []
        if prompt_data:
            agent_files = prompt_data.get('files', []) or []
            print(f"DEBUG: Got {len(agent_files)} files from prompt_data: {agent_files}")
        else:
            agent_files = self.files or []
            print(f"DEBUG: Got {len(agent_files)} files from self.files: {agent_files}")

        # Enhance instructions with file context if files are available
        if agent_files:
            file_list = "\n".join([f"- {path}" for path in agent_files])
            files_context = f"""

Available files in this session:
{file_list}

IMPORTANT: When calling tools with file parameters, you MUST use the exact file paths listed above.
Do NOT invent or simplify filenames. Use the complete path as shown.
"""
            original_instructions = self.instructions or ""
            self.instructions = original_instructions + files_context
            print(f"Enhanced agent instructions with {len(agent_files)} file paths")

        await self._create_agent()

        if not self.prompt:
            print("No prompt provided")
            self.false_path = "No prompt provided for agent execution"
            return

        print(f"About to run agent with prompt: {self.prompt[:100]}...")
        if agent_files:
            print(f"Agent will process {len(agent_files)} files: {agent_files}")

        # Convert relative file paths to presigned URLs
        agent_file_urls = generate_presigned_urls_for_files(agent_files) if agent_files else []
        print(f"DEBUG: Generated {len(agent_file_urls)} presigned URLs: {agent_file_urls}")

        # Parse files by type for native agno v2 support
        images = []
        audio = []
        videos = []
        files = []

        for i, file_path in enumerate(agent_files):
            file_url = agent_file_urls[i] if i < len(agent_file_urls) else file_path
            file_path_lower = file_path.lower()

            if any(file_path_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
                print(f"DEBUG: Adding image {i}: path={file_path}, url={file_url}")
                images.append(Image(url=file_url))
            elif any(file_path_lower.endswith(ext) for ext in ['.mp3', '.wav', '.m4a', '.flac', '.aac']):
                audio.append(Audio(url=file_url))
            elif any(file_path_lower.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']):
                videos.append(Video(url=file_url))
            else:
                files.append(file_url)

        print(f"Files categorized - images: {len(images)}, audio: {len(audio)}, videos: {len(videos)}, files: {len(files)}")
        print(f"DEBUG: About to call arun with images={[str(img.url) for img in images]}")

        try:
            # In Agno v2, arun supports native file parameters
            stream = self.instance.arun(
                self.prompt,
                stream=True,
                stream_intermediate_steps=True,
                images=images if images else None,
                audio=audio if audio else None,
                videos=videos if videos else None,
                files=files if files else None
            )

            async def _collect_response(event_stream):
                final_response = None
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
                        "AgentRunResponseContent"
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
                    
                    # Store the final response
                    if hasattr(event, 'run_response'):
                        final_response = event.run_response
                    elif hasattr(event, 'content'):
                        final_response = event
                        
                return final_response

            response = await _collect_response(stream)

            # Extract content from the final response
            if hasattr(response, 'content'):
                content = response.content
                # If content is a Pydantic model, convert to dict/JSON
                if hasattr(content, 'model_dump'):
                    self.true_path = content.model_dump()
                    print(f"Converted Pydantic model to dict: {self.true_path}")
                else:
                    self.true_path = content
            else:
                print(f"Response has no content attribute, using str: {str(response)}")
                self.true_path = str(response)
        except Exception as e:
            self.false_path = NodeError.format(e, True)
            return
