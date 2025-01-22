"""LightRAG store implementation for document management."""
from pathlib import Path
from typing import Dict, Any, List, Optional
from lightrag import LightRAG, QueryParam
from ...utils.logger import logger
from ...utils.constants import (
    DEFAULT_STORE_PATH, DEFAULT_EMBEDDING_DIM, MAX_TOKEN_SIZE,
    DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP, SUCCESS_MESSAGES, ERROR_MESSAGES
)

class LightRAGStore:
    """Manage document storage and retrieval using LightRAG."""
    
    def __init__(
        self,
        store_path: Path = DEFAULT_STORE_PATH,
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
        llm_model_func: Optional[Any] = None,
        embedding_func: Optional[Any] = None
    ):
        """Initialize LightRAG store."""
        self.store_path = store_path / "lightrag"
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize LightRAG with configuration
        self.rag = LightRAG(
            working_dir=str(self.store_path),
            llm_model_func=llm_model_func,
            embedding_func=embedding_func
        )
    
    def add_document(self, metadata: Dict[str, Any]) -> bool:
        """Add document to store using metadata."""
        try:
            # Convert metadata to store format
            store_data = self._prepare_store_data(metadata)
            
            # Insert into LightRAG
            self.rag.insert(store_data)
            
            logger.info(SUCCESS_MESSAGES["store_update"])
            return True
            
        except Exception as e:
            logger.error(ERROR_MESSAGES["store_error"].format(error=str(e)))
            return False
    
    def remove_document(self, file_path: str) -> bool:
        """Remove document from store."""
        try:
            # LightRAG doesn't have direct removal, so we need to rebuild
            # TODO: Implement more efficient removal
            self.rag.delete_by_entity(file_path)
            
            logger.info(f"✓ Document removed from store: {file_path}")
            return True
            
        except Exception as e:
            logger.error(ERROR_MESSAGES["store_error"].format(error=str(e)))
            return False
    
    def search(
        self,
        query: str,
        mode: str = "hybrid",
        max_results: int = 5,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Search store with query."""
        try:
            # Configure search parameters
            param = QueryParam(
                mode=mode,
                chunk_size=DEFAULT_CHUNK_SIZE,
                chunk_overlap=DEFAULT_OVERLAP
            )
            
            # Perform search
            results = self.rag.query(
                query,
                param=param,
                only_need_context=not include_metadata
            )
            
            return results
            
        except Exception as e:
            logger.error(ERROR_MESSAGES["store_error"].format(error=str(e)))
            return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        try:
            return self.rag.get_stats()
        except Exception as e:
            logger.error(ERROR_MESSAGES["store_error"].format(error=str(e)))
            return {}
    
    def _prepare_store_data(self, metadata: Dict[str, Any]) -> str:
        """Prepare metadata for store insertion."""
        # Combine relevant fields for text content
        content_parts = [
            metadata.get('title', ''),
            metadata.get('abstract', ''),
            '\n'.join(ref.get('title', '') for ref in metadata.get('references', [])),
            '\n'.join(eq.get('content', '') for eq in metadata.get('equations', []))
        ]
        
        # Join with newlines and add metadata
        return {
            'text': '\n\n'.join(part for part in content_parts if part),
            'metadata': metadata
        } 