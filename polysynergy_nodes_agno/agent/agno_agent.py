from datetime import datetime
from textwrap import dedent

from agno.agent import Agent
from agno.models.base import Model
from agno.tools.exa import ExaTools

from polysynergy_node_runner.setup_context.dock_property import dock_text_area
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_error import NodeError
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.path_settings import PathSettings

from polysynergy_nodes_agno.agent.utils.find_connected_model import find_connected_model


@node(
    name="Agno Agent",
    category="agno",
    icon="agno.svg",
)
class AgnoAgent(Node):

    model: Model | None = NodeVariableSettings(label="Model", has_in=True)

    description: str = NodeVariableSettings(
        label="Description",
        default="You are a helpful assistant.",
        has_in=True,
        dock=dock_text_area(rich=True),
        required=True
    )

    instructions: str = NodeVariableSettings(
        label="Instructions",
        default="You are a helpful assistant.",
        has_in=True,
        dock=dock_text_area(rich=True),
        required=True
    )

    expected_output: str = NodeVariableSettings(
        label="Expected Output",
        has_in=True,
        dock=dock_text_area(),
        required=True
    )

    markdown: bool = NodeVariableSettings(
        label="Markdown Output",
        default=True,
        info="If true, the output will be formatted in Markdown.",
        dock=True
    )

    show_tool_calls = NodeVariableSettings(
        label="Show Tool Calls",
        default=True,
        info="If true, the agent will display the tool calls made during execution.",
        dock=True
    )

    add_datetime_to_instructions: bool = NodeVariableSettings(
        label="Add DateTime to Instructions",
        default=True,
        info="If true, the current date and time will be added to the instructions.",
        dock=True
    )

    true_path: bool | str = PathSettings("Answer", info="This is the path for successful execution.")
    false_path: bool | str | dict = PathSettings("Error", info="This is the path for errors during execution.")

    def _setup(self):
        model = find_connected_model(self)
        if model is None:
            raise Exception("No model connected. Please connect a model to the node.")

        return model

    async def execute(self):

        model = self._setup()

        today = datetime.now().strftime("%Y-%m-%d")

        agent = Agent(
            model=model,
            tools=[ExaTools(start_published_date=today, type="keyword", api_key="c474c800-141a-4f6e-8110-38c203ff8044")],
            description=dedent(self.description),
            instructions=dedent(self.instructions),
            expected_output=dedent(self.expected_output),
            markdown=self.markdown,
            show_tool_calls=self.show_tool_calls,
            add_datetime_to_instructions=self.add_datetime_to_instructions,
        )

        try:
            response = await agent.arun("Research the latest developments in brain-computer interfaces")
            self.true_path = response.content
        except Exception as e:
            self.false_path = NodeError.format(e, True)
            return
