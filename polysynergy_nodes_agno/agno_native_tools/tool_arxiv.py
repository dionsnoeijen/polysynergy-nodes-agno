from pathlib import Path

from agno.agent import Agent
from agno.team import Team
from agno.tools import Toolkit
from agno.tools.arxiv import ArxivTools
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Arxiv Tool",
    category="agno_native_tools",
    icon='agno.svg',
    has_enabled_switch=False,
)
class AxrivTool(ServiceNode):

    agent_or_team: Agent | Team | None = NodeVariableSettings(
        has_in=True,
        info="Specify whether this tool is for an agent or a team.",
    )

    search_arxiv: bool = NodeVariableSettings(
        label="Search Arxiv",
        default=True,
        dock=True,
        info="Enable searching Arxiv.",
    )

    read_arxiv_papers: bool = NodeVariableSettings(
        label="Read Arxiv Papers",
        default=True,
        dock=True,
        info="Enable reading Arxiv papers.",
    )

    download_dir: str | None = NodeVariableSettings(
        label="Download Directory",
        dock=True,
        info="Directory to store downloaded Arxiv papers.",
    )

    async def provide_instance(self) -> Toolkit:

        path = Path(__file__).parent.joinpath("tmp", "arxiv_pdfs__{session_id}")

        return ArxivTools(
            search_arxiv=self.search_arxiv,
            read_arxiv_papers=self.read_arxiv_papers,
            download_dir=path,
        )
