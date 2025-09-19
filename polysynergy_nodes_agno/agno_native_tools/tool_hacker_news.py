from agno.agent import Agent
from agno.team import Team
from agno.tools import Toolkit
from agno.tools.hackernews import HackerNewsTools
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Hacker News Tool",
    category="agno_native_tools",
    icon='agno.svg',
    has_enabled_switch=False,
)
class HackerNewsTool(ServiceNode):
    """
    HackerNews is a tool for getting top stories from Hacker News.
    Args:
        get_top_stories (bool): Whether to get top stories from Hacker News.
        get_user_details (bool): Whether to get user details from Hacker News.
    """

    agent_or_team: Agent | Team | None = NodeVariableSettings(
        has_in=True,
        info="Specify whether this tool is for an agent or a team.",
    )

    get_top_stories: bool = NodeVariableSettings(
        label="Get Top Stories",
        default=True,
        dock=True,
        info="Enable getting top stories from Hacker News.",
    )

    get_user_details: bool = NodeVariableSettings(
        label="Get User Details",
        default=True,
        dock=True,
        info="Enable getting user details from Hacker News.",
    )

    # Set by tool calling mechanism
    output: str | None = None

    async def provide_instance(self) -> Toolkit:
        return HackerNewsTools(
            get_top_stories=self.get_top_stories,
            get_user_details=self.get_user_details,
        )