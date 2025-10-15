import os

from agno.db import BaseDb
from agno.db.sqlite import SqliteDb
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode
from polysynergy_node_runner.utils.tenant_project_naming import get_prefixed_name


@node(
    name="SQLite Database",
    category="agno_db",
    icon="database.svg",
    has_enabled_switch=False,
    metadata={"deployment": "local"},
)
class SqliteDatabase(ServiceNode):
    """
    SQLite database for Agno v2 agents/teams/workflows.
    Provides persistent storage for sessions, memory, and metrics.

    Perfect for local development and testing.
    Uses separate environment variables to avoid conflicts with main API database.

    NOTE: This node uses SQLite with local file storage, making it
    unsuitable for serverless/cloud deployments. For production cloud
    environments, use DynamoDBDatabase or PostgreSQLDatabase.
    """

    db_file: str = NodeVariableSettings(
        label="Database File",
        dock=True,
        default="tmp/agno.db",
        info="Path to SQLite database file for storing agent data",
    )

    session_table: str | None = NodeVariableSettings(
        label="Session Table",
        dock=True,
        default="agno_sessions",
        info="Table name for storing agent/team/workflow sessions",
    )

    memory_table: str | None = NodeVariableSettings(
        label="Memory Table",
        dock=True,
        default="agno_memory",
        info="Table name for storing agent memories",
    )

    metrics_table: str | None = NodeVariableSettings(
        label="Metrics Table",
        dock=True,
        default="agno_metrics",
        info="Table name for storing metrics and analytics",
    )

    eval_table: str | None = NodeVariableSettings(
        label="Eval Table",
        dock=True,
        default="agno_evals",
        info="Table name for storing evaluation results",
    )

    knowledge_table: str | None = NodeVariableSettings(
        label="Knowledge Table",
        dock=True,
        default="agno_knowledge",
        info="Table name for storing knowledge base data",
    )

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
        info="SQLite database instance for Agno v2",
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
        """Create and return SQLite database instance."""

        kwargs = {}

        # Database file path
        kwargs["db_file"] = self.db_file

        # Table names with tenant-project prefix (standard names)
        if self.session_table:
            kwargs["session_table"] = get_prefixed_name(suffix=self.session_table)
        if self.memory_table:
            kwargs["memory_table"] = get_prefixed_name(suffix=self.memory_table)
        if self.metrics_table:
            kwargs["metrics_table"] = get_prefixed_name(suffix=self.metrics_table)
        if self.eval_table:
            kwargs["eval_table"] = get_prefixed_name(suffix=self.eval_table)
        if self.knowledge_table:
            kwargs["knowledge_table"] = get_prefixed_name(suffix=self.knowledge_table)

        # Create SQLite database instance
        self.db_instance = SqliteDb(**kwargs)

        return self.db_instance
