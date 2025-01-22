"""Consolidate metadata from various extractors."""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from ...utils.logger import logger
from ...utils.constants import DEFAULT_STORE_PATH
from .models import DocumentMetadata, Author

class MetadataConsolidator:
    """Consolidate and manage document metadata."""
    
    def __init__(self, store_path: Path = DEFAULT_STORE_PATH):
        """Initialize consolidator with store path."""
        self.store_path = store_path
        self.metadata_path = store_path / "metadata.json"
        self._ensure_metadata_file()
    
    def _ensure_metadata_file(self):
        """Ensure metadata file exists."""
        self.store_path.mkdir(parents=True, exist_ok=True)
        if not self.metadata_path.exists():
            self.metadata_path.write_text("{}", encoding="utf-8")
    
    def consolidate_metadata(
        self,
        file_path: Path,
        file_hash: str,
        identifier_info: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        references: Optional[list] = None,
        equations: Optional[list] = None,
        errors: Optional[list] = None
    ) -> DocumentMetadata:
        """Consolidate metadata from various sources."""
        try:
            # Create base metadata
            doc_metadata = DocumentMetadata(
                file_path=str(file_path),
                file_hash=file_hash,
                title=metadata.get("title", "") if metadata else "",
                authors=[Author(**author) if isinstance(author, dict) else Author(full_name=author)
                        for author in (metadata.get("authors", []) if metadata else [])],
                abstract=metadata.get("abstract", "") if metadata else None,
                year=metadata.get("year") if metadata else None,
                references=references or [],
                equations=equations or [],
                errors=errors or []
            )
            
            # Add identifier information if available
            if identifier_info:
                doc_metadata.identifier = identifier_info.get("identifier")
                doc_metadata.identifier_type = identifier_info.get("identifier_type")
                doc_metadata.extraction_method = identifier_info.get("method")
            
            # Save consolidated metadata
            self._save_metadata(doc_metadata)
            
            return doc_metadata
            
        except Exception as e:
            logger.error(f"Error consolidating metadata: {str(e)}")
            raise
    
    def _save_metadata(self, metadata: DocumentMetadata):
        """Save metadata to JSON store."""
        try:
            # Load existing metadata
            current_metadata = self._load_metadata()
            
            # Update with new metadata
            current_metadata[str(metadata.file_path)] = metadata.model_dump()
            
            # Save back to file
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(current_metadata, f, indent=2, ensure_ascii=False)
                
            logger.info(f"✓ Metadata saved for {metadata.file_path}")
            
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")
            raise
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from JSON store."""
        try:
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata: {str(e)}")
            return {}
    
    def get_metadata(self, file_path: Path) -> Optional[DocumentMetadata]:
        """Get metadata for a specific file."""
        metadata_dict = self._load_metadata().get(str(file_path))
        if metadata_dict:
            return DocumentMetadata(**metadata_dict)
        return None
    
    def remove_metadata(self, file_path: Path):
        """Remove metadata for a specific file."""
        try:
            current_metadata = self._load_metadata()
            if str(file_path) in current_metadata:
                del current_metadata[str(file_path)]
                with open(self.metadata_path, "w", encoding="utf-8") as f:
                    json.dump(current_metadata, f, indent=2, ensure_ascii=False)
                logger.info(f"✓ Metadata removed for {file_path}")
        except Exception as e:
            logger.error(f"Error removing metadata: {str(e)}")
            raise 