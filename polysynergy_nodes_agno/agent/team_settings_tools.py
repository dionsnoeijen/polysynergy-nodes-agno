from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Team Tools Settings",
    category="agno",
    has_enabled_switch=False,
    icon="agno.svg",
)
class TeamSettingsTools(ServiceNode):
    enable_agentic_context: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the agent automatically manages context for the current session.",
    )

    share_member_interactions: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the agent shares interactions with team members.",
    )

    get_member_information_tool: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the agent uses a tool to get information about team members.",
    )

    search_knowledge: bool = NodeVariableSettings(
        dock=True,
        default=True,
        info="Add a tool to search the knowledge base (aka Agentic RAG) Only added if knowledge is provided.",
    )

    read_team_history: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="If True, the agent reads the team history to provide context for interactions.",
    )

    instance: "TeamSettingsTools" = NodeVariableSettings(
        label="Settings",
        group="messaging",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.team_settings_tools.TeamSettingsTools"
    )

    def provide_instance(self) -> "TeamSettingsTools":
        return self