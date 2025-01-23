"""High-level store management operations."""
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

from ...utils.constants import DEFAULT_STORE_PATH
from ...utils.logger import logger
from ..metadata.consolidator import MetadataConsolidator
from ..metadata.models import DocumentMetadata
from .lightrag import LightRAGStore


class StoreManager:
    """Manage document storage and metadata operations."""

    def __init__(
        self,
        store_path: Path = DEFAULT_STORE_PATH,
        llm_model_func: Optional[Any] = None,
        embedding_func: Optional[Any] = None
    ):
        """Initialize store manager."""
        self.store_path = store_path
        self.metadata_consolidator = MetadataConsolidator(store_path)
        self.lightrag_store = LightRAGStore(
            store_path=store_path,
            llm_model_func=llm_model_func,
            embedding_func=embedding_func
        )

    async def add_document_async(
        self,
        file_path: Path,
        metadata: Dict[str, Any]
    ) -> bool:
        """Add document to both metadata store and LightRAG asynchronously."""
        try:
            # First save to metadata store
            doc_metadata = await self.metadata_consolidator.consolidate_metadata_async(
                file_path=file_path,
                file_hash=metadata.get('file_hash', ''),
                identifier_info=metadata.get('identifier_info'),
                metadata=metadata.get('metadata'),
                references=metadata.get('references'),
                equations=metadata.get('equations'),
                citations=metadata.get('citations'),
                errors=metadata.get('errors')
            )

            # Then add to LightRAG store
            store_success = await asyncio.to_thread(
                self.lightrag_store.add_document,
                doc_metadata.model_dump()
            )

            return store_success

        except Exception as e:
            logger.error(f"Error adding document to store: {str(e)}")
            return False

    def add_document(self, file_path: Path, metadata: Dict[str, Any]) -> bool:
        """Synchronous wrapper for adding document."""
        return asyncio.run(self.add_document_async(file_path, metadata))

    async def remove_document_async(self, file_path: Path) -> bool:
        """Remove document from both stores asynchronously."""
        try:
            # Remove from metadata store
            await asyncio.to_thread(
                self.metadata_consolidator.remove_metadata,
                file_path
            )

            # Remove from LightRAG store
            store_success = await asyncio.to_thread(
                self.lightrag_store.remove_document,
                str(file_path)
            )

            return store_success

        except Exception as e:
            logger.error(f"Error removing document from store: {str(e)}")
            return False

    def remove_document(self, file_path: Path) -> bool:
        """Synchronous wrapper for removing document."""
        return asyncio.run(self.remove_document_async(file_path))

    async def search_async(
        self,
        query: str,
        mode: str = "hybrid",
        max_results: int = 5,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Search documents using LightRAG asynchronously."""
        return await asyncio.to_thread(
            self.lightrag_store.search,
            query=query,
            mode=mode,
            max_results=max_results,
            include_metadata=include_metadata
        )

    def search(
        self,
        query: str,
        mode: str = "hybrid",
        max_results: int = 5,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Synchronous wrapper for search."""
        return asyncio.run(self.search_async(
            query=query,
            mode=mode,
            max_results=max_results,
            include_metadata=include_metadata
        ))

    async def get_document_metadata_async(
        self,
        file_path: Path
    ) -> Optional[DocumentMetadata]:
        """Get metadata for a specific document asynchronously."""
        metadata = await asyncio.to_thread(
            self.metadata_consolidator.get_metadata,
            file_path
        )
        return metadata

    def get_document_metadata(
        self,
        file_path: Path
    ) -> Optional[DocumentMetadata]:
        """Synchronous wrapper for getting document metadata."""
        return asyncio.run(self.get_document_metadata_async(file_path))

    async def get_all_metadata_async(self) -> Dict[str, Any]:
        """Get metadata for all documents asynchronously."""
        return await asyncio.to_thread(
            self.metadata_consolidator._load_metadata
        )

    def get_all_metadata(self) -> Dict[str, Any]:
        """Synchronous wrapper for getting all metadata."""
        return asyncio.run(self.get_all_metadata_async())

    async def get_store_stats_async(self) -> Dict[str, Any]:
        """Get statistics about the store asynchronously."""
        lightrag_stats = await asyncio.to_thread(
            self.lightrag_store.get_stats
        )
        metadata = await self.get_all_metadata_async()
        metadata_count = len(metadata.get("documents", {}))

        return {
            "document_count": metadata_count,
            "lightrag_stats": lightrag_stats
        }

    def get_store_stats(self) -> Dict[str, Any]:
        """Synchronous wrapper for getting store stats."""
        return asyncio.run(self.get_store_stats_async())
