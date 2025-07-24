from polysynergy_node_runner.setup_context.dock_property import dock_text_area
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.path_settings import PathSettings


@node(
    name="Chat Play Agent",
    category="flow",
    has_enabled_switch=False,
    icon='play.svg'
)
class ChatPlayAgent(Node):

    title: str = NodeVariableSettings(label="Title", dock=True)

    info: str = NodeVariableSettings(label="Info", dock=dock_text_area(rich=True))

    true_path: bool = PathSettings(default=True, label="Prompt")

    def execute(self):
        pass