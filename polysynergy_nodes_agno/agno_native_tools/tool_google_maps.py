from agno.agent import Agent
from agno.team import Team
from agno.tools import Toolkit
from agno.tools.google_maps import GoogleMapTools
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Google Maps Tool",
    category="agno_native_tools",
    icon='agno.svg',
)
class GoogleMapsTool(ServiceNode):
    """Google Maps tool for finding places and businesses by location."""

    agent_or_team: Agent | Team | None = NodeVariableSettings(
        has_in=True,
        info="Specify whether this tool is for an agent or a team.",
    )

    api_key: str | None = NodeVariableSettings(
        label="API Key",
        dock=True,
        info="Google Maps API key (required). Get one from Google Cloud Console.",
    )

    # Set by tool calling mechanism
    output: str | None = None

    async def provide_instance(self) -> Toolkit:
        return GoogleMapTools(
            key=self.api_key,
        )
