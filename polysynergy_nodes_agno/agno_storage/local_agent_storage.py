from agno.storage.base import Storage
from agno.storage.sqlite import SqliteStorage
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Local Agent Storage",
    category="agno_storage", 
    icon="storage.svg",
    has_enabled_switch=False,
)
class LocalAgentStorage(ServiceNode):
    """
    Local SQLite-backed storage for Agno agents.
    Stores conversation history and session data.
    Perfect for development and testing.
    """

    db_file: str = NodeVariableSettings(
        label="Database File",
        dock=True,
        default="tmp/agent_storage.db",
        info="Path to SQLite database file for storing conversation history",
    )
    
    table_name: str = NodeVariableSettings(
        label="Table Name",
        dock=True,
        default="agent_sessions",
        info="Name of the table for storing agent sessions",
    )

    # History Settings - moved from AgentSettingsHistory
    add_history_to_messages: bool = NodeVariableSettings(
        dock=True,
        default=True,
        info="If True, adds messages from chat history to the list sent to the model for better context.",
    )

    num_history_runs: int = NodeVariableSettings(
        dock=True,
        default=3,
        info="Number of previous runs to include in the messages for contextual continuity.",
    )

    read_chat_history: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Adds a tool that allows the model to read the chat history.",
    )

    storage_instance: Storage | None = NodeVariableSettings(
        label="Storage Instance",
        has_out=True,
        info="SQLite-backed storage instance for conversation history",
    )

    async def provide_instance(self) -> Storage:
        """Create and return SQLite-backed Storage instance."""
        
        # Create SQLite storage for conversation history
        self.storage_instance = SqliteStorage(
            table_name=self.table_name,
            db_file=self.db_file,
        )
        
        return self.storage_instance

    def provide_storage_settings(self) -> dict:
        """Provide storage-related settings for the agent."""
        return {
            'add_history_to_messages': self.add_history_to_messages,
            'num_history_runs': self.num_history_runs,
            'read_chat_history': self.read_chat_history,
        }

    async def execute(self):
        pass