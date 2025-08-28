from agno.knowledge import AgentKnowledge
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.base import VectorDb
from agno.document.chunking.fixed import FixedSizeChunking
from agno.document.chunking.recursive import RecursiveChunking
from polysynergy_node_runner.setup_context.dock_property import dock_property, dock_dict
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode
from polysynergy_node_runner.execution_context.is_compatible_provider import is_compatible_provider


@node(
    name="PDF URL Knowledge Base",
    category="agno_knowledge",
    icon="brain.svg",
    has_enabled_switch=False,
)
class PDFUrlKnowledge(ServiceNode):
    """
    PDF URL-based knowledge base for Agno agents.
    Loads PDF documents from URLs with metadata for filtering.
    """

    # Vector Database Input (connected from vector DB service nodes)
    vector_db: VectorDb | None = NodeVariableSettings(
        label="Vector Database",
        dock=True,
        has_in=True,
        info="Vector database service to store document embeddings (e.g., LanceDB, Qdrant).",
    )

    # PDF URLs with metadata
    urls: list[dict[str, any]] = NodeVariableSettings(
        label="PDF URLs",
        has_in=True,
        dock=dock_dict(
            key_label="URL",
            value_label="Metadata",
            info="List of PDF URLs with optional metadata for filtering."
        ),
        default=[],
        info="PDF URLs to load with optional metadata (cuisine, source, region, etc.)",
    )

    # Knowledge Base Configuration
    num_documents: int | None = NodeVariableSettings(
        label="Max Documents",
        dock=True,
        info="Maximum number of documents to load (optional limit).",
    )

    optimize_on: int | None = NodeVariableSettings(
        label="Optimize On",
        dock=True,
        default=1000,
        info="Number of documents to optimize the vector database on.",
    )

    chunking_strategy: str | None = NodeVariableSettings(
        label="Chunking Strategy", 
        dock=dock_property(select_values={
            "fixed": "fixed",
            "recursive": "recursive"
        }),
        default="fixed",
        info="How to split documents into chunks for embedding.",
    )

    formats: list[str] | None = NodeVariableSettings(
        label="Supported Formats",
        dock=True,
        default=["pdf"],
        info="Document formats to process (default: pdf).",
    )

    # Output
    knowledge_base_instance: AgentKnowledge | None = NodeVariableSettings(
        label="Knowledge Base Instance",
        has_out=True,
        info="PDF URL knowledge base instance for use in agents",
    )

    async def _find_connected_vector_db(self) -> VectorDb | None:
        """Find connected vector database from input connections."""
        vector_db_connections = [c for c in self.get_in_connections() if c.target_handle == "vector_db"]
        
        for conn in vector_db_connections:
            vector_db_node = self.state.get_node_by_id(conn.source_node_id)
            if hasattr(vector_db_node, "provide_instance") and is_compatible_provider(vector_db_node, VectorDb):
                return await vector_db_node.provide_instance()
        
        return None

    async def provide_instance(self) -> AgentKnowledge:
        """Create and return PDF URL knowledge base instance."""
        
        print(f"[PDFUrlKnowledge] Starting to create knowledge base instance")
        
        # Get connected vector database
        vector_db = await self._find_connected_vector_db()
        if not vector_db:
            print(f"[PDFUrlKnowledge] ERROR: No vector database connected")
            raise ValueError("No vector database connected. Please connect a vector database service node.")
        
        print(f"[PDFUrlKnowledge] Connected vector database: {type(vector_db).__name__}")

        # Convert URLs to format expected by PDFUrlKnowledgeBase
        # Support multiple input formats:
        # 1. Simple string array: ["url1.pdf", "url2.pdf"]
        # 2. URL + metadata objects: [{"url": "url1.pdf", "metadata": {...}}]
        # 3. Dock dict format: [{"key": "url1.pdf", "value": "{}"}]
        print(f"[PDFUrlKnowledge] Processing URLs input: {self.urls}")
        print(f"[PDFUrlKnowledge] URLs type: {type(self.urls)}")
        
        formatted_urls = []
        if self.urls:
            print(f"[PDFUrlKnowledge] Found {len(self.urls)} URL entries to process")
            for i, url_item in enumerate(self.urls):
                print(f"[PDFUrlKnowledge] Processing URL {i+1}: {url_item} (type: {type(url_item)})")
                
                if isinstance(url_item, str):
                    # Format 1: Simple string URL
                    print(f"[PDFUrlKnowledge] Format 1: Simple string URL detected")
                    # Check if URL contains .pdf (even with query parameters)
                    if ".pdf" in url_item.lower():
                        print(f"[PDFUrlKnowledge] URL contains .pdf, adding to list with auto-generated metadata")
                        
                        # Auto-add source information for simple string URLs
                        import os
                        from urllib.parse import urlparse, unquote
                        
                        try:
                            parsed_url = urlparse(url_item)
                            # Get filename from URL path
                            filename = os.path.basename(unquote(parsed_url.path))
                            if not filename or filename == '/':
                                # Fallback: use last part of domain + timestamp
                                filename = f"{parsed_url.netloc.split('.')[-2]}_document.pdf"
                        except Exception as e:
                            print(f"[PDFUrlKnowledge] Could not extract document name from URL: {e}")
                            filename = "Unknown Document"
                        
                        # Convert simple string URL to dict format with metadata
                        formatted_url_with_metadata = {
                            "url": url_item,
                            "metadata": {
                                "document_name": filename,
                                "source_url": url_item
                            }
                        }
                        
                        print(f"[PDFUrlKnowledge] Auto-added source metadata: document_name='{filename}', source_url='{url_item}'")
                        formatted_urls.append(formatted_url_with_metadata)
                    else:
                        print(f"[PDFUrlKnowledge] WARNING: URL does not contain .pdf, skipping: {url_item}")
                elif isinstance(url_item, dict):
                    if "url" in url_item:
                        # Format 2: Already in PDFUrlKnowledgeBase format
                        print(f"[PDFUrlKnowledge] Format 2: URL+metadata dict detected")
                        formatted_urls.append(url_item)
                    elif "key" in url_item:
                        # Format 3: Dock dict format - convert to PDFUrlKnowledgeBase format
                        print(f"[PDFUrlKnowledge] Format 3: Dock dict format detected")
                        url = url_item.get("key", "")
                        metadata_str = url_item.get("value", "{}")
                        
                        # Parse metadata if it's a string
                        if isinstance(metadata_str, str):
                            try:
                                import json
                                metadata = json.loads(metadata_str) if metadata_str.strip() else {}
                            except:
                                metadata = {}
                        else:
                            metadata = metadata_str or {}
                        
                        if url:
                            # Auto-add source information if not provided
                            if "document_name" not in metadata and "source" not in metadata:
                                # Extract document name from URL
                                import os
                                from urllib.parse import urlparse, unquote
                                
                                try:
                                    parsed_url = urlparse(url)
                                    # Get filename from URL path
                                    filename = os.path.basename(unquote(parsed_url.path))
                                    if not filename or filename == '/':
                                        # Fallback: use last part of domain + timestamp
                                        filename = f"{parsed_url.netloc.split('.')[-2]}_document.pdf"
                                    
                                    # Add source metadata
                                    metadata["document_name"] = filename
                                    metadata["source_url"] = url
                                    print(f"[PDFUrlKnowledge] Auto-added source metadata: document_name='{filename}', source_url='{url}'")
                                except Exception as e:
                                    print(f"[PDFUrlKnowledge] Could not extract document name from URL: {e}")
                                    metadata["document_name"] = "Unknown Document"
                                    metadata["source_url"] = url
                            
                            result = {
                                "url": url,
                                "metadata": metadata
                            }
                            print(f"[PDFUrlKnowledge] Converted dock format to: {result}")
                            formatted_urls.append(result)
                        else:
                            print(f"[PDFUrlKnowledge] WARNING: Empty URL in dock dict, skipping")
                    else:
                        print(f"[PDFUrlKnowledge] WARNING: Unknown dict format, skipping: {url_item}")
                else:
                    print(f"[PDFUrlKnowledge] WARNING: Unknown URL format, skipping: {url_item}")
        else:
            print(f"[PDFUrlKnowledge] No URLs provided")
        
        print(f"[PDFUrlKnowledge] Final formatted URLs: {formatted_urls}")
        print(f"[PDFUrlKnowledge] Total URLs to process: {len(formatted_urls)}")

        kwargs = {
            "urls": formatted_urls,
            "vector_db": vector_db,
        }
        
        print(f"[PDFUrlKnowledge] Building PDFUrlKnowledgeBase with base kwargs: urls={len(formatted_urls)} items, vector_db={type(vector_db).__name__}")

        if self.num_documents is not None:
            kwargs["num_documents"] = self.num_documents
            print(f"[PDFUrlKnowledge] Added num_documents: {self.num_documents}")
            
        if self.optimize_on:
            kwargs["optimize_on"] = self.optimize_on
            print(f"[PDFUrlKnowledge] Added optimize_on: {self.optimize_on}")
            
        if self.chunking_strategy:
            strategy_map = {
                "fixed": FixedSizeChunking(),
                "recursive": RecursiveChunking(),
            }
            strategy_instance = strategy_map.get(self.chunking_strategy, FixedSizeChunking())
            kwargs["chunking_strategy"] = strategy_instance
            print(f"[PDFUrlKnowledge] Added chunking_strategy: {self.chunking_strategy} -> {type(strategy_instance).__name__}")
            
        if self.formats:
            kwargs["formats"] = self.formats
            print(f"[PDFUrlKnowledge] Added formats: {self.formats}")

        print(f"[PDFUrlKnowledge] Creating PDFUrlKnowledgeBase instance with all parameters")
        
        # Create PDF URL knowledge base instance
        try:
            self.knowledge_base_instance = PDFUrlKnowledgeBase(**kwargs)
            
            # Override the _is_valid_url method to handle S3 signed URLs
            original_is_valid_url = self.knowledge_base_instance._is_valid_url
            
            def custom_is_valid_url(url: str) -> bool:
                """Custom URL validation that handles S3 signed URLs with query parameters."""
                print(f"[PDFUrlKnowledge] Validating URL: {url}")
                
                # Check if URL contains .pdf anywhere (not just at the end)
                if ".pdf" in url.lower():
                    print(f"[PDFUrlKnowledge] URL is valid (contains .pdf)")
                    return True
                else:
                    print(f"[PDFUrlKnowledge] URL is invalid (no .pdf found)")
                    return False
            
            # Replace the validation method
            self.knowledge_base_instance._is_valid_url = custom_is_valid_url
            
            print(f"[PDFUrlKnowledge] Successfully created PDFUrlKnowledgeBase instance")
            print(f"[PDFUrlKnowledge] Instance type: {type(self.knowledge_base_instance).__name__}")
            print(f"[PDFUrlKnowledge] Instance URLs: {self.knowledge_base_instance.urls}")
            print(f"[PDFUrlKnowledge] Custom URL validation installed")
            return self.knowledge_base_instance
        except Exception as e:
            print(f"[PDFUrlKnowledge] ERROR: Failed to create PDFUrlKnowledgeBase: {e}")
            import traceback
            traceback.print_exc()
            raise
