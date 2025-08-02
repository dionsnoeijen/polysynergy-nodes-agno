from polysynergy_node_runner.setup_context.dock_property import dock_text_area
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings


@node(
    name="Prompt",
    category="flow",
    has_enabled_switch=False,
    icon='play.svg'
)
class PromptNode(Node):

    name: str = NodeVariableSettings(
        label="Name",
        dock=True,
        info="Name for this prompt node."
    )

    prompt: str = NodeVariableSettings(
        label="Prompt",
        dock=dock_text_area(rich=True),
        has_in=True,
        has_out=True,
        info="The prompt text to be used by agents or teams."
    )

    def execute(self):
        pass