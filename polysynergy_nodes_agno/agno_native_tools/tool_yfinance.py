from agno.agent import Agent
from agno.team import Team
from agno.tools import Toolkit
from agno.tools.yfinance import YFinanceTools
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="YFinance Tool",
    category="agno_native_tools",
    has_enabled_switch=False,
    icon="agno.svg",
)
class YFinanceTool(ServiceNode):
    """
    A tool for fetching stock data using the yfinance library.

    stock_price (bool): Whether to get the current stock price.
    company_info (bool): Whether to get company information.
    stock_fundamentals (bool): Whether to get stock fundamentals.
    income_statements (bool): Whether to get income statements.
    key_financial_ratios (bool): Whether to get key financial ratios.
    analyst_recommendations (bool): Whether to get analyst recommendations.
    company_news (bool): Whether to get company news.
    technical_indicators (bool): Whether to get technical indicators.
    historical_prices (bool): Whether to get historical prices.
    enable_all (bool): Whether to enable all tools.
    """

    agent_or_team: Agent | Team | None = NodeVariableSettings(
        has_in=True,
        info="Specify whether this tool is for an agent or a team.",
    )

    stock_price: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Get the current stock price.",
    )

    company_info: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Get company information.",
    )

    stock_fundamentals: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Get stock fundamentals.",
    )

    income_statements: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Get income statements.",
    )

    key_financial_ratios: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Get key financial ratios.",
    )

    analyst_recommendations: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Get analyst recommendations.",
    )

    company_news: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Get company news.",
    )

    technical_indicators: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Get technical indicators.",
    )

    historical_prices: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Get historical prices.",
    )

    enable_all: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Enable all tools.",
    )

    async def provide_instance(self) -> Toolkit:
        return YFinanceTools(
            stock_price=self.stock_price,
            company_info=self.company_info,
            stock_fundamentals=self.stock_fundamentals,
            income_statements=self.income_statements,
            key_financial_ratios=self.key_financial_ratios,
            analyst_recommendations=self.analyst_recommendations,
            company_news=self.company_news,
            technical_indicators=self.technical_indicators,
            historical_prices=self.historical_prices,
            enable_all=self.enable_all
        )
