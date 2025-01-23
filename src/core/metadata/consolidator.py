"""Consolidate metadata from various extractors with enhanced validation."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import aiofiles

from ...utils.constants import DEFAULT_STORE_PATH, ProcessingState
from ...utils.logger import logger
from .models import Author, Citation, DocumentMetadata, Equation, ProcessingMetadata, Reference, SchemaVersion, Symbol


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


class MetadataConsolidator:
    """Enhanced metadata consolidator with validation."""

    def __init__(self, store_path: Path = DEFAULT_STORE_PATH):
        """Initialize consolidator with store path."""
        self.store_path = store_path
        self.metadata_path = store_path / "metadata.json"
        self.schema_version = SchemaVersion()
        self._ensure_metadata_file()

    def _ensure_metadata_file(self):
        """Ensure metadata file exists with version."""
        self.store_path.mkdir(parents=True, exist_ok=True)
        if not self.metadata_path.exists():
            initial_data = {"schema_version": str(self.schema_version), "documents": {}}
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
        else:
            # Load and validate existing metadata
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "documents" not in data:
                    data["documents"] = {}
                    with open(self.metadata_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
            except Exception as e:
                logger.error(f"Error validating metadata file: {str(e)}")
                # Create new metadata file
                initial_data = {"schema_version": str(self.schema_version), "documents": {}}
                with open(self.metadata_path, "w", encoding="utf-8") as f:
                    json.dump(initial_data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)

    async def consolidate_metadata_async(
        self,
        file_path: Path,
        file_hash: str,
        identifier_info: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        references: Optional[list] = None,
        equations: Optional[list] = None,
        citations: Optional[list] = None,
        errors: Optional[list] = None,
    ) -> DocumentMetadata:
        """Asynchronously consolidate and validate metadata."""
        try:
            # Start processing metadata
            processing = ProcessingMetadata(started_at=datetime.now(), steps_completed=[], extraction_methods={})

            # Create base metadata
            doc_metadata = DocumentMetadata(
                schema_version=self.schema_version,
                file_path=str(file_path),
                file_hash=file_hash,
                title=metadata.get("title", "") if metadata else "",
                authors=[
                    Author(**author) if isinstance(author, dict) else Author(full_name=author)
                    for author in (metadata.get("authors", []) if metadata else [])
                ],
                abstract=metadata.get("abstract", "") if metadata else None,
                year=metadata.get("year") if metadata else None,
                processing=processing,
                processing_status=ProcessingState.PROCESSING.value,
            )

            # Process components in parallel
            await asyncio.gather(
                self._process_identifier(doc_metadata, identifier_info),
                self._process_references(doc_metadata, references),
                self._process_equations(doc_metadata, equations),
                self._process_citations(doc_metadata, citations),
            )

            # Validate consolidated metadata
            validation_results = await self._validate_metadata(doc_metadata)
            doc_metadata.validated = all(validation_results.values())
            if not doc_metadata.validated:
                doc_metadata.validation_errors.extend(
                    f"{key} validation failed" for key, valid in validation_results.items() if not valid
                )

            # Update processing metadata
            doc_metadata.processing.completed_at = datetime.now()
            doc_metadata.processing.duration = (
                doc_metadata.processing.completed_at - doc_metadata.processing.started_at
            ).total_seconds()

            # Set final status
            doc_metadata.processing_status = (
                ProcessingState.COMPLETED.value if doc_metadata.validated else ProcessingState.VALIDATION_FAILED.value
            )

            # Save consolidated metadata
            await self._save_metadata_async(doc_metadata)

            return doc_metadata

        except Exception as e:
            logger.error(f"Error consolidating metadata: {str(e)}")
            raise

    def consolidate_metadata(
        self,
        file_path: Path,
        file_hash: str,
        identifier_info: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        references: Optional[list] = None,
        equations: Optional[list] = None,
        citations: Optional[list] = None,
        errors: Optional[list] = None,
    ) -> DocumentMetadata:
        """Synchronous wrapper for metadata consolidation."""
        return asyncio.run(
            self.consolidate_metadata_async(
                file_path=file_path,
                file_hash=file_hash,
                identifier_info=identifier_info,
                metadata=metadata,
                references=references,
                equations=equations,
                citations=citations,
                errors=errors,
            )
        )

    async def _process_identifier(self, metadata: DocumentMetadata, identifier_info: Optional[Dict[str, Any]]):
        """Process identifier information."""
        if identifier_info:
            metadata.identifier = identifier_info.get("identifier")
            metadata.identifier_type = identifier_info.get("identifier_type")
            metadata.processing.extraction_methods["identifier"] = identifier_info.get("method", "unknown")
            metadata.processing.steps_completed.append("identifier_extraction")

    async def _process_references(self, metadata: DocumentMetadata, references: Optional[list]):
        """Process and validate references."""
        if references:
            processed_refs = []
            for ref in references:
                if isinstance(ref, dict):
                    # Generate reference ID if not present
                    if "reference_id" not in ref:
                        ref["reference_id"] = f"ref_{len(processed_refs) + 1}"
                    processed_refs.append(Reference.model_validate(ref))
                elif hasattr(ref, "model_dump"):  # Handle existing Reference objects
                    processed_refs.append(ref)
            metadata.references = processed_refs
            metadata.processing.steps_completed.append("reference_extraction")

    async def _process_equations(self, metadata: DocumentMetadata, equations: Optional[list]):
        """Process and validate equations."""
        if equations:
            processed_eqs = []
            for eq in equations:
                if isinstance(eq, dict):
                    # Process symbols if present
                    if "symbols" in eq and isinstance(eq["symbols"], list):
                        eq["symbols"] = [
                            Symbol.model_validate(sym) if isinstance(sym, dict) else Symbol(symbol=sym)
                            for sym in eq["symbols"]
                        ]
                    processed_eqs.append(Equation.model_validate(eq))
                elif hasattr(eq, "model_dump"):  # Handle existing Equation objects
                    processed_eqs.append(eq)
            metadata.equations = processed_eqs
            metadata.processing.steps_completed.append("equation_extraction")

    async def _process_citations(self, metadata: DocumentMetadata, citations: Optional[list]):
        """Process and validate citations."""
        if citations:
            processed_cits = []
            for cit in citations:
                if isinstance(cit, dict):
                    processed_cits.append(Citation.model_validate(cit))
                elif hasattr(cit, "model_dump"):  # Handle existing Citation objects
                    processed_cits.append(cit)
            metadata.citations = processed_cits
            metadata.processing.steps_completed.append("citation_extraction")

    async def _validate_metadata(self, metadata: DocumentMetadata) -> Dict[str, bool]:
        """Validate metadata components."""
        validation_results = {
            "basic_metadata": await self._validate_basic_metadata(metadata),
            "references": await self._validate_references(metadata),
            "equations": await self._validate_equations(metadata),
            "citations": await self._validate_citations(metadata),
        }
        metadata.processing.validation_results = validation_results
        return validation_results

    async def _validate_basic_metadata(self, metadata: DocumentMetadata) -> bool:
        """Validate basic metadata fields."""
        return all([metadata.file_path, metadata.file_hash, metadata.title, len(metadata.authors) > 0])

    async def _validate_references(self, metadata: DocumentMetadata) -> bool:
        """Validate references."""
        if not metadata.references:
            return True

        return all(
            ref.title
            or ref.raw_text  # Must have either title or raw text
            and len(ref.authors) > 0  # Must have at least one author
            and ref.reference_id  # Must have reference ID
            for ref in metadata.references
        )

    async def _validate_equations(self, metadata: DocumentMetadata) -> bool:
        """Validate equations."""
        if not metadata.equations:
            return True

        return all(
            eq.content  # Must have content
            and eq.equation_type  # Must have type
            and (
                not eq.symbols  # If has symbols, must be valid
                or all(sym.symbol for sym in eq.symbols)
            )
            for eq in metadata.equations
        )

    async def _validate_citations(self, metadata: DocumentMetadata) -> bool:
        """Validate citations."""
        if not metadata.citations:
            return True

        # Build reference ID set
        ref_ids = {ref.reference_id for ref in metadata.references}

        return all(
            cit.text  # Must have text
            and cit.reference_id  # Must have reference ID
            and cit.reference_id in ref_ids  # Must reference valid reference
            for cit in metadata.citations
        )

    async def _save_metadata_async(self, metadata: DocumentMetadata):
        """Save metadata asynchronously."""
        try:
            # Load existing metadata
            current_metadata = await self._load_metadata_async()

            # Update with new metadata
            current_metadata["documents"][str(metadata.file_path)] = metadata.model_dump()
            current_metadata["schema_version"] = str(self.schema_version)

            # Save back to file
            async with aiofiles.open(self.metadata_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(current_metadata, indent=2, ensure_ascii=False, cls=DateTimeEncoder))

            logger.info(f"✓ Metadata saved for {metadata.file_path}")

        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")
            raise

    async def _load_metadata_async(self) -> Dict[str, Any]:
        """Load metadata asynchronously."""
        try:
            async with aiofiles.open(self.metadata_path, "r", encoding="utf-8") as f:
                content = await f.read()
                data = json.loads(content)
                if "documents" not in data:
                    data["documents"] = {}
                return data
        except Exception as e:
            logger.error(f"Error loading metadata: {str(e)}")
            return {"schema_version": str(self.schema_version), "documents": {}}

    def get_metadata(self, file_path: Path) -> Optional[DocumentMetadata]:
        """Get metadata for a specific file."""
        metadata_dict = self._load_metadata().get("documents", {}).get(str(file_path))
        if metadata_dict:
            return DocumentMetadata.model_validate(metadata_dict)
        return None

    def remove_metadata(self, file_path: Path):
        """Remove metadata for a specific file."""
        try:
            current_metadata = self._load_metadata()
            if str(file_path) in current_metadata.get("documents", {}):
                del current_metadata["documents"][str(file_path)]
                with open(self.metadata_path, "w", encoding="utf-8") as f:
                    json.dump(current_metadata, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
                logger.info(f"✓ Metadata removed for {file_path}")
        except Exception as e:
            logger.error(f"Error removing metadata: {str(e)}")
            raise

    def _load_metadata(self) -> Dict[str, Any]:
        """Synchronous metadata loading."""
        try:
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "documents" not in data:
                    data["documents"] = {}
                return data
        except Exception as e:
            logger.error(f"Error loading metadata: {str(e)}")
            return {"schema_version": str(self.schema_version), "documents": {}}
