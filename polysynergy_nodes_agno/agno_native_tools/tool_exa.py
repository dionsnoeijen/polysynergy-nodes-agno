from agno.agent import Agent
from agno.team import Team
from agno.tools import Toolkit
from agno.tools.exa import ExaTools
from polysynergy_node_runner.setup_context.dock_property import dock_property, dock_select_values
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Exa Tool",
    category="search",
    icon="agno.svg",
)
class ExaTool(ServiceNode):

    """
    Args:
        text (bool): Retrieve text content from results. Default is True.
        text_length_limit (int): Max length of text content per result. Default is 1000.
        highlights (bool): Include highlighted snippets. Default is True.
        answer (bool): Enable answer generation. Default is True.
        research (bool): Enable research tool functionality. Default is True.
        api_key (Optional[str]): Exa API key. Retrieved from `EXA_API_KEY` env variable if not provided.
        num_results (Optional[int]): Default number of search results. Overrides individual searches if set.
        start_crawl_date (Optional[str]): Include results crawled on/after this date (`YYYY-MM-DD`).
        end_crawl_date (Optional[str]): Include results crawled on/before this date (`YYYY-MM-DD`).
        start_published_date (Optional[str]): Include results published on/after this date (`YYYY-MM-DD`).
        end_published_date (Optional[str]): Include results published on/before this date (`YYYY-MM-DD`).
        use_autoprompt (Optional[bool]): Enable autoprompt features in queries.
        type (Optional[str]): Specify content type (e.g., article, blog, video).
        category (Optional[str]): Filter results by category. Options are "company", "research paper", "news", "pdf", "github", "tweet", "personal site", "linkedin profile", "financial report".
        include_domains (Optional[List[str]]): Restrict results to these domains.
        exclude_domains (Optional[List[str]]): Exclude results from these domains.
        show_results (bool): Log search results for debugging. Default is False.
        model (Optional[str]): The search model to use. Options are 'exa' or 'exa-pro'.
        timeout (int): Maximum time in seconds to wait for API responses. Default is 30 seconds.
    """

    agent_or_team: Agent | Team | None = NodeVariableSettings(
        has_in=True,
        info="Specify whether this tool is for an agent or a team.",
    )

    text: bool = NodeVariableSettings(
        label="Text",
        default=True,
        dock=True,
        info="Retrieve text content from results.",
    )

    text_length_limit: int = NodeVariableSettings(
        label="Text Length Limit",
        default=1000,
        dock=True,
        info="Maximum length of text content per result.",
    )

    highlights: bool = NodeVariableSettings(
        label="Highlights",
        dock=True,
        default=True,
        info="Include highlighted snippets in results.",
    )

    answer: bool = NodeVariableSettings(
        label="Answer",
        default=True,
        dock=True,
        info="Enable answer generation for queries.",
    )

    research: bool = NodeVariableSettings(
        label="Research",
        default=True,
        dock=True,
        info="Enable research tool functionality.",
    )

    api_key: str | None = NodeVariableSettings(
        label="API Key",
        dock=True,
        info="Exa API key. Retrieved from `EXA_API_KEY` env variable if not provided.",
    )

    num_results: int | None = NodeVariableSettings(
        label="Number of Results",
        dock=True,
        info="Default number of search results. Overrides individual searches if set.",
    )

    start_crawl_date: str | None = NodeVariableSettings(
        label="Start Crawl Date",
        dock=True,
        info="Include results crawled on/after this date (`YYYY-MM-DD`).",
    )

    end_crawl_date: str | None = NodeVariableSettings(
        label="End Crawl Date",
        dock=True,
        info="Include results crawled on/before this date (`YYYY-MM-DD`).",
    )

    start_published_date: str | None = NodeVariableSettings(
        label="Start Published Date",
        dock=True,
        info="Include results published on/after this date (`YYYY-MM-DD`).",
    )

    end_published_date: str | None = NodeVariableSettings(
        label="End Published Date",
        dock=True,
        info="Include results published on/before this date (`YYYY-MM-DD`).",
    )

    use_autoprompt: bool | None = NodeVariableSettings(
        label="Use Autoprompt",
        default=False,
        info="Enable autoprompt features in queries.",
    )

    type: str | None = NodeVariableSettings(
        label="Type",
        dock=True,
        info="Specify content type (e.g., article, blog, video).",
    )

    category: str | None = NodeVariableSettings(
        label="Category",
        dock=dock_select_values(select_values={
            "company": "Company",
            "research paper": "Research Paper",
            "news": "News",
            "pdf": "PDF",
            "github": "GitHub",
            "tweet": "Tweet",
            "personal site": "Personal Site",
            "linkedin profile": "LinkedIn Profile",
            "financial report": "Financial Report"
        }),
        info="Filter results by category. Options are 'company', 'research paper', 'news', 'pdf', 'github', 'tweet', 'personal site', 'linkedin profile', 'financial report'.",
    )

    include_domains: list | None = NodeVariableSettings(
        label="Include Domains",
        dock=True,
        info="Restrict results to these domains.",
    )

    exclude_domains: list | None = NodeVariableSettings(
        label="Exclude Domains",
        dock=True,
        info="Exclude results from these domains.",
    )

    show_results: bool = NodeVariableSettings(
        label="Show Results",
        default=False,
        dock=True,
        info="Log search results for debugging.",
    )

    model: str | None = NodeVariableSettings(
        label="Model",
        dock=dock_property(select_values={"exa": "exa", "exa-pro": "exa-pro"}),
        info="The search model to use. Options are 'exa' or 'exa-pro'.",
    )

    timeout: int = NodeVariableSettings(
        label="Timeout",
        default=30,
        dock=True,
        info="Maximum time in seconds to wait for API responses.",
    )

    def provide_instance(self) -> Toolkit:
        return ExaTools(
            text=self.text,
            text_length_limit=self.text_length_limit,
            highlights=self.highlights,
            answer=self.answer,
            research=self.research,
            api_key=self.api_key,
            num_results=self.num_results,
            start_crawl_date=self.start_crawl_date,
            end_crawl_date=self.end_crawl_date,
            start_published_date=self.start_published_date,
            end_published_date=self.end_published_date,
            use_autoprompt=self.use_autoprompt,
            type=self.type,
            category=self.category,
            include_domains=self.include_domains,
            exclude_domains=self.exclude_domains,
            show_results=self.show_results,
            model=self.model,
            timeout=self.timeout
        )
