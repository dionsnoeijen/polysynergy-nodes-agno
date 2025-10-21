from polysynergy_node_runner.setup_context.dock_property import dock_text_area
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.path_settings import PathSettings

from polysynergy_nodes_agno.agno_agent.utils.send_chat_stream_event import send_chat_stream_event


@node(
    name="Chat HTML",
    category="chat_content",
    icon="html.svg",
)
class ChatHTML(Node):
    """
    Send HTML content to the chat interface for rich visual display.

    This node allows you to display rich formatted content in the chat, including:
    - Images (<img> tags)
    - Tables
    - Styled cards
    - Lists
    - Custom HTML layouts

    The HTML will be sanitized on the frontend for security.
    """

    html_content: str = NodeVariableSettings(
        label="HTML Content",
        dock=dock_text_area(rich=True),
        has_in=True,
        info="HTML content to display in chat (will be sanitized on frontend for security)"
    )

    # OUTPUT
    true_path: bool | str = PathSettings("Success", info="Executed successfully")
    false_path: bool | str = PathSettings("Error", info="Error during execution")

    async def execute(self):
        """Send HTML content to chat via WebSocket event"""

        if not self.html_content:
            self.false_path = "No HTML content provided"
            self.true_path = False
            return

        try:
            # Send HTML content event to chat UI via Redis
            send_chat_stream_event(
                flow_id=self.context.node_setup_version_id,
                run_id=self.context.run_id,
                node_id=self.id,
                event={
                    "event": "ChatHTML",
                    "html_content": self.html_content,
                },
                agent_role="single",
                is_member_agent=False
            )

            print(f"[ChatHTML] Sent HTML content to chat ({len(self.html_content)} chars)")
            self.true_path = True
            self.false_path = False

        except Exception as e:
            print(f"[ChatHTML] Error sending HTML content: {e}")
            self.false_path = str(e)
            self.true_path = False
