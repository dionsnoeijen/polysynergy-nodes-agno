import os
from typing import Optional

from agno.memory.v2.memory import Memory
from polysynergy_nodes_agno.agno_memory.db import DynamoDbMemoryDb
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
    Stores extracted memories from conversations.
    Perfect for serverless/Lambda deployments and persistent memory across sessions.
    """

    table_name: str = NodeVariableSettings(
        label="Table Name",
        dock=True,
        default="agno_agent_memory",
        info="Name of the DynamoDB table for storing extracted memories",
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

    memory_instance: Memory | None = NodeVariableSettings(
        label="Memory Instance",
        has_out=True,
        info="DynamoDB-backed memory instance for use in agents",
    )

    async def provide_instance(self, session_id: str) -> Memory:
        """Create and return DynamoDB-backed Memory instance."""
        
        # Use environment variables if node values are empty
        access_key = self.aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = self.aws_secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
        region = self.region_name or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

        # Get session_id from memory settings that will be used by the agent
        memory_settings = self.provide_memory_settings()

        # Create DynamoDB memory database
        memory_db = DynamoDbMemoryDb(
            table_name=self.table_name,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=self.endpoint_url,
            create_table_if_not_exists=self.create_table_if_not_exists,
            session_id=session_id,
        )

        # Create Memory with DynamoDB backend (v2 API)
        print(f"Creating Memory v2 with DynamoDB backend")
        self.memory_instance = Memory(db=memory_db)
        print(f"Memory v2 created successfully: {self.memory_instance}")
        print(f"Memory v2 db attribute: {self.memory_instance.db}")
        
        # Test if the memory database is working by attempting a test operation
        from agno.memory.v2.row import MemoryRow
        test_memory = MemoryRow(
            id="test_memory",
            user_id="test_user", 
            memory={"test": f"Test memory entry for session {session_id}"}
        )
        print(f"Testing upsert_memory with test data for session_id: {session_id}")
        try:
            result = memory_db.upsert_memory(test_memory)
            print(f"Test upsert result: {result}")
        except Exception as e:
            print(f"Test upsert failed: {e}")
            import traceback
            traceback.print_exc()

        return self.memory_instance
    
    def provide_memory_settings(self) -> dict:
        return {
            'enable_agentic_memory': True,  # Enable memory when memory node is connected
            'enable_user_memories': self.create_user_memories,
            'enable_session_summaries': self.create_session_summary,
        }

    async def execute(self):
        pass