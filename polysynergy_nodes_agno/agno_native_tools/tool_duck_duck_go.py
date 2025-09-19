from typing import Optional
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
    icon="agno.svg",
    has_enabled_switch=False,
)
class DuckDuckGoTool(ServiceNode):
    """
    DuckDuckGo toolkit (DDGS backend).

    Args (ondersteund door huidige DuckDuckGoTools):
        search (bool): Exposeeer algemene search.
        news (bool): Exposeeer nieuwszoekfunctie.
        modifier (str|None): Voorvoegsel voor query (bv. 'site:example.com').
        fixed_max_results (int|None): Forceer max results.
        proxy (str|None): Door aan DDGS(proxy=...).
        timeout (int|None): Door aan DDGS(timeout=...).
        verify_ssl (bool): Door aan DDGS(verify=...).

    Let op: 'headers' en 'proxies' worden niet meer ondersteund door de toolkit.
    """

    # Koppeling vanuit agent/team (finder zoekt naar target_handle == "agent_or_team")
    agent_or_team: Agent | Team | None = NodeVariableSettings(
        has_in=True,
        info="Specify whether this tool is for an agent or a team.",
    )

    # Instelbare opties (sluiten aan op DuckDuckGoTools __init__)
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

    modifier: Optional[str] = NodeVariableSettings(
        label="Modifier",
        dock=True,
        info="A modifier to be used in the search request (e.g., 'site:example.com').",
    )

    fixed_max_results: Optional[int] = NodeVariableSettings(
        label="Fixed Max Results",
        dock=True,
        info="Force a maximum number of results (overrides runtime max_results).",
    )

    proxy: Optional[str] = NodeVariableSettings(
        label="Proxy",
        dock=True,
        info="Proxy passed to DDGS.",
    )

    timeout: int = NodeVariableSettings(
        label="Timeout (seconds)",
        default=10,
        dock=True,
        info="Maximum seconds to wait for a response.",
    )

    verify_ssl: bool = NodeVariableSettings(
        label="Verify SSL",
        default=True,
        dock=True,
        info="Verify SSL certificates (maps to DDGS(verify=...)).",
    )

    # Set by tool calling mechanism
    output: str | None = None

    async def provide_instance(self) -> Toolkit:
        # Direct conform de huidige DuckDuckGoTools signature
        return DuckDuckGoTools(
            enable_search=self.search,
            enable_news=self.news,
            modifier=self.modifier,
            fixed_max_results=self.fixed_max_results,
            proxy=self.proxy,
            timeout=self.timeout,
            verify_ssl=self.verify_ssl,
        )