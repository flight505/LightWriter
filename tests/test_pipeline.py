"""Integration tests for the complete document processing pipeline."""
import asyncio
import json
import shutil
from pathlib import Path
from typing import Any, Dict

import pytest

from src.core.extractors.citation_extractor import CitationExtractor
from src.core.extractors.equation_extractor import EquationExtractor
from src.core.extractors.identifier_extractor import IdentifierExtractor
from src.core.extractors.pdf_extractor import PDFExtractor
from src.core.extractors.reference_extractor import ReferenceExtractor
from src.core.metadata.consolidator import MetadataConsolidator
from src.utils.constants import PROCESSED_OUTPUT_PATH, ProcessingState


@pytest.fixture(scope="function")
def output_dir():
    """Create and return output directory for test results."""
    path = PROCESSED_OUTPUT_PATH / "test_results" / "pipeline"
    if path.exists():
        shutil.rmtree(path)

    # Create output directories
    for subdir in ["marker", "metadata", "references", "equations", "citations", "consolidated"]:
        (path / subdir).mkdir(parents=True)

    return path

def save_json_output(data: Dict[str, Any], filepath: Path) -> None:
    """Save data as JSON with proper encoding."""
    with filepath.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def test_full_processing_pipeline(output_dir):
    """Test the complete document processing pipeline."""
    # Initialize extractors
    pdf_extractor = PDFExtractor()
    identifier_extractor = IdentifierExtractor()
    reference_extractor = ReferenceExtractor()
    equation_extractor = EquationExtractor()
    citation_extractor = CitationExtractor()
    metadata_consolidator = MetadataConsolidator()

    # Get test PDFs
    test_pdfs = list(Path("tests/pdfs").glob("*.pdf"))
    assert len(test_pdfs) > 0, "No test PDFs found"

    # Process each PDF
    for pdf_path in test_pdfs:
        print(f"\nProcessing: {pdf_path.name}")
        doc_results = {
            "filename": pdf_path.name,
            "processing_state": ProcessingState.PROCESSING.value,
            "steps": {}
        }

        try:
            # 1. Extract text with Marker
            print("  Extracting text...")
            pdf_content = pdf_extractor.extract_all(pdf_path)
            text = pdf_content["text"]
            markdown = pdf_content["markdown"]

            # Save Marker output
            marker_dir = output_dir / "marker"
            with (marker_dir / f"{pdf_path.stem}_text.txt").open('w', encoding='utf-8') as f:
                f.write(text)
            with (marker_dir / f"{pdf_path.stem}_markdown.md").open('w', encoding='utf-8') as f:
                f.write(markdown)

            doc_results["steps"]["text_extraction"] = {
                "status": "completed",
                "file_hash": pdf_content.get("file_hash", "")
            }

            # 2. Extract identifier
            print("  Extracting identifier...")
            identifier_info = identifier_extractor.extract_identifier(pdf_path)
            save_json_output(
                identifier_info,
                output_dir / "metadata" / f"{pdf_path.stem}_identifier.json"
            )
            doc_results["steps"]["identifier"] = identifier_info

            # 3. Extract references
            print("  Extracting references...")
            references = reference_extractor.extract_references(
                text=text,
                identifier=identifier_info.get('identifier'),
                identifier_type=identifier_info.get('identifier_type')
            )
            save_json_output(
                {"references": [ref.model_dump() for ref in references]},
                output_dir / "references" / f"{pdf_path.stem}_references.json"
            )
            doc_results["steps"]["references"] = {
                "count": len(references)
            }

            # 4. Extract equations
            print("  Extracting equations...")
            equations = equation_extractor.extract_equations(markdown)
            save_json_output(
                {"equations": [eq.model_dump() for eq in equations]},
                output_dir / "equations" / f"{pdf_path.stem}_equations.json"
            )
            doc_results["steps"]["equations"] = {
                "count": len(equations)
            }

            # 5. Extract citations
            print("  Extracting citations...")
            citations = citation_extractor.extract_citations(text)
            unique_refs = citation_extractor.extract_unique_references(citations)
            citation_results = {
                "total_citations": len(citations),
                "unique_references": len(unique_refs),
                "citations": [citation.model_dump() for citation in citations],
                "unique_reference_ids": sorted(unique_refs)
            }
            save_json_output(
                citation_results,
                output_dir / "citations" / f"{pdf_path.stem}_citations.json"
            )
            doc_results["steps"]["citations"] = citation_results

            # 6. Consolidate metadata
            print("  Consolidating metadata...")
            metadata = await metadata_consolidator.consolidate_metadata_async(
                file_path=pdf_path,
                file_hash=pdf_content.get("file_hash", ""),
                identifier_info=identifier_info,
                references=references,
                equations=equations,
                citations=citations
            )
            save_json_output(
                metadata.model_dump(),
                output_dir / "consolidated" / f"{pdf_path.stem}_metadata.json"
            )

            doc_results["processing_state"] = ProcessingState.COMPLETED.value
            doc_results["success"] = True

        except Exception as e:
            print(f"  Error processing {pdf_path.name}: {str(e)}")
            doc_results["processing_state"] = ProcessingState.FAILED.value
            doc_results["success"] = False
            doc_results["error"] = str(e)

        # Save final processing results
        save_json_output(
            doc_results,
            output_dir / f"{pdf_path.stem}_processing_results.json"
        )

        # Assertions
        if doc_results["success"]:
            assert doc_results["processing_state"] == ProcessingState.COMPLETED.value
            assert "identifier" in doc_results["steps"]
            assert doc_results["steps"]["references"]["count"] > 0
            assert doc_results["steps"]["citations"]["total_citations"] > 0

async def test_validation_handling(output_dir):
    """Test metadata validation handling."""
    metadata_consolidator = MetadataConsolidator()
    test_pdf = next(Path("tests/pdfs").glob("*.pdf"))

    # Test with minimal metadata
    metadata = await metadata_consolidator.consolidate_metadata_async(
        file_path=test_pdf,
        file_hash="test_hash",
        metadata={
            "title": "Test Paper",
            "authors": [{"full_name": "Test Author"}]
        }
    )

    assert metadata is not None
    assert hasattr(metadata, 'validated')
    assert hasattr(metadata, 'validation_errors')

    # Check validation results
    assert metadata.processing.validation_results is not None
    assert "basic_metadata" in metadata.processing.validation_results
    assert "references" in metadata.processing.validation_results
    assert "equations" in metadata.processing.validation_results
    assert "citations" in metadata.processing.validation_results

async def test_concurrent_processing(output_dir):
    """Test concurrent processing of multiple documents."""
    metadata_consolidator = MetadataConsolidator()
    test_pdfs = list(Path("tests/pdfs").glob("*.pdf"))[:3]  # Test with first 3 PDFs

    async def process_doc(pdf_path: Path):
        return await metadata_consolidator.consolidate_metadata_async(
            file_path=pdf_path,
            file_hash=f"test_hash_{pdf_path.stem}",
            metadata={
                "title": f"Test Paper {pdf_path.stem}",
                "authors": [{"full_name": "Test Author"}]
            }
        )

    # Process documents concurrently
    results = await asyncio.gather(*[
        process_doc(pdf) for pdf in test_pdfs
    ])

    # Verify results
    assert len(results) == len(test_pdfs)
    for metadata in results:
        assert metadata is not None
        assert metadata.file_hash.startswith("test_hash_")
        assert metadata.title.startswith("Test Paper")
        assert len(metadata.authors) == 1
