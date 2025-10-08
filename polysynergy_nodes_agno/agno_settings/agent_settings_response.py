from agno.models.base import Model
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode
from pydantic import BaseModel


@node(
    name="Agent Response Model Settings",
    category="agno_settings",
    has_enabled_switch=False,
    icon="agno.svg",
)
class AgentSettingsResponseModel(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'output_schema',
        'parser_model',
        'parser_model_prompt',
        'parse_response',
        'structured_outputs',
        'use_json_mode',
        'save_response_to_file',
    ]

    output_schema: BaseModel | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="Pydantic model defining the structured output schema"
    )

    response_model: BaseModel | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="Pydantic model used to parse the agent response."
    )

    parser_model: Model | None = NodeVariableSettings(
        dock=True,
        info="Optional model used to convert the output from the main model into the response_model.",
        has_in=True,
    )

    parser_model_prompt: str | None = NodeVariableSettings(
        dock=True,
        info="Prompt to send to the parser model for converting the raw output.",
        has_in=True,
    )

    parse_response: bool = NodeVariableSettings(
        dock=True,
        info="If True, parse the model output into the response_model.",
    )

    structured_outputs: bool | None = NodeVariableSettings(
        dock=True,
        info="Enable structured output parsing if supported by the model."
    )

    use_json_mode: bool = NodeVariableSettings(
        dock=True,
        info="If True, enforce JSON format for model output instead of relying on schema inference."
    )

    save_response_to_file: str | None = NodeVariableSettings(
        dock=True,
        info="If set, save the full response to this file path."
    )

    instance: "AgentSettingsResponseModel" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_response_model.AgentSettingsResponseModel"
    )

    async def provide_instance(self) -> "AgentSettingsResponseModel":
        # Check if output_schema is connected from another node
        schema_connections = [
            c for c in self.get_in_connections()
            if c.target_handle == "output_schema"
        ]

        print(f"DEBUG AgentSettingsResponseModel: Found {len(schema_connections)} output_schema connections")

        if schema_connections:
            conn = schema_connections[0]
            source_node = self.state.get_node_by_id(conn.source_node_id)
            print(f"DEBUG AgentSettingsResponseModel: Source node = {source_node.handle if source_node else None}")

            if source_node and hasattr(source_node, "provide_instance"):
                # Get the model from the connected node
                model = await source_node.provide_instance()
                self.output_schema = model
                print(f"DEBUG AgentSettingsResponseModel: Loaded output_schema from connected node: {model}")

        print(f"DEBUG AgentSettingsResponseModel: Final output_schema = {self.output_schema}")
        return self
