"""High-level store management operations."""
from pathlib import Path
from typing import Dict, Any, List, Optional
from ...utils.logger import logger
from ...utils.constants import DEFAULT_STORE_PATH
from ..metadata.consolidator import MetadataConsolidator
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
    
    def add_document(self, file_path: Path, metadata: Dict[str, Any]) -> bool:
        """Add document to both metadata store and LightRAG."""
        try:
            # First save to metadata store
            doc_metadata = self.metadata_consolidator.consolidate_metadata(
                file_path=file_path,
                file_hash=metadata.get('file_hash', ''),
                identifier_info=metadata.get('identifier_info'),
                metadata=metadata.get('metadata'),
                references=metadata.get('references'),
                equations=metadata.get('equations'),
                errors=metadata.get('errors')
            )
            
            # Then add to LightRAG store
            store_success = self.lightrag_store.add_document(
                doc_metadata.model_dump()
            )
            
            return store_success
            
        except Exception as e:
            logger.error(f"Error adding document to store: {str(e)}")
            return False
    
    def remove_document(self, file_path: Path) -> bool:
        """Remove document from both stores."""
        try:
            # Remove from metadata store
            self.metadata_consolidator.remove_metadata(file_path)
            
            # Remove from LightRAG store
            store_success = self.lightrag_store.remove_document(str(file_path))
            
            return store_success
            
        except Exception as e:
            logger.error(f"Error removing document from store: {str(e)}")
            return False
    
    def search(
        self,
        query: str,
        mode: str = "hybrid",
        max_results: int = 5,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Search documents using LightRAG."""
        return self.lightrag_store.search(
            query=query,
            mode=mode,
            max_results=max_results,
            include_metadata=include_metadata
        )
    
    def get_document_metadata(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific document."""
        metadata = self.metadata_consolidator.get_metadata(file_path)
        if metadata:
            return metadata.model_dump()
        return None
    
    def get_all_metadata(self) -> Dict[str, Any]:
        """Get metadata for all documents."""
        return self.metadata_consolidator._load_metadata()
    
    def get_store_stats(self) -> Dict[str, Any]:
        """Get statistics about the store."""
        lightrag_stats = self.lightrag_store.get_stats()
        metadata_count = len(self.get_all_metadata())
        
        return {
            "document_count": metadata_count,
            "lightrag_stats": lightrag_stats
        } 