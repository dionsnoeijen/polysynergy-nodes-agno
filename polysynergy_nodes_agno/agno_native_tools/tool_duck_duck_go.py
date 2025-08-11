from agno.agent import Agent
from agno.team import Team
from agno.tools import Toolkit
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode
from agno.tools.duckduckgo import DuckDuckGoTools

@node(
    name="DuckDuckGo Tool",
    category="agno_native_tools",
    icon='agno.svg',
    has_enabled_switch=False,
)
class DuckDuckGoTool(ServiceNode):
    """
    DuckDuckGo is a toolkit for searching DuckDuckGo easily.
    Args:
        search (bool): Enable DuckDuckGo search function.
        news (bool): Enable DuckDuckGo news function.
        modifier (Optional[str]): A modifier to be used in the search request.
        fixed_max_results (Optional[int]): A fixed number of maximum results.
        headers (Optional[Any]): Headers to be used in the search request.
        proxy (Optional[str]): Proxy to be used in the search request.
        proxies (Optional[Any]): A list of proxies to be used in the search request.
        timeout (Optional[int]): The maximum number of seconds to wait for a response.`

    """

    agent_or_team: Agent | Team | None = NodeVariableSettings(
        has_in=True,
        info="Specify whether this tool is for an agent or a team.",
    )

    search: bool = NodeVariableSettings(
        label="Search",
        default=True,
        dock=True,
        info="Enable DuckDuckGo search function.",
    )

    news: bool = NodeVariableSettings(
        label="News",
        default=True,
        dock=True,
        info="Enable DuckDuckGo news function.",
    )

    modifier: str | None = NodeVariableSettings(
        label="Modifier",
        dock=True,
        info="A modifier to be used in the search request.",
    )

    fixed_max_results: int | None = NodeVariableSettings(
        label="Fixed Max Results",
        dock=True,
        info="A fixed number of maximum results.",
    )

    headers: dict | None = NodeVariableSettings(
        label="Headers",
        dock=True,
        info="Headers to be used in the search request.",
    )

    proxy: str | None = NodeVariableSettings(
        label="Proxy",
        dock=True,
        info="Proxy to be used in the search request.",
    )

    proxies: dict | None = NodeVariableSettings(
        label="Proxies",
        dock=True,
        info="A list of proxies to be used in the search request.",
    )

    timeout: int = NodeVariableSettings(
        label="Timeout",
        default=10,
        dock=True,
        info="The maximum number of seconds to wait for a response.",
    )

    verify_ssl: bool = NodeVariableSettings(
        label="Verify SSL",
        default=True,
        dock=True,
        info="Whether to verify SSL certificates.",
    )

    def provide_instance(self) -> Toolkit:
        return DuckDuckGoTools(
            search=self.search,
            news=self.news,
            modifier=self.modifier,
            fixed_max_results=self.fixed_max_results,
            headers=self.headers,
            proxy=self.proxy,
            proxies=self.proxies,
            timeout=self.timeout,
            verify_ssl=self.verify_ssl
        )
