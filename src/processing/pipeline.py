"""Processing pipeline for document extraction."""

import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

from ..core.extractors.citation_extractor import CitationExtractor
from ..core.extractors.equation_extractor import EquationExtractor
from ..core.extractors.identifier_extractor import IdentifierExtractor
from ..core.extractors.pdf_extractor import PDFExtractor
from ..core.extractors.reference_extractor import ReferenceExtractor
from ..core.metadata.models import Author, Citation, DocumentMetadata, Equation, ProcessingMetadata, Reference
from ..core.store.manager import StoreManager
from ..utils.constants import ProcessingState
from ..utils.logger import logger


class ExtractionResult(NamedTuple):
    """Result of content extraction step."""

    text: str
    markdown: str
    file_hash: str
    success: bool
    error: Optional[str] = None

class MetadataResult(NamedTuple):
    """Result of metadata extraction and processing."""

    title: str
    authors: List[Author]
    year: Optional[int]
    identifier: Optional[str] = None
    identifier_type: Optional[str] = None
    abstract: Optional[str] = None
    extraction_method: str = "filename"


class ProcessingPipeline:
    """Coordinate document processing steps."""

    def __init__(self, store_manager: Optional[StoreManager] = None):
        """Initialize pipeline with extractors."""
        self.pdf_extractor = PDFExtractor()
        self.identifier_extractor = IdentifierExtractor()
        self.reference_extractor = ReferenceExtractor()
        self.equation_extractor = EquationExtractor()
        self.citation_extractor = CitationExtractor()
        self.store_manager = store_manager or StoreManager()

    def _extract_metadata_from_filename(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from filename.
        Expected format: Author et al. - YYYY - Title-annotated.pdf
        """
        filename = file_path.stem
        # Remove -annotated suffix if present
        filename = re.sub(r"-annotated$", "", filename)

        # Split on ' - ' but keep the delimiters
        parts = [p.strip() for p in filename.split(" - ")]
        if len(parts) >= 3:
            authors_str, year_str, *title_parts = parts
            title = " - ".join(title_parts)

            # Parse authors
            authors = []
            if " et al." in authors_str:
                # Single author with et al.
                author = authors_str.replace(" et al.", "")
                authors.append(Author(full_name=author))
            else:
                # Multiple authors separated by ' and ' or ', '
                author_list = re.split(r",\s*|\s+and\s+", authors_str)
                authors.extend(Author(full_name=a.strip()) for a in author_list if a.strip())

            # Parse year
            try:
                year = int(year_str)
            except ValueError:
                year = None

            # Log extracted metadata for debugging
            logger.info("Extracted metadata from filename:")
            logger.info(f"  Title: {title}")
            logger.info(f"  Authors: {[a.full_name for a in authors]}")
            logger.info(f"  Year: {year}")

            return {"title": title, "authors": authors, "year": year}

        # Fallback: use filename as title
        logger.warning(f"Could not parse metadata from filename: {filename}")
        return {"title": filename, "authors": [Author(full_name="Unknown Author")], "year": None}

    async def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process document through extraction pipeline."""
        try:
            logger.info(f"Processing document: {file_path}")
            processing = self._initialize_processing()
            state = ProcessingState.INITIALIZED
            errors = []

            # Step 1: Extract content
            state = ProcessingState.EXTRACTING_TEXT
            content = await self._extract_content(file_path)
            if not content.success:
                errors.append(content.error or "Text extraction failed")
                return self._create_result(state, errors)
            processing.steps_completed.append("text_extraction")

            # Step 2: Process metadata
            state = ProcessingState.EXTRACTING_IDENTIFIER
            metadata = await self._process_metadata(file_path, content.text)
            processing.steps_completed.append("identifier_extraction")
            processing.extraction_methods["identifier"] = metadata.extraction_method

            # Step 3: Process academic content
            state = ProcessingState.PROCESSING_CONTENT
            academic_content = await self._process_academic_content(
                content.text, metadata.identifier, metadata.identifier_type
            )
            processing.steps_completed.extend(["reference_extraction", "equation_extraction", "citation_extraction"])

            # Step 4: Validate and store
            state = ProcessingState.VALIDATING
            result = await self._validate_and_store(
                file_path=file_path,
                content=content,
                metadata=metadata,
                academic_content=academic_content,
                processing=processing,
            )

            return result

        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return self._create_result(ProcessingState.FAILED, [str(e)])

    def _initialize_processing(self) -> ProcessingMetadata:
        """Initialize processing metadata."""
        return ProcessingMetadata(
            started_at=datetime.now(),
            steps_completed=[],
            validation_results={"basic_metadata": True, "references": True, "equations": True, "citations": True},
        )

    async def _extract_content(self, file_path: Path) -> ExtractionResult:
        """Extract text content from document."""
        try:
            extraction_results = await asyncio.to_thread(self.pdf_extractor.extract_all, file_path)

            text = extraction_results.get("text")
            markdown = extraction_results.get("markdown")

            if not text or not markdown:
                return ExtractionResult("", "", "", False, "Failed to extract text content")

            return ExtractionResult(
                text=text, markdown=markdown, file_hash=extraction_results["file_hash"], success=True
            )

        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            return ExtractionResult("", "", "", False, str(e))

    async def _process_metadata(self, file_path: Path, text: str) -> MetadataResult:
        """Process and merge metadata from filename and identifiers."""
        # Get metadata from filename
        filename_meta = self._extract_metadata_from_filename(file_path)

        # Try to get metadata from identifiers
        identifier_info = await asyncio.to_thread(self.identifier_extractor.extract_identifier, file_path) or {}

        # Merge metadata, preferring identifier info
        return MetadataResult(
            title=identifier_info.get("title") or filename_meta["title"],
            authors=identifier_info.get("authors") or filename_meta["authors"],
            year=identifier_info.get("year") or filename_meta["year"],
            identifier=identifier_info.get("identifier"),
            identifier_type=identifier_info.get("identifier_type"),
            abstract=identifier_info.get("abstract"),
            extraction_method=identifier_info.get("method", "filename"),
        )

    async def _process_academic_content(
        self, text: str, identifier: Optional[str], identifier_type: Optional[str]
    ) -> Dict[str, Any]:
        """Process academic content (references, equations, citations)."""
        # Extract and process references
        references = await self._process_references(text, identifier, identifier_type)

        # Extract equations and get clean text
        equations, clean_text = await self._process_equations(text)

        # Extract citations from clean text
        citations = await self._process_citations(clean_text)

        return {"references": references, "equations": equations, "citations": citations}

    async def _process_references(
        self, text: str, identifier: Optional[str], identifier_type: Optional[str]
    ) -> List[Reference]:
        """Process references with proper ID assignment."""
        raw_references = await asyncio.to_thread(
            self.reference_extractor.extract_references,
            identifier=identifier,
            identifier_type=identifier_type,
            text=text,
        )

        references = []
        for i, ref in enumerate(raw_references, 1):
            ref_id = f"ref_{i}"
            if isinstance(ref, dict):
                ref["reference_id"] = ref_id
                if not ref.get("title"):
                    ref["raw_text"] = ref.get("raw_text", f"Reference {i}")
                references.append(Reference.model_validate(ref))
            elif hasattr(ref, "model_dump"):
                ref.reference_id = ref_id
                if not ref.title:
                    ref.raw_text = ref.raw_text or f"Reference {i}"
                references.append(ref)

        return references

    async def _validate_and_store(
        self,
        file_path: Path,
        content: ExtractionResult,
        metadata: MetadataResult,
        academic_content: Dict[str, Any],
        processing: ProcessingMetadata,
    ) -> Dict[str, Any]:
        """Validate and store processed document."""
        # Validate basic metadata
        has_basic_metadata = bool(metadata.title and metadata.authors)
        processing.validation_results["basic_metadata"] = has_basic_metadata

        # Create document metadata
        doc_metadata = DocumentMetadata(
            file_path=str(file_path),
            file_hash=content.file_hash,
            identifier=metadata.identifier,
            identifier_type=metadata.identifier_type,
            title=metadata.title,
            authors=metadata.authors,
            abstract=metadata.abstract,
            year=metadata.year,
            references=academic_content["references"],
            equations=academic_content["equations"],
            citations=academic_content["citations"],
            processing=processing,
            processing_status=ProcessingState.VALIDATING.value,
            validated=has_basic_metadata,
            validation_errors=[] if has_basic_metadata else ["basic_metadata validation failed"],
        )

        # Store metadata
        store_success = await self.store_manager.add_document_async(
            file_path=file_path, metadata=doc_metadata.model_dump()
        )

        # Update final state
        if store_success:
            state = ProcessingState.COMPLETED if has_basic_metadata else ProcessingState.VALIDATION_FAILED

            # Update metadata with final state
            doc_metadata.processing_status = state.value
            doc_metadata.processing.completed_at = datetime.now()
            doc_metadata.processing.duration = (
                doc_metadata.processing.completed_at - doc_metadata.processing.started_at
            ).total_seconds()

            # Store updated metadata
            await self.store_manager.add_document_async(file_path=file_path, metadata=doc_metadata.model_dump())

            return self._create_result(state, [])

        return self._create_result(ProcessingState.FAILED, ["Store update failed"])

    def process_document_sync(self, file_path: Path) -> Dict[str, Any]:
        """Synchronous wrapper for document processing."""
        return asyncio.run(self.process_document(file_path))

    def _create_result(self, state: ProcessingState, errors: list) -> Dict[str, Any]:
        """Create standardized result dictionary."""
        return {"state": state.value, "success": state == ProcessingState.COMPLETED, "errors": errors}

    async def _process_equations(self, text: str) -> Tuple[List[Equation], str]:
        """Extract equations and return clean text."""
        # Extract equations
        equations = self.equation_extractor.extract_equations(text)

        # Remove equation content from text to avoid interference with citations
        clean_text = text
        for eq in sorted(equations, key=lambda x: x.location["start"], reverse=True):
            start = eq.location["start"]
            end = eq.location["end"]
            # Replace equation with placeholder to maintain text positions
            clean_text = clean_text[:start] + " " * (end - start) + clean_text[end:]

        return equations, clean_text

    async def _process_citations(self, text: str) -> List[Citation]:
        """Extract and filter citations from clean text."""
        citations = self.citation_extractor.extract_citations(text)

        # Filter out potential years
        filtered_citations = []
        for citation in citations:
            if citation.citation_type == "numeric":
                # Check if citation numbers are valid (not years)
                numbers = [
                    num.strip()
                    for num in citation.normalized_text.split(",")
                    if len(num.strip()) <= 3  # Exclude 4-digit numbers (years)
                ]
                if numbers:
                    citation.normalized_text = ",".join(numbers)
                    filtered_citations.append(citation)
            else:
                filtered_citations.append(citation)

        return filtered_citations
