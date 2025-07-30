from agno.agent import Agent
from agno.team import Team
from agno.tools import Toolkit
from agno.tools.googlesearch import GoogleSearchTools
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Google Search Tool",
    category="agno",
    icon='agno.svg',
)
class GoogleSearchTool(ServiceNode):
    """
    GoogleSearch is a Python library for searching Google easily.
    It uses requests and BeautifulSoup4 to scrape Google.

    Args:
        fixed_max_results (Optional[int]): A fixed number of maximum results.
        fixed_language (Optional[str]): Language of the search results.
        headers (Optional[Any]): Custom headers for the request.
        proxy (Optional[str]): Proxy settings for the request.
        timeout (Optional[int]): Timeout for the request, default is 10 seconds.
        cache_results (bool): Enable caching of search results.
        cache_ttl (int): Time-to-live for cached results in seconds.
        cache_dir (Optional[str]): Directory to store cache files.
    """

    agent_or_team: Agent | Team | None = NodeVariableSettings(
        has_in=True,
        info="Specify whether this tool is for an agent or a team.",
    )

    fixed_max_results: int | None = NodeVariableSettings(
        label="Fixed Max Results",
        dock=True,
        info="A fixed number of maximum results.",
    )

    fixed_language: str | None = NodeVariableSettings(
        label="Fixed Language",
        dock=True,
        info="Language of the search results.",
    )

    headers: dict | None = NodeVariableSettings(
        label="Headers",
        dock=True,
        info="Custom headers for the request.",
    )

    proxy: str | None = NodeVariableSettings(
        label="Proxy",
        dock=True,
        info="Proxy settings for the request.",
    )

    timeout: int = NodeVariableSettings(
        label="Timeout",
        default=10,
        dock=True,
        info="Timeout for the request in seconds.",
    )

    cache_results: bool = NodeVariableSettings(
        label="Cache Results",
        default=False,
        dock=True,
        info="Enable caching of search results.",
    )

    cache_ttl: int = NodeVariableSettings(
        label="Cache TTL",
        default=3600,
        dock=True,
        info="Time-to-live for cached results in seconds.",
    )

    cache_dir: str | None = NodeVariableSettings(
        label="Cache Directory",
        dock=True,
        info="Directory to store cache files.",
    )

    def provide_instance(self) -> Toolkit:
        return GoogleSearchTools(
            fixed_max_results=self.fixed_max_results,
            fixed_language=self.fixed_language,
            headers=self.headers,
            proxy=self.proxy,
            timeout=self.timeout,
            cache_results=self.cache_results,
            cache_ttl=self.cache_ttl,
            cache_dir=self.cache_dir,
        )
