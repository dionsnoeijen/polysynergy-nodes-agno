import os

from agno.db import BaseDb
from agno.db.postgres import PostgresDb
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode
from polysynergy_node_runner.utils.tenant_project_naming import get_prefixed_name


@node(
    name="PostgreSQL Database",
    category="agno_db",
    icon="database.svg",
    has_enabled_switch=False,
)
class PostgreSQLDatabase(ServiceNode):
    """
    PostgreSQL database for Agno v2 agents/teams/workflows.
    Provides persistent storage for sessions, memory, and metrics.

    Ideal for large team sessions that exceed DynamoDB's 400KB item limit.
    Uses separate environment variables to avoid conflicts with main API database.
    """

    # Agno session behavior settings
    add_history_to_context: bool = NodeVariableSettings(
        dock=True,
        default=True,
        info="If True, adds messages from chat history to the list sent to the model for better context.",
    )

    num_history_runs: int = NodeVariableSettings(
        dock=True,
        default=5,
        info="Number of previous runs to include in the messages for contextual continuity.",
    )

    read_chat_history: bool = NodeVariableSettings(
        dock=True,
        default=False,
        info="Adds a tool that allows the model to read the chat history.",
    )

    enable_user_memories: bool = NodeVariableSettings(
        label="Enable User Memories",
        dock=True,
        default=True,
        info="Enable storing and retrieving user-specific memories in the database.",
    )

    db_instance: BaseDb | None = NodeVariableSettings(
        label="Database Instance",
        has_out=True,
        info="PostgreSQL database instance for Agno v2",
    )

    def provide_db_settings(self) -> dict:
        """Provide database-related settings for the agent (runtime context)."""
        return {
            "add_history_to_context": self.add_history_to_context,
            "num_history_runs": self.num_history_runs,
            "read_chat_history": self.read_chat_history,
            "enable_user_memories": self.enable_user_memories,
        }

    async def provide_instance(self) -> BaseDb:
        """Create and return PostgreSQL database instance."""
        
        kwargs = {}
        
        # Build connection URL from environment variables only
        host = os.environ.get("AGNO_DB_HOST", "localhost")
        port = int(os.environ.get("AGNO_DB_PORT", "5433"))
        name = os.environ.get("AGNO_DB_NAME", "agno_session_db")
        user = os.environ.get("AGNO_DB_USER", "agno_user")
        password = os.environ.get("AGNO_DB_PASSWORD", "agno_password")
        
        db_url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"
        kwargs["db_url"] = db_url
        
        # Table names with tenant-project prefix (standard names, not configurable)
        kwargs["session_table"] = get_prefixed_name(suffix="agno_sessions")
        kwargs["memory_table"] = get_prefixed_name(suffix="agno_memory")
        kwargs["metrics_table"] = get_prefixed_name(suffix="agno_metrics")
        kwargs["eval_table"] = get_prefixed_name(suffix="agno_evals")
        kwargs["knowledge_table"] = get_prefixed_name(suffix="agno_knowledge")

        # Create PostgreSQL database instance
        self.db_instance = PostgresDb(**kwargs)

        return self.db_instance