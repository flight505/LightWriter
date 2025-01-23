"""LightRAG store implementation for document management."""

import asyncio
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

from sentence_transformers import SentenceTransformer

from ...utils.constants import (
    DEFAULT_EMBEDDING_DIM,
    DEFAULT_STORE_PATH,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
)
from ...utils.logger import logger
from ..metadata.models import DocumentMetadata


def create_embedding_function(model: SentenceTransformer) -> Callable:
    """Create an embedding function with the correct attributes."""

    @wraps(model.encode)
    def embedding_func(text: str) -> Any:
        return model.encode(text)

    # Add required attributes
    embedding_func.embedding_dim = model.get_sentence_embedding_dimension()
    return embedding_func


class LightRAGStore:
    """Manage document storage and retrieval using LightRAG."""

    def __init__(
        self,
        store_path: Path = DEFAULT_STORE_PATH,
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
        llm_model_func: Optional[Any] = None,
        embedding_func: Optional[Any] = None,
    ):
        """Initialize LightRAG store."""
        self.store_path = store_path / "lightrag"
        self.store_path.mkdir(parents=True, exist_ok=True)

        # Create store subdirectories
        (self.store_path / "documents").mkdir(exist_ok=True)
        (self.store_path / "vectors").mkdir(exist_ok=True)
        (self.store_path / "metadata").mkdir(exist_ok=True)

        # Initialize embedding model if not provided
        if embedding_func is None:
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            embedding_func = create_embedding_function(self.embedding_model)

        self.embedding_func = embedding_func
        self.embedding_dim = embedding_dim
        self.llm_model_func = llm_model_func

    async def add_document_async(self, metadata: Union[Dict[str, Any], DocumentMetadata]) -> bool:
        """Add document to store using metadata asynchronously."""
        try:
            # Convert metadata to store format if needed
            if isinstance(metadata, DocumentMetadata):
                store_data = await self._prepare_store_data_async(metadata)
            else:
                # If it's already a dict, assume it's in the correct format
                store_data = await self._prepare_store_data_async(DocumentMetadata.model_validate(metadata))

            # Save document content
            doc_path = self.store_path / "documents" / f"{store_data['id']}.txt"
            async with asyncio.Lock():
                with open(doc_path, "w", encoding="utf-8") as f:
                    f.write(store_data["text"])

            # Generate and save embeddings
            embeddings = await asyncio.to_thread(self.embedding_func, [store_data["text"]])
            vec_path = self.store_path / "vectors" / f"{store_data['id']}.npy"
            async with asyncio.Lock():
                with open(vec_path, "wb") as f:
                    embeddings.tofile(f)

            # Save metadata
            meta_path = self.store_path / "metadata" / f"{store_data['id']}.json"
            async with asyncio.Lock():
                with open(meta_path, "w", encoding="utf-8") as f:
                    f.write(store_data["metadata"])

            logger.info(SUCCESS_MESSAGES["store_update"])
            return True

        except Exception as e:
            logger.error(ERROR_MESSAGES["store_error"].format(error=str(e)))
            return False

    def add_document(self, metadata: Union[Dict[str, Any], DocumentMetadata]) -> bool:
        """Synchronous wrapper for adding document."""
        return asyncio.run(self.add_document_async(metadata))

    async def remove_document_async(self, file_path: str) -> bool:
        """Remove document from store asynchronously."""
        try:
            doc_id = Path(file_path).stem
            paths = [
                self.store_path / "documents" / f"{doc_id}.txt",
                self.store_path / "vectors" / f"{doc_id}.npy",
                self.store_path / "metadata" / f"{doc_id}.json",
            ]

            for path in paths:
                if path.exists():
                    path.unlink()

            logger.info(f"✓ Document removed from store: {file_path}")
            return True

        except Exception as e:
            logger.error(ERROR_MESSAGES["store_error"].format(error=str(e)))
            return False

    def remove_document(self, file_path: str) -> bool:
        """Synchronous wrapper for removing document."""
        return asyncio.run(self.remove_document_async(file_path))

    async def search_async(
        self, query: str, mode: str = "hybrid", max_results: int = 5, include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Search store with query asynchronously."""
        try:
            # Generate query embedding
            query_embedding = await asyncio.to_thread(self.embedding_func, [query])

            # TODO: Implement actual search logic
            # For now, return empty results
            return {"matches": [], "metadata": {} if include_metadata else None}

        except Exception as e:
            logger.error(ERROR_MESSAGES["store_error"].format(error=str(e)))
            return {}

    def search(
        self, query: str, mode: str = "hybrid", max_results: int = 5, include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Synchronous wrapper for search."""
        return asyncio.run(
            self.search_async(query=query, mode=mode, max_results=max_results, include_metadata=include_metadata)
        )

    async def get_stats_async(self) -> Dict[str, Any]:
        """Get store statistics asynchronously."""
        try:
            doc_count = len(list((self.store_path / "documents").glob("*.txt")))
            return {"document_count": doc_count, "store_path": str(self.store_path)}
        except Exception as e:
            logger.error(ERROR_MESSAGES["store_error"].format(error=str(e)))
            return {}

    def get_stats(self) -> Dict[str, Any]:
        """Synchronous wrapper for getting stats."""
        return asyncio.run(self.get_stats_async())

    async def _prepare_store_data_async(self, metadata: DocumentMetadata) -> Dict[str, Any]:
        """Prepare metadata for store insertion asynchronously."""
        # Combine relevant fields for text content
        content_parts = [
            metadata.title,
            metadata.abstract or "",
            # References
            "\n".join(ref.title or ref.raw_text or "" for ref in metadata.references),
            # Equations with context
            "\n".join(f"{eq.content} - {eq.context or ''}" for eq in metadata.equations),
            # Citations with context
            "\n".join(f"{cit.text} - {cit.context or ''}" for cit in metadata.citations),
        ]

        # Join with newlines and add metadata
        return {
            "id": metadata.file_hash,
            "text": "\n\n".join(part.strip() for part in content_parts if part.strip()),
            "metadata": metadata.model_dump_json(),
        }

    def _prepare_store_data(self, metadata: DocumentMetadata) -> Dict[str, Any]:
        """Synchronous wrapper for preparing store data."""
        return asyncio.run(self._prepare_store_data_async(metadata))
