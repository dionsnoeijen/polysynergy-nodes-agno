import json
from typing import Any, Union
from uuid import uuid4
from agno.knowledge import Knowledge
from agno.knowledge.chunking.strategy import ChunkingStrategy
from agno.knowledge.document.base import Document
from agno.vectordb import VectorDb
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.path_settings import PathSettings

from polysynergy_nodes_agno.agno_agent.utils.find_connected_service import find_connected_service


@node(
    name="JSON Knowledge",
    category="agno_knowledge",
    icon="brain.svg",
    has_enabled_switch=False,
)
class JSONKnowledge(Node):
    """Knowledge node for loading JSON data directly into a knowledge base.

    Accepts JSON arrays or objects and converts each item into a searchable document.
    Perfect for API responses, generated data, or any in-memory JSON structures.
    """

    vector_db: VectorDb | None = NodeVariableSettings(
        label="Vector Database",
        has_in=True,
        info="Connected vector database service for storing and querying document vectors.",
        type="agno.vectordb.base.VectorDb",
    )

    chunking_strategy: ChunkingStrategy | None = NodeVariableSettings(
        label="Chunking Strategy",
        has_in=True,
        info="Chunking strategy for splitting JSON content into chunks for vector storage.",
        type="agno.knowledge.chunking.strategy.ChunkingStrategy",
    )

    json_data: list | dict | str = NodeVariableSettings(
        label="JSON Data",
        has_in=True,
        default=[],
        info="JSON data as list, dict, or JSON string. Arrays are converted to individual documents.",
    )

    document_name: str = NodeVariableSettings(
        label="Document Name",
        dock=True,
        default="json_document",
        info="Name prefix for generated documents.",
    )

    optimize_on: int | None = NodeVariableSettings(
        label="Optimize On",
        dock=True,
        default=1000,
        info="Optimize vector database after this many documents.",
    )

    true_path: bool | str = PathSettings(label="Success")
    false_path: bool | str = PathSettings(label="Failure")

    async def knowledge_instance(self) -> Knowledge:
        """Create Knowledge instance with connected vector database."""
        # Get connected vector database
        vector_db = await find_connected_service(self, "vector_db", VectorDb)
        if not vector_db:
            raise ValueError("No vector database connected. Please connect a Vector Database node.")

        # Create Knowledge instance with the vector database
        return Knowledge(vector_db=vector_db)

    async def execute(self):
        """Load JSON data into the knowledge base with configurable chunking strategy."""
        try:
            # Parse json_data if it's a string
            if isinstance(self.json_data, str):
                try:
                    json_contents = json.loads(self.json_data)
                except json.JSONDecodeError as e:
                    self.false_path = f"Invalid JSON string: {str(e)}"
                    return
            else:
                json_contents = self.json_data

            # Ensure we have a list to iterate over
            if isinstance(json_contents, dict):
                json_contents = [json_contents]
            elif not isinstance(json_contents, list):
                self.false_path = f"JSON data must be a list or dict, got {type(json_contents).__name__}"
                return

            if not json_contents:
                self.false_path = "No JSON data provided"
                return

            # Get the knowledge instance and chunking strategy
            knowledge_base = await self.knowledge_instance()
            chunker = await find_connected_service(self, "chunking_strategy", ChunkingStrategy)

            if not chunker:
                # Fallback to simple default chunking
                from agno.knowledge.chunking.fixed import FixedSizeChunking
                chunker = FixedSizeChunking(chunk_size=1000, overlap=100)
                print("No chunking strategy connected, using default FixedSizeChunking (1000 chars, 100 overlap)")
            else:
                print(f"Using connected chunking strategy: {chunker.__class__.__name__}")

            # Convert each JSON object to a Document
            documents = []
            for idx, item in enumerate(json_contents, start=1):
                # Convert item to JSON string for document content
                content = json.dumps(item, ensure_ascii=False, indent=2)

                # Create metadata
                metadata = {
                    "source": "json_data",
                    "index": idx,
                    "chunking_strategy": chunker.__class__.__name__,
                }

                # Add any top-level string fields as metadata for better searchability
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, (str, int, float, bool)):
                            metadata[f"json_{key}"] = value

                # Create Document
                doc = Document(
                    name=f"{self.document_name}_{idx}",
                    id=str(uuid4()),
                    meta_data=metadata,
                    content=content,
                )
                documents.append(doc)

            print(f"Created {len(documents)} documents from JSON data")

            # Apply chunking strategy
            chunked_documents = await self._apply_chunking(documents, chunker)

            print(f"Created {len(chunked_documents)} chunks after chunking")

            # Generate content hash and insert into vector database
            if knowledge_base.vector_db:
                # Create a simple content object for hashing
                from agno.knowledge.content import Content
                content = Content(
                    id=str(uuid4()),
                    path="json_data",
                    metadata={"source": "json_data", "document_count": len(documents)}
                )
                content_hash = knowledge_base._build_content_hash(content)

                await knowledge_base.vector_db.async_insert(
                    content_hash=content_hash,
                    documents=chunked_documents,
                    filters={"source": "json_data"}
                )
                print(f"Successfully inserted {len(chunked_documents)} chunks to vector database")
            else:
                raise ValueError("No vector database available in knowledge base")

            # Set success path
            self.true_path = f"Successfully processed {len(documents)} JSON items into {len(chunked_documents)} chunks"

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"JSON processing error - Full trace:\n{error_trace}")
            self.false_path = f"Error during JSON processing: {str(e)}"
            raise

    async def _apply_chunking(self, documents: list[Document], chunker: ChunkingStrategy) -> list[Document]:
        """Apply chunking strategy to documents."""
        import asyncio

        chunked_documents = []

        # Check what chunking method is available
        if hasattr(chunker, 'chunk_documents_async'):
            # Async method for multiple documents
            chunked_documents = await chunker.chunk_documents_async(documents)
        elif hasattr(chunker, 'chunk_documents'):
            # Sync method for multiple documents - run in thread pool
            chunked_documents = await asyncio.to_thread(chunker.chunk_documents, documents)
        elif hasattr(chunker, 'chunk'):
            # Single document chunking method - run in thread pool
            def chunk_all_documents():
                all_chunks = []
                for doc in documents:
                    chunks = chunker.chunk(doc)
                    all_chunks.extend(chunks)
                return all_chunks

            chunked_documents = await asyncio.to_thread(chunk_all_documents)
        else:
            # Fallback: no chunking, use original documents
            print(f"Warning: No chunking method found, using original documents")
            chunked_documents = documents

        return chunked_documents
