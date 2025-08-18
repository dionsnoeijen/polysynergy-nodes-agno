"""DynamoDB implementation of the MemoryDb interface for Agno AgentMemory."""
import os
from typing import List, Optional
from datetime import datetime
import json

try:
    import boto3
    from boto3.dynamodb.conditions import Key
    from botocore.exceptions import ClientError
except ImportError:
    raise ImportError("`boto3` not installed. Please install it with `pip install boto3`")

from agno.memory.v2.db.memory_db import MemoryDb
from agno.memory.v2.row import MemoryRow
from agno.utils.log import log_debug, log_info, logger


class DynamoDbMemoryDb(MemoryDb):
    """DynamoDB implementation of the MemoryDb interface."""
    
    def __init__(
        self,
        table_name: str = "agno_agent_memory",
        region_name: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        create_table_if_not_exists: bool = True,
        session_id: Optional[str] = None,
    ):
        """
        Initialize DynamoDB memory database.
        
        Args:
            table_name: Name of the DynamoDB table
            region_name: AWS region name
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            endpoint_url: Custom endpoint URL (for LocalStack)
            create_table_if_not_exists: Auto-create table if it doesn't exist
            session_id: Session ID to use for storing memories
        """
        self.table_name = table_name
        self.create_table_if_not_exists = create_table_if_not_exists
        self.session_id = session_id or 'default'
        
        # Initialize DynamoDB client
        client_kwargs = {}
        if region_name:
            client_kwargs['region_name'] = region_name
        if aws_access_key_id and aws_secret_access_key:
            client_kwargs['aws_access_key_id'] = aws_access_key_id
            client_kwargs['aws_secret_access_key'] = aws_secret_access_key
        if endpoint_url:
            client_kwargs['endpoint_url'] = endpoint_url
            
        self.dynamodb = boto3.resource('dynamodb', **client_kwargs)
        self.client = boto3.client('dynamodb', **client_kwargs)
        
        # Initialize table
        self._table = None
        if self.create_table_if_not_exists:
            self.create()
    
    @property
    def table(self):
        """Get or create the DynamoDB table."""
        if self._table is None:
            self._table = self.dynamodb.Table(self.table_name)
        return self._table
    
    def create(self) -> None:
        """Create the DynamoDB table if it doesn't exist."""
        if not self.table_exists():
            try:
                log_debug(f"Creating DynamoDB table: {self.table_name}")
                self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {'AttributeName': 'session_id', 'KeyType': 'HASH'},  # Primary key
                        {'AttributeName': 'id', 'KeyType': 'RANGE'},  # Sort key
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'session_id', 'AttributeType': 'S'},
                        {'AttributeName': 'id', 'AttributeType': 'S'},
                        {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'user_id_index',
                            'KeySchema': [
                                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                            ],
                            'Projection': {'ProjectionType': 'ALL'},
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST',
                )
                # Wait for table to be created
                self.table.wait_until_exists()
                log_info(f"Created DynamoDB table: {self.table_name}")
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceInUseException':
                    logger.error(f"Error creating table '{self.table_name}': {e}")
                    raise
    
    def memory_exists(self, memory: MemoryRow) -> bool:
        """Check if a memory exists in the database."""
        try:
            # Use the session_id from the database instance
            session_id = self.session_id
            response = self.table.get_item(Key={'session_id': session_id, 'id': memory.id})
            return 'Item' in response
        except ClientError as e:
            logger.error(f"Error checking memory existence: {e}")
            return False
    
    def read_memories(
        self, user_id: Optional[str] = None, limit: Optional[int] = None, sort: Optional[str] = None
    ) -> List[MemoryRow]:
        """Read memories from the database."""
        memories: List[MemoryRow] = []
        
        try:
            if user_id:
                # Query using the user_id index
                response = self.table.query(
                    IndexName='user_id_index',
                    KeyConditionExpression=Key('user_id').eq(user_id),
                    ScanIndexForward=(sort == 'asc'),
                    Limit=limit if limit else 100
                )
                items = response.get('Items', [])
            else:
                # Query for the current session_id only
                response = self.table.query(
                    KeyConditionExpression=Key('session_id').eq(self.session_id),
                    ScanIndexForward=(sort == 'asc'),
                    Limit=limit if limit else 100
                )
                items = response.get('Items', [])
            
            for item in items:
                # Parse the memory field
                memory_data = item.get('memory', '{}')
                if isinstance(memory_data, str):
                    try:
                        memory_data = json.loads(memory_data)
                    except json.JSONDecodeError:
                        try:
                            memory_data = eval(memory_data)
                        except:
                            memory_data = {}
                
                memories.append(MemoryRow(
                    id=item['id'],
                    user_id=item.get('user_id'),
                    memory=memory_data
                ))
                
        except ClientError as e:
            log_debug(f"Exception reading from table: {e}")
            if not self.table_exists():
                log_debug(f"Table does not exist: {self.table_name}")
                log_debug("Creating table for future transactions")
                self.create()
        
        return memories
    
    def upsert_memory(self, memory: MemoryRow) -> Optional[MemoryRow]:
        """Insert or update a memory in the database."""
        try:
            # Serialize memory object
            memory_str = json.dumps(memory.memory) if isinstance(memory.memory, dict) else str(memory.memory)
            
            # Use the session_id from the database instance (passed from AgentMemory)
            session_id = self.session_id
            
            item = {
                'session_id': session_id,
                'id': memory.id,
                'user_id': memory.user_id or 'default',
                'memory': memory_str,
                'updated_at': datetime.utcnow().isoformat(),
            }
            
            # Check if this is a new item
            existing = self.memory_exists(memory)
            if not existing:
                item['created_at'] = datetime.utcnow().isoformat()
            
            # Debug logging
            logger.info(f"Storing memory in DynamoDB - session_id: {session_id}, id: {memory.id}, user_id: {memory.user_id}")
            logger.debug(f"Memory content: {memory_str[:200]}...")
            
            # Put item (this will insert or update)
            self.table.put_item(Item=item)
            logger.info(f"Successfully stored memory in DynamoDB")
            return memory
            
        except ClientError as e:
            logger.error(f"Exception upserting into table: {e}")
            if not self.table_exists():
                log_info(f"Table does not exist: {self.table_name}")
                log_info("Creating table for future transactions")
                self.create()
                # Retry once after creating table
                return self.upsert_memory(memory)
            raise
    
    def delete_memory(self, id: str, session_id: str = 'default') -> None:
        """Delete a memory from the database."""
        try:
            self.table.delete_item(Key={'session_id': session_id, 'id': id})
        except ClientError as e:
            logger.error(f"Error deleting memory: {e}")
            raise
    
    def drop_table(self) -> None:
        """Drop the DynamoDB table."""
        if self.table_exists():
            try:
                log_debug(f"Deleting table: {self.table_name}")
                self.table.delete()
                self.table.wait_until_not_exists()
            except ClientError as e:
                logger.error(f"Error dropping table: {e}")
                raise
    
    def table_exists(self) -> bool:
        """Check if the table exists."""
        try:
            self.client.describe_table(TableName=self.table_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return False
            logger.error(f"Error checking table existence: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all items from the table."""
        try:
            # Scan and delete all items
            response = self.table.scan()
            items = response.get('Items', [])
            
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.delete_item(Key={
                        'session_id': item.get('session_id', 'default'),
                        'id': item['id']
                    })
            
            # Handle pagination if there are more items
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items = response.get('Items', [])
                with self.table.batch_writer() as batch:
                    for item in items:
                        batch.delete_item(Key={
                            'session_id': item.get('session_id', 'default'),
                            'id': item['id']
                        })
            
            return True
        except ClientError as e:
            logger.error(f"Error clearing table: {e}")
            return False