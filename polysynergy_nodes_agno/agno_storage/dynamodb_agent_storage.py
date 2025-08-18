import os
from typing import Optional

from agno.storage.base import Storage
from agno.storage.dynamodb import DynamoDbStorage
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="DynamoDB Agent Storage",
    category="agno_storage",
    icon="storage.svg",
    has_enabled_switch=False,
)
class DynamoDBAgentStorage(ServiceNode):
    """
    DynamoDB-backed storage for Agno agents.
    Stores conversation history and session data.
    Perfect for serverless/Lambda deployments and persistent storage across sessions.
    """

    table_name: str = NodeVariableSettings(
        label="Table Name",
        dock=True,
        default="agno_agent_sessions",
        info="Name of the DynamoDB table for storing conversation history",
    )

    region_name: str = NodeVariableSettings(
        label="AWS Region",
        dock=True,
        default="eu-central-1",
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

    storage_instance: Storage | None = NodeVariableSettings(
        label="Storage Instance",
        has_out=True,
        info="DynamoDB-backed storage instance for conversation history",
    )

    async def provide_instance(self) -> Storage:
        """Create and return DynamoDB-backed Storage instance."""
        
        # Use environment variables if node values are empty
        access_key = self.aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = self.aws_secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
        region = self.region_name or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        
        # Create DynamoDB storage for conversation history
        self.storage_instance = DynamoDbStorage(
            table_name=self.table_name,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=self.endpoint_url,
        )
        
        return self.storage_instance

    async def execute(self):
        pass