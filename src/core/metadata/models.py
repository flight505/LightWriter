"""Metadata models for academic documents."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class Author(BaseModel):
    """Author model with name components."""
    full_name: str
    given: Optional[str] = None
    family: Optional[str] = None

class Reference(BaseModel):
    """Reference model for bibliography entries."""
    title: Optional[str] = None
    authors: List[Author] = Field(default_factory=list)
    year: Optional[int] = None
    raw_text: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None

class Equation(BaseModel):
    """Equation model with context."""
    content: str
    context: Optional[str] = None
    symbols: List[str] = Field(default_factory=list)
    equation_number: Optional[str] = None
    location: Dict[str, int] = Field(default_factory=dict)

class DocumentMetadata(BaseModel):
    """Complete document metadata model."""
    # Document identification
    file_path: str
    file_hash: str
    identifier: Optional[str] = None
    identifier_type: Optional[str] = None
    
    # Basic metadata
    title: str
    authors: List[Author]
    abstract: Optional[str] = None
    year: Optional[int] = None
    
    # Content metadata
    references: List[Reference] = Field(default_factory=list)
    equations: List[Equation] = Field(default_factory=list)
    
    # Processing metadata
    processed_at: datetime = Field(default_factory=datetime.now)
    extraction_method: Optional[str] = None
    processing_status: str = "completed"
    errors: List[str] = Field(default_factory=list)
    
    def to_store_format(self) -> Dict[str, Any]:
        """Convert metadata to format suitable for store."""
        return {
            "title": self.title,
            "authors": [author.full_name for author in self.authors],
            "abstract": self.abstract or "",
            "year": self.year,
            "references": [ref.title for ref in self.references if ref.title],
            "equations": [eq.content for eq in self.equations],
            "metadata": self.model_dump()
        } 