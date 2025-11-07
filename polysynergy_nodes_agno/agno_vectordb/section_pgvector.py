import asyncio
import os
from uuid import UUID
from typing import Optional

from agno.knowledge.embedder import Embedder
from agno.vectordb.base import VectorDb
from agno.vectordb.search import SearchType
from agno.vectordb.distance import Distance

from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Section PgVector Database",
    category="agno_vectordb",
    icon="database.svg",
    has_enabled_switch=False,
)
class SectionPgVectorVectorDB(ServiceNode):
    # Section Selection
    section_id: str = NodeVariableSettings(
        label="Section",
        dock=dock_property(
            metadata={"source": "portal_sections"},
            placeholder="Select a section with vectorization enabled"
        ),
        has_in=True,
        info="Section to use as vector database",
    )

    # Output
    vector_db_instance: VectorDb | None = NodeVariableSettings(
        label="Vector Database Instance",
        has_out=True,
        info="Section PgVector database instance for use in knowledge bases",
    )

    def _get_embedder_from_config(self, config: dict, api_key: Optional[str]) -> Embedder:
        """Create embedder instance based on section config."""
        provider = config.get('provider', 'openai')
        model = config.get('model', 'text-embedding-3-small')
        dimensions = config.get('dimensions')

        if provider == 'openai':
            from agno.knowledge.embedder.openai import OpenAIEmbedder
            kwargs = {'id': model, 'api_key': api_key}
            if dimensions:
                kwargs['dimensions'] = dimensions
            return OpenAIEmbedder(**kwargs)
        elif provider == 'mistral':
            from agno.knowledge.embedder.mistral import MistralEmbedder
            kwargs = {'id': model, 'api_key': api_key}
            if dimensions:
                kwargs['dimensions'] = dimensions
            return MistralEmbedder(**kwargs)
        else:
            raise ValueError(f"Unsupported embedder provider: {provider}")

    def _get_api_key_from_secrets(self, secret_id: str) -> Optional[str]:
        """Fetch API key from secrets table."""
        from polysynergy_nodes.section.repositories.db_session import get_main_db_session
        from sqlalchemy import text

        with get_main_db_session() as db:
            sql = text("SELECT value FROM secrets WHERE id = :secret_id")
            result = db.execute(sql, {"secret_id": secret_id})
            row = result.fetchone()
            if row:
                return row.value
        return None

    async def provide_instance(self) -> VectorDb:
        """Create and return Section PgVector database instance."""

        # Validate section_id
        if not self.section_id:
            raise ValueError("Section ID is required")

        try:
            section_uuid = UUID(self.section_id)
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid section UUID: {str(e)}")

        # Fetch section information in thread (sync SQLAlchemy)
        def _sync_fetch_section():
            from polysynergy_nodes.section.repositories.db_session import get_main_db_session
            from polysynergy_nodes.section.repositories.node_section_repository import NodeSectionRepository

            with get_main_db_session() as db:
                section_repo = NodeSectionRepository(db)
                return section_repo.get_by_id(section_uuid)

        section_info = await asyncio.to_thread(_sync_fetch_section)

        print(f"[SectionPgVectorVectorDB] Section: {section_info['label']}")
        print(f"[SectionPgVectorVectorDB] Schema: {section_info['schema_name']}")

        # Check if vectorization is enabled
        vectorization_config = section_info.get('vectorization_config')
        if not vectorization_config or not vectorization_config.get('enabled'):
            raise ValueError(
                f"Section '{section_info['label']}' does not have vectorization enabled. "
                f"Please enable vectorization in the section configuration first."
            )

        print(f"[SectionPgVectorVectorDB] Vectorization: {vectorization_config.get('provider')} / {vectorization_config.get('model')}")

        # Get API key from secrets if configured
        api_key = None
        api_key_secret_id = vectorization_config.get('api_key_secret_id')
        if api_key_secret_id:
            api_key = await asyncio.to_thread(
                self._get_api_key_from_secrets,
                api_key_secret_id
            )

        # Create embedder from section config
        embedder_to_use = self._get_embedder_from_config(vectorization_config, api_key)
        print(f"[SectionPgVectorVectorDB] Using embedder from section config: {type(embedder_to_use).__name__}")

        # Convert enum strings to proper types
        search_type = SearchType[vectorization_config.get('search_type', 'hybrid')]
        distance = Distance[vectorization_config.get('distance', 'cosine')]

        # Get database URL
        database_url = section_info['database_url']

        print(f"[SectionPgVectorVectorDB] Creating SectionPgVector instance...")
        print(f"  - section_id: {self.section_id}")
        print(f"  - project_schema: {section_info['schema_name']}")
        print(f"  - search_type: {search_type}")
        print(f"  - distance: {distance}")

        # Create SectionPgVector instance
        from polysynergy_nodes.section.vectordb.section_pgvector import SectionPgVector

        self.vector_db_instance = SectionPgVector(
            section_id=self.section_id,
            project_schema=section_info['schema_name'],
            db_url=database_url,
            embedder=embedder_to_use,
            search_type=search_type,
            distance=distance,
        )

        print(f"[SectionPgVectorVectorDB] ✓ SectionPgVector instance created")

        return self.vector_db_instance
