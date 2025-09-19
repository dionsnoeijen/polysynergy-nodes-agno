from typing import Any, Union, Sequence
from agno.knowledge import Knowledge
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

    vector_db: VectorDb | None = NodeVariableSettings(
        label="Vector Database",
        has_in=True,
        info="Connected vector database service for storing and querying document vectors.",
        type="agno.vectordb.base.VectorDb",
    )

    urls: list[Union[str, dict[str, Any]]] = NodeVariableSettings(
        label="Document URLs/Paths",
        has_in=True,
        dock=dock_dict(
            key_label="URL/Path",
            value_label="Metadata",
            info="List of document URLs (http/https) or S3 keys (path/to/file.pdf) with optional metadata."
        ),
        default=[],
        info="Mixed document URLs or S3 paths with optional metadata.",
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
        """Load documents into the knowledge base."""
        try:

            # Download documents to temp directory
            print(f"Processing {len(self.urls)} URLs...")
            exts: Sequence[str] = self.allowed_extensions or [".pdf", ".docx"]
            print(f"Enriching metadata for URLs with extensions: {exts}")
            url_items = enrich_metadata(self.urls or [], extensions=exts)
            print(f"Downloading {len(url_items)} items to temp directory...")
            path_items = download_mixed_items_to_tmp(url_items, extensions=exts)
            print(f"Downloaded {len(path_items)} files successfully")

            if not path_items:
                self.false_path = "No valid documents found after processing URLs."
                return

            # Get the knowledge instance once
            knowledge_base = await self.knowledge_instance()

            # Add content for each downloaded file using async API
            processed_count = 0
            failed_count = 0

            for path_item in path_items:
                try:
                    # Get metadata for this specific document
                    item_metadata = path_item.get("metadata", {})

                    # Use add_content_async with metadata per document
                    await knowledge_base.add_content_async(
                        path=path_item["path"],
                        metadata=item_metadata,  # Enriched metadata per document
                        # Reader will be determined automatically by file extension
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