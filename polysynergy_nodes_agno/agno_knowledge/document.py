import os
from typing import Any, Union, Sequence
from agno.knowledge import Knowledge
from agno.knowledge.chunking.strategy import ChunkingStrategy
from agno.vectordb import VectorDb
from polysynergy_node_runner.setup_context.dock_property import dock_dict
from polysynergy_node_runner.setup_context.node import Node
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.path_settings import PathSettings

from polysynergy_nodes_agno.agno_agent.utils.find_connected_service import find_connected_service
from polysynergy_nodes_agno.agno_knowledge.utils.enrich_metadata import enrich_metadata
from polysynergy_nodes_agno.agno_knowledge.utils.download_mixed_items_to_tmp import download_mixed_items_to_tmp

@node(
    name="Document Knowledge",
    category="agno_knowledge",
    icon="brain.svg",
    has_enabled_switch=False,
)
class DocumentKnowledge(Node):
    """
    Load documents into a vector knowledge base with support for URLs, file paths, and bytes content.

    Supports multiple input formats:
    - URLs: Download and process documents from HTTP(S) URLs
    - S3 keys: Download from S3 buckets
    - Local file paths: Process existing files from /tmp/ or other locations
    - Bytes content: Process in-memory document bytes (e.g., from HTTP requests)

    Examples:

    1. URLs:
    {
      "url": "https://example.com/document.pdf",
      "metadata": {"source": "web", "category": "manual"}
    }

    2. Local file path:
    {
      "url": "/tmp/document.pdf",
      "metadata": {"uploaded_by": "user123"}
    }

    3. Bytes content (recommended - use 'bytes' key):
    {
      "bytes": <PDF_BYTES>,
      "metadata": {"filename": "report.pdf", "source": "http_request"}
    }

    4. Bytes content (alternative - via 'url' key):
    {
      "url": <PDF_BYTES>,
      "metadata": {"filename": "report.pdf"}
    }

    The node automatically detects the input type and processes accordingly.
    For bytes content, "filename" is REQUIRED in metadata to identify the document.
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
        info="Chunking strategy for splitting documents into chunks for vector storage.",
        type="agno.knowledge.chunking.strategy.ChunkingStrategy",
    )

    urls_or_paths: list = NodeVariableSettings(
        label="URLs, Paths, or Bytes",
        has_in=True,
        dock=dock_dict(
            key_label="URL/Path/Bytes",
            value_label="Metadata",
            info="URLs (http/https), S3 keys, local paths (/tmp/file.pdf), or bytes content with metadata including 'filename'"
        ),
        default=[],
        info="Mixed URLs, S3 keys, local file paths, or bytes content with optional metadata.",
    )

    allowed_extensions: list[str] | None = NodeVariableSettings(
        label="Allowed Extensions",
        dock=True,
        default=[".pdf", ".docx", ".doc", ".rtf", ".txt", ".pptx", ".xlsx", ".csv"],
        info="Extensions to accept from URLs and S3 paths.",
    )

    num_documents: int | None = NodeVariableSettings(label="Max Documents", dock=True)
    optimize_on: int | None = NodeVariableSettings(label="Optimize On", dock=True, default=1000)

    true_path: bool | str = PathSettings(label="Success")
    false_path: bool | str = PathSettings(label="Failure")

    async def knowledge_instance(self) -> Knowledge:
        """Create Knowledge instance with connected vector database and load documents."""
        # Get connected vector database
        vector_db = await find_connected_service(self, "vector_db", VectorDb)
        if not vector_db:
            raise ValueError("No vector database connected. Please connect a Vector Database node.")

        # Create Knowledge instance with the vector database
        return Knowledge(vector_db=vector_db)

    async def execute(self):
        """Load documents into the knowledge base with configurable chunking strategy."""
        try:
            exts: Sequence[str] = self.allowed_extensions or [".pdf", ".docx"]

            # First separate bytes items from URL/path items
            # because enrich_metadata doesn't handle bytes
            raw_items = self.urls_or_paths or []
            bytes_items = []
            url_path_items = []

            for item in raw_items:
                if isinstance(item, dict):
                    # Check for bytes content first (can be under "bytes" or "url" key)
                    bytes_content = item.get("bytes")
                    if bytes_content and isinstance(bytes_content, bytes):
                        bytes_items.append(item)
                        continue

                    # Check if url value is actually bytes
                    url_value = item.get("url")
                    if isinstance(url_value, bytes):
                        # Convert to bytes format
                        bytes_items.append({"bytes": url_value, "metadata": item.get("metadata", {})})
                        continue

                # Not bytes, add to url/path items for enrichment
                url_path_items.append(item)

            # Process URLs/paths through enrichment
            enriched_items = enrich_metadata(url_path_items, extensions=exts)

            # Separate URLs/S3 keys from local file paths
            url_items = []
            local_path_items = []

            for item in enriched_items:
                metadata = item.get("metadata", {})
                path_or_url = item.get("url")

                if path_or_url:
                    # Check if it's a URL or local path
                    if path_or_url.startswith(('http://', 'https://')):
                        # It's a URL - needs downloading
                        url_items.append(item)
                    elif os.path.exists(path_or_url):
                        # It's an existing local file path
                        local_path_items.append({"path": path_or_url, "metadata": metadata})
                    else:
                        # Assume it's S3 key or URL - let download function handle it
                        url_items.append(item)

            # Download URLs and S3 keys to tmp
            downloaded_items = download_mixed_items_to_tmp(url_items, extensions=exts) if url_items else []

            # Handle bytes items - write to temp files
            bytes_path_items = []
            if bytes_items:
                import tempfile

                for bytes_item in bytes_items:
                    # Get filename from metadata - REQUIRED for bytes
                    metadata = bytes_item.get("metadata", {})
                    filename = metadata.get("filename")

                    if not filename:
                        raise ValueError(
                            "Filename is required in metadata when providing bytes content. "
                            "Example: {'bytes': <BYTES>, 'metadata': {'filename': 'document.pdf'}}"
                        )

                    # Ensure file has extension
                    if not any(filename.endswith(ext) for ext in exts):
                        # Default to .pdf if no recognized extension
                        filename = f"{filename}.pdf"

                    # Write bytes to temp file
                    temp_path = os.path.join(tempfile.gettempdir(), filename)
                    with open(temp_path, 'wb') as f:
                        f.write(bytes_item["bytes"])

                    print(f"Wrote {len(bytes_item['bytes'])} bytes to {temp_path}")
                    bytes_path_items.append({"path": temp_path, "metadata": metadata})

            # Combine downloaded, existing local files, and bytes-converted files
            path_items = downloaded_items + local_path_items + bytes_path_items

            if not path_items:
                self.false_path = "No valid documents found after processing URLs and tmp paths."
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

            # Add content for each downloaded file using async API with custom chunking
            processed_count = 0
            failed_count = 0

            for path_item in path_items:
                try:
                    # Get metadata for this specific document
                    item_metadata = path_item.get("metadata", {})
                    item_metadata["chunking_strategy"] = chunker.__class__.__name__

                    # Use add_content_async with custom reader that uses our chunking strategy
                    await self._add_content_with_chunking(
                        knowledge_base=knowledge_base,
                        path=path_item["path"],
                        metadata=item_metadata,
                        chunker=chunker
                    )
                    processed_count += 1
                except Exception as e:
                    print(f"Failed to process document {path_item.get('path', 'unknown')}: {str(e)}")
                    failed_count += 1

            # Set success/failure paths with useful info
            if processed_count > 0:
                if failed_count == 0:
                    self.true_path = f"Successfully processed {processed_count} documents"
                else:
                    self.true_path = f"Processed {processed_count} documents ({failed_count} failed)"
            else:
                self.false_path = f"Failed to process all {len(path_items)} documents"

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Document processing error - Full trace:\n{error_trace}")
            self.false_path = f"Error during document processing: {str(e)}"
            raise

    async def _add_content_with_chunking(self, knowledge_base, path, metadata, chunker):
        """Add content to knowledge base with custom chunking strategy."""
        from agno.knowledge.reader import ReaderFactory
        from agno.knowledge.content import Content
        from pathlib import Path
        from uuid import uuid4

        # Create a Content object without automatic chunking
        content_id = str(uuid4())
        content = Content(
            id=content_id,
            path=path,
            metadata=metadata
        )

        # Get appropriate reader for the file type
        file_path = Path(path)
        reader = ReaderFactory.get_reader_for_extension(file_path.suffix)

        if not reader:
            raise ValueError(f"No reader available for file type: {file_path.suffix}")

        # Read the document without chunking (run in thread pool to avoid blocking)
        import asyncio
        reader.chunk = False  # Disable automatic chunking
        documents = await asyncio.to_thread(reader.read, file_path, name=file_path.name)

        if not documents:
            raise ValueError(f"No content could be read from: {path}")

        # Apply custom chunking strategy
        print(f"Applying {chunker.__class__.__name__} to {len(documents)} documents")

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

        print(f"Created {len(chunked_documents)} chunks")

        # Set content_id for all chunks
        for doc in chunked_documents:
            doc.content_id = content_id
            if metadata:
                doc.meta_data.update(metadata)

        # Add to vector database directly
        if knowledge_base.vector_db:
            content_hash = knowledge_base._build_content_hash(content)
            await knowledge_base.vector_db.async_insert(
                content_hash=content_hash,
                documents=chunked_documents,
                filters=metadata
            )
            print(f"Successfully inserted {len(chunked_documents)} chunks to vector database")
        else:
            raise ValueError("No vector database available in knowledge base")