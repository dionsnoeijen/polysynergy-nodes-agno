from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Team Settings Team Tools",
    category="agno_settings",
    has_enabled_switch=False,
    icon="agno.svg",
)
class TeamSettingsTeamTools(ServiceNode):

    show_tool_calls: bool = NodeVariableSettings(
        dock=True,
        default=True,
        info="If True, the agent shows tool calls in the chat.",
    )

    tool_choice: dict | None = NodeVariableSettings(
        dock=dock_property(
            select_values={
                "none": "Don't use tools",
                "auto": "Let the model choose",
                "custom": "Use a specific tool (advanced)"
            },
            info="Controls which tool the model uses during execution."
        ),
        info=(
            "Controls which (if any) tool is called by the model. "
            "'none' disables tools, 'auto' lets the model choose, "
            "or provide a dict like {'type': 'function', 'function': {'name': 'my_function'}} "
            "to force a specific tool."
        )
    )

    tool_call_limit: int | None = NodeVariableSettings(
        dock=True,
        info="Maximum number of tool calls allowed in a single run. Set to None for no limit.",
    )

    tool_hooks: list | None = NodeVariableSettings(
        dock=True,
        info="A list of hooks to be called before and after the tool call.",
    )

    instance: "TeamSettingsTeamTools" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.team_settings_team_tools.TeamSettingsTeamTools"
    )

    def provide_instance(self) -> "TeamSettingsTeamTools":
        return self