from agno.agent import Agent
from agno.team import Team
from agno.tools.x import XTools
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="XTool",
    category="agno_native_tools",
    icon='agno.svg',
)
class XTool(ServiceNode):
    """
    Args:
        bearer_token Optional[str]: The bearer token for Twitter API.
        consumer_key Optional[str]: The consumer key for Twitter API.
        consumer_secret Optional[str]: The consumer secret for Twitter API.
        access_token Optional[str]: The access token for Twitter API.
        access_token_secret Optional[str]: The access token secret for Twitter API.
        include_post_metrics Optional[bool]: Whether to include post metrics in the search results.
        wait_on_rate_limit Optional[bool]: Whether to wait on rate limit.
    """

    agent_or_team: Agent | Team | None = NodeVariableSettings(
        has_in=True,
        info="Specify whether this tool is for an agent or a team.",
    )

    bearer_token: str | None = NodeVariableSettings(
        label="Bearer Token",
        info="The bearer token for Twitter API.",
        dock=True,
        has_in=True,
    )

    consumer_key: str | None = NodeVariableSettings(
        label="Consumer Key",
        info="The consumer key for Twitter API.",
        dock=True,
        has_in=True,
    )

    consumer_secret: str | None = NodeVariableSettings(
        label="Consumer Secret",
        info="The consumer secret for Twitter API.",
        dock=True,
        has_in=True,
    )

    access_token: str | None = NodeVariableSettings(
        label="Access Token",
        info="The access token for Twitter API.",
        dock=True,
        has_in=True,
    )

    access_token_secret: str | None = NodeVariableSettings(
        label="Access Token Secret",
        info="The access token secret for Twitter API.",
        dock=True,
        has_in=True,
    )

    include_post_metrics: bool = NodeVariableSettings(
        label="Include Post Metrics",
        info="Whether to include post metrics in the search results.",
        dock=True,
        default=False,
    )

    wait_on_rate_limit: bool = NodeVariableSettings(
        label="Wait on Rate Limit",
        info="Whether to wait on rate limit.",
        dock=True,
        default=False,
    )

    # Set by tool calling mechanism
    output: str | None = None

    async def provide_instance(self) -> XTools:
        return XTools(
            bearer_token=self.bearer_token,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            include_post_metrics=self.include_post_metrics,
            wait_on_rate_limit=self.wait_on_rate_limit
        )