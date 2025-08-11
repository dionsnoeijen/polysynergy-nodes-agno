from agno.memory import AgentMemory
from agno.storage.sqlite import SqliteStorage
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Local Agent Memory",
    category="agno_memory", 
    icon="memory.svg",
    has_enabled_switch=False,
)
class LocalAgentMemory(ServiceNode):
    """
    Local SQLite-backed memory for Agno agents.
    Perfect for development and testing.
    """

    db_file: str = NodeVariableSettings(
        label="Database File",
        dock=True,
        default="tmp/agent_memory.db",
        info="Path to SQLite database file for storing agent memory",
    )

    # Memory settings
    create_user_memories: bool = NodeVariableSettings(
        label="Create User Memories",
        dock=True,
        default=True,
        info="Store memories for each user across sessions",
    )

    create_session_summary: bool = NodeVariableSettings(
        label="Create Session Summary",
        dock=True,
        default=True,
        info="Generate and store session summaries",
    )

    memory_instance: AgentMemory = NodeVariableSettings(
        label="Memory Instance",
        has_out=True,
        info="SQLite-backed agent memory instance for use in agents",
    )

    async def provide_instance(self) -> AgentMemory:
        """Create and return SQLite-backed AgentMemory instance."""
        
        # Create SQLite storage backend
        storage = SqliteStorage(
            db_file=self.db_file,
            table_name="agent_memory",
        )

        # Create AgentMemory with SQLite backend
        self.memory_instance = AgentMemory(
            db=storage,
            create_user_memories=self.create_user_memories,
            create_session_summary=self.create_session_summary,
        )

        return self.memory_instance

    async def execute(self):
        pass