from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Team Settings Context",
    category="agno",
    icon="agno.svg",
)
class TeamSettingsContext(ServiceNode):

    context: dict | None = NodeVariableSettings(
        dock=True,
        info="Context settings for the team, such as team name, members, and other relevant information.",
    )

    add_context: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, adds the context to the team agent's system message.",
    )

    instance: "TeamSettingsContext" = NodeVariableSettings(
        label="Settings",
        group="messaging",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.team_settings_context.TeamSettingsContext"
    )

    def provide_instance(self) -> "TeamSettingsContext":
        return self