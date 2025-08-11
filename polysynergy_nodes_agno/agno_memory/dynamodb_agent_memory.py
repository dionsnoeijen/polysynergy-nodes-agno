import os
from typing import Optional

from agno.memory import AgentMemory
from agno.storage.dynamodb import DynamoDbStorage
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="DynamoDB Agent Memory",
    category="agno_memory",
    icon="memory.svg",
    has_enabled_switch=False,
)
class DynamoDBAgentMemory(ServiceNode):
    """
    DynamoDB-backed memory for Agno agents.
    Perfect for serverless/Lambda deployments and persistent memory across sessions.
    """

    table_name: str = NodeVariableSettings(
        label="Table Name",
        dock=True,
        default="agno_agent_memory",
        info="Name of the DynamoDB table for storing agent memory",
    )

    region_name: str = NodeVariableSettings(
        label="AWS Region",
        dock=True,
        default="us-east-1",
        info="AWS region where DynamoDB table is located",
    )

    aws_access_key_id: Optional[str] = NodeVariableSettings(
        label="AWS Access Key ID",
        dock=True,
        info="AWS access key ID (leave empty to use default credentials)",
    )

    aws_secret_access_key: Optional[str] = NodeVariableSettings(
        label="AWS Secret Access Key",
        dock=True,
        info="AWS secret access key (leave empty to use default credentials)",
    )

    endpoint_url: Optional[str] = NodeVariableSettings(
        label="Endpoint URL",
        dock=True,
        info="Custom DynamoDB endpoint URL (for local development with LocalStack)",
    )

    create_table_if_not_exists: bool = NodeVariableSettings(
        label="Auto Create Table",
        dock=True,
        default=True,
        info="Automatically create DynamoDB table if it doesn't exist",
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

    memory_instance: AgentMemory | None = NodeVariableSettings(
        label="Memory Instance",
        has_out=True,
        info="DynamoDB-backed agent memory instance for use in agents",
    )

    async def provide_instance(self) -> AgentMemory:
        """Create and return DynamoDB-backed AgentMemory instance."""
        
        # Use environment variables if node values are empty
        access_key = self.aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = self.aws_secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
        region = self.region_name or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

        # Create DynamoDB storage backend
        storage = DynamoDbStorage(
            table_name=self.table_name,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=self.endpoint_url,
            create_table_if_not_exists=self.create_table_if_not_exists,
        )

        # Create AgentMemory with DynamoDB backend
        self.memory_instance = AgentMemory(
            db=storage,
            create_user_memories=self.create_user_memories,
            create_session_summary=self.create_session_summary,
        )

        return self.memory_instance

    async def execute(self):
        pass