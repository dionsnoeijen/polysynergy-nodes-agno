import os
from typing import Optional, Any

from agno.storage.base import Storage
from agno.storage.dynamodb import DynamoDbStorage
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

from polysynergy_nodes_agno.agno_storage.wrappers.dynamodb_agent_storage_wrapper import DeltaStorageWrapper


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

    # Agno history gedrag richting model
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

    persist_delta_only: bool = NodeVariableSettings(
        label="Store Only Last Turn (Delta)",
        dock=True,
        default=True,
        info=(
            "⚡ Storage optimization: when saving, only the most recent turn "
            "(the latest user message + the latest agent reply) is persisted. "
            "This prevents duplicate data and oversized JSON records.\n\n"
            "➡ Note: this setting only affects how chat history is stored. "
            "The agent still has full conversational context based on "
            "'add_history_to_messages' and 'num_history_runs'. "
            "The AI can therefore use multiple past turns in its reasoning."
        ),
    )

    storage_instance: Storage | None = NodeVariableSettings(
        label="Storage Instance",
        has_out=True,
        info="DynamoDB-backed storage instance for conversation history",
    )

    async def provide_instance(self) -> Storage:
        """Create and return DynamoDB-backed Storage instance (optionally wrapped)."""
        is_lambda = (
            "AWS_EXECUTION_ENV" in os.environ
            and os.environ["AWS_EXECUTION_ENV"].lower().startswith("aws_lambda")
        )

        kwargs = {"table_name": self.table_name}
        if self.region_name:
            kwargs["region_name"] = self.region_name

        # credentials
        if self.aws_access_key_id and self.aws_secret_access_key:
            kwargs["aws_access_key_id"] = self.aws_access_key_id
            kwargs["aws_secret_access_key"] = self.aws_secret_access_key
        elif not is_lambda:
            ak = os.environ.get("AWS_ACCESS_KEY_ID")
            sk = os.environ.get("AWS_SECRET_ACCESS_KEY")
            if ak and sk:
                kwargs["aws_access_key_id"] = ak
                kwargs["aws_secret_access_key"] = sk

        # localstack e.d.
        if self.endpoint_url:
            kwargs["endpoint_url"] = self.endpoint_url

        base = DynamoDbStorage(**kwargs)
        self.storage_instance = DeltaStorageWrapper(base) if self.persist_delta_only else base

        print(f"{self.storage_instance.__class__.__name__} initialized with table '{self.table_name}' in region '{self.region_name}'")

        return self.storage_instance

    def provide_storage_settings(self) -> dict:
        """Provide storage-related settings for the agent (runtime context)."""
        return {
            "add_history_to_messages": self.add_history_to_messages,
            "num_history_runs": self.num_history_runs,
            "read_chat_history": self.read_chat_history,
        }

    async def execute(self):
        pass