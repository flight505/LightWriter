"""Metadata models for academic documents."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SchemaVersion(BaseModel):
    """Track metadata schema version."""

    major: int = 1
    minor: int = 0
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


class Author(BaseModel):
    """Author model with name components."""

    model_config = ConfigDict(validate_assignment=True)

    full_name: str
    given: Optional[str] = None
    family: Optional[str] = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Author name cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    def parse_name_components(self) -> "Author":
        """Parse name components if not provided."""
        if not self.given and not self.family:
            parts = self.full_name.split(" ")
            if len(parts) > 1:
                self.family = parts[-1]
                self.given = " ".join(parts[:-1])
        return self


class Citation(BaseModel):
    """Citation model for tracking in-text citations."""

    model_config = ConfigDict(validate_assignment=True)

    text: str
    context: str
    citation_type: str = Field(default="numeric", description="Type of citation (numeric or author-year)")
    reference_id: str
    location: Dict[str, int]
    normalized_text: Optional[str] = None

    @field_validator("citation_type")
    @classmethod
    def validate_citation_type(cls, v: str) -> str:
        valid_types = {"numeric", "author-year"}
        if v not in valid_types:
            raise ValueError(f"Citation type must be one of {valid_types}")
        return v


class Reference(BaseModel):
    """Reference model with enhanced validation."""

    model_config = ConfigDict(validate_assignment=True)

    title: Optional[str] = None
    authors: List[Author] = Field(default_factory=list)
    year: Optional[int] = None
    raw_text: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    citations: List[Citation] = Field(default_factory=list)
    reference_id: str = Field(default="")

    @field_validator("doi")
    @classmethod
    def validate_doi(cls, v: Optional[str]) -> Optional[str]:
        if v:
            doi_pattern = r"10.\d{4,9}/[-._;()/:\w]+"
            if not re.match(doi_pattern, v):
                raise ValueError("Invalid DOI format")
        return v

    @field_validator("arxiv_id")
    @classmethod
    def validate_arxiv(cls, v: Optional[str]) -> Optional[str]:
        if v:
            arxiv_pattern = r"\d{4}\.\d{4,5}(v\d+)?"
            if not re.match(arxiv_pattern, v):
                raise ValueError("Invalid arXiv ID format")
        return v


class Symbol(BaseModel):
    """Mathematical symbol with context."""

    model_config = ConfigDict(validate_assignment=True)

    symbol: str
    type: str  # greek, operator, variable, etc.
    description: Optional[str] = None
    latex_command: Optional[str] = None


class Equation(BaseModel):
    """Enhanced equation model."""

    model_config = ConfigDict(validate_assignment=True)

    content: str
    context: Optional[str] = None
    symbols: List[Symbol] = Field(default_factory=list)
    equation_number: Optional[str] = None
    location: Dict[str, int] = Field(default_factory=dict)
    equation_type: str = Field(default="inline")  # inline, display, numbered
    latex_source: Optional[str] = None

    @field_validator("equation_type")
    @classmethod
    def validate_equation_type(cls, v: str) -> str:
        valid_types = {"inline", "display", "numbered"}
        if v not in valid_types:
            raise ValueError(f"Equation type must be one of {valid_types}")
        return v


class ProcessingMetadata(BaseModel):
    """Track processing details."""

    model_config = ConfigDict(validate_assignment=True)

    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    steps_completed: List[str] = Field(default_factory=list)
    extraction_methods: Dict[str, str] = Field(default_factory=dict)
    validation_results: Dict[str, bool] = Field(default_factory=dict)


class DocumentMetadata(BaseModel):
    """Enhanced document metadata model."""

    model_config = ConfigDict(validate_assignment=True)

    # Schema version
    schema_version: SchemaVersion = Field(default_factory=SchemaVersion)

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
    citations: List[Citation] = Field(default_factory=list)

    # Processing metadata
    processing: ProcessingMetadata = Field(default_factory=ProcessingMetadata)
    processing_status: str = "initialized"
    errors: List[str] = Field(default_factory=list)

    # Validation tracking
    validated: bool = False
    validation_errors: List[str] = Field(default_factory=list)

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: Optional[int]) -> Optional[int]:
        if v:
            current_year = datetime.now().year
            if not (1800 <= v <= current_year + 1):
                raise ValueError(f"Year must be between 1800 and {current_year + 1}")
        return v

    @model_validator(mode="after")
    def validate_references_citations(self) -> "DocumentMetadata":
        """Ensure citations match references."""
        # Build reference ID set
        ref_ids = {ref.reference_id for ref in self.references if ref.reference_id}

        # Validate citations
        for citation in self.citations:
            if citation.reference_id not in ref_ids:
                self.validation_errors.append(f"Citation references non-existent reference ID: {citation.reference_id}")

        return self

    def to_store_format(self) -> Dict[str, Any]:
        """Convert metadata to format suitable for store."""
        return {
            "schema_version": str(self.schema_version),
            "title": self.title,
            "authors": [author.full_name for author in self.authors],
            "abstract": self.abstract or "",
            "year": self.year,
            "references": [
                {
                    "title": ref.title,
                    "authors": [a.full_name for a in ref.authors],
                    "year": ref.year,
                    "doi": ref.doi,
                    "arxiv_id": ref.arxiv_id,
                }
                for ref in self.references
                if ref.title
            ],
            "equations": [
                {"content": eq.content, "type": eq.equation_type, "symbols": [s.symbol for s in eq.symbols]}
                for eq in self.equations
            ],
            "citations": [
                {"text": cit.text, "reference_id": cit.reference_id, "type": cit.citation_type}
                for cit in self.citations
            ],
            "processing_status": self.processing_status,
            "validated": self.validated,
            "metadata": self.model_dump(),
        }
