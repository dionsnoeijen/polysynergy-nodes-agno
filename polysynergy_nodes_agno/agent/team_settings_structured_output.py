from agno.models.base import Model
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode
from pydantic import BaseModel


@node(
    name="Team Settings Structured Output",
    category="agent",
    has_enabled_switch=False,
    icon='team_settings.svg',
)
class TeamSettingsStructuredOutput(ServiceNode):

    settings: list = [
        'response_model',
        'parser_model',
        'parser_model_prompt',
        'use_json_model',
        'parse_response',
    ]

    response_model: BaseModel = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="The model used to generate structured outputs for team interactions.",
        type="pydantic.BaseModel"
    )

    parser_model: Model = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="The model used to parse structured outputs from team interactions.",
        type="agno.models.base.Model"
    )

    parser_model_prompt: str | None = NodeVariableSettings(
        dock=True,
        has_in=True,
        info="The prompt used by the parser model to parse structured outputs.",
    )

    use_json_model: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the structured output is formatted as JSON.",
    )

    parse_response: bool = NodeVariableSettings(
        dock=True,
        default=True,
        info="If True, the response is parsed into the structured output model.",
    )

    instance: "TeamSettingsStructuredOutput" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.team_settings_structured_output.TeamSettingsStructuredOutput"
    )

    def provide_instance(self) -> "TeamSettingsStructuredOutput":
        return self