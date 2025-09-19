import os

from agno.db import BaseDb
from agno.db.dynamo import DynamoDb
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode
from polysynergy_node_runner.utils.tenant_project_naming import get_prefixed_name

# RunSeparatedDbWrapper removed - DynamoDB 400KB limit makes it useless


@node(
    name="DynamoDB Database",
    category="agno_db",
    icon="database.svg",
    has_enabled_switch=False,
)
class DynamoDbDatabase(ServiceNode):
    """
    DynamoDB database for Agno v2 agents/teams/workflows.
    Provides persistent storage for sessions, memory, and metrics.
    """

    region_name: str = NodeVariableSettings(
        label="AWS Region",
        dock=True,
        default="eu-central-1",
        info="AWS region where DynamoDB tables are located",
    )

    # @todo: See how to integrate custom dynamodb endpoint
    aws_access_key_id: str | None = NodeVariableSettings(
        label="AWS Access Key ID",
        dock=True,
        info="AWS access key ID (leave empty to use default credentials)",
    )

    aws_secret_access_key: str | None = NodeVariableSettings(
        label="AWS Secret Access Key",
        dock=True,
        info="AWS secret access key (leave empty to use default credentials)",
    )

    endpoint_url: str | None = NodeVariableSettings(
        label="Endpoint URL",
        dock=True,
        info="Custom DynamoDB endpoint URL (for local development with LocalStack)",
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

    add_history_to_messages: bool = NodeVariableSettings(
        dock=True,
        default=True,
        info="If True, adds messages from chat history to the list sent to the model for better context.",
    )

    num_history_runs: int = NodeVariableSettings(
        dock=True,
        default=20,
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

    # Run optimization removed - DynamoDB 400KB limit makes it ineffective

    db_instance: BaseDb | None = NodeVariableSettings(
        label="Database Instance",
        has_out=True,
        info="DynamoDB database instance for Agno v2",
    )

    def provide_db_settings(self) -> dict:
        """Provide storage-related settings for the agent (runtime context)."""
        return {
            "add_history_to_context": self.add_history_to_messages,
            "num_history_runs": self.num_history_runs,
            "read_chat_history": self.read_chat_history,
            "enable_user_memories": self.enable_user_memories,
        }

    async def provide_instance(self) -> BaseDb:
        """Create and return DynamoDB database instance."""
        is_lambda = (
            "AWS_EXECUTION_ENV" in os.environ
            and os.environ["AWS_EXECUTION_ENV"].lower().startswith("aws_lambda")
        )

        kwargs = {}
        
        # Region
        if self.region_name:
            kwargs["region_name"] = self.region_name

        # Credentials
        if self.aws_access_key_id and self.aws_secret_access_key:
            kwargs["aws_access_key_id"] = self.aws_access_key_id
            kwargs["aws_secret_access_key"] = self.aws_secret_access_key
        elif not is_lambda:
            ak = os.environ.get("AWS_ACCESS_KEY_ID")
            sk = os.environ.get("AWS_SECRET_ACCESS_KEY")
            if ak and sk:
                kwargs["aws_access_key_id"] = ak
                kwargs["aws_secret_access_key"] = sk

        # Table names with tenant-project prefix
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

        # Create the base DynamoDB instance
        base_db = DynamoDb(**kwargs)
        
        # DynamoDB has 400KB item limit, so optimization wrapper is useless
        # Use base DynamoDB directly
        print(f"[DynamoDbDatabase] Using DynamoDB (400KB limit per item)")
        self.db_instance = base_db

        return self.db_instance