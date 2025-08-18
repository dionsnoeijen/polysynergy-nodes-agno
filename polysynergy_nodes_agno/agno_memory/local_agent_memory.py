from agno.memory.v2.memory import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
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
    Stores extracted memories from conversations.
    Perfect for development and testing.
    """

    db_file: str = NodeVariableSettings(
        label="Database File",
        dock=True,
        default="tmp/agent_memory.db",
        info="Path to SQLite database file for storing extracted memories",
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

    memory_instance: Memory | None = NodeVariableSettings(
        label="Memory Instance",
        has_out=True,
        info="SQLite-backed memory instance for use in agents",
    )

    async def provide_instance(self) -> Memory:
        """Create and return SQLite-backed Memory instance."""
        
        # Create SQLite memory database
        memory_db = SqliteMemoryDb(
            table_name="memories",
            db_file=self.db_file,
        )

        # Create Memory with SQLite backend (v2 API)
        self.memory_instance = Memory(db=memory_db)

        return self.memory_instance
    
    def provide_memory_settings(self) -> dict:
        return {
            'enable_agentic_memory': True,  # Enable memory when memory node is connected
            'enable_user_memories': self.create_user_memories,
            'enable_session_summaries': self.create_session_summary,
        }

    async def execute(self):
        pass