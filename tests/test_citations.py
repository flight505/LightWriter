"""Test citation extraction and validation."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

import pytest

from src.core.extractors.citation_extractor import CitationExtractor
from src.core.extractors.pdf_extractor import PDFExtractor
from src.core.metadata.models import Author, Citation, Reference
from src.utils.constants import PROCESSED_OUTPUT_PATH


def citation_to_dict(citation: Citation) -> dict:
    """Convert Citation object to dictionary for JSON serialization."""
    return {
        "text": citation.text,
        "context": citation.context,
        "citation_type": citation.citation_type,
        "reference_id": citation.reference_id,
        "location": citation.location,
        "normalized_text": citation.normalized_text,
    }


@pytest.fixture
def output_dir():
    """Create and return output directory for test results."""
    path = PROCESSED_OUTPUT_PATH / "test_results"
    # Clean previous results
    if path.exists():
        shutil.rmtree(path)

    # Create directories
    citations_dir = path / "citations"
    marker_dir = path / "marker"
    citations_dir.mkdir(parents=True)
    marker_dir.mkdir(parents=True)

    return path


@pytest.fixture
def sample_references() -> List[Reference]:
    """Create sample references for testing."""
    return [
        Reference(
            title="Sample Paper One",
            authors=[Author(full_name="Author A")],
            year=2023,
            reference_id="ref_1",
            doi="10.1234/sample.1",
        ),
        Reference(
            title="Sample Paper Two",
            authors=[Author(full_name="Author B"), Author(full_name="Author C")],
            year=2022,
            reference_id="ref_2",
            arxiv_id="2201.12345",
        ),
    ]


def test_citation_types():
    """Test different citation type detection."""
    citation_extractor = CitationExtractor()

    # Test numeric citations
    numeric_text = "This is shown in [1] and also discussed in [2, 3]."
    numeric_citations = citation_extractor.extract_citations(numeric_text)
    assert len(numeric_citations) > 0
    assert all(c.citation_type == "numeric" for c in numeric_citations)

    # Test author-year citations
    author_year_text = "Smith et al. (2023) showed that... Another study (Jones, 2022) found..."
    author_year_citations = citation_extractor.extract_citations(author_year_text)
    assert len(author_year_citations) > 0
    assert all(c.citation_type == "author-year" for c in author_year_citations)


def test_citation_normalization():
    """Test citation text normalization."""
    citation_extractor = CitationExtractor()

    # Test numeric citations with various formats
    numeric_cases = [
        ("[1]", "1"),
        ("[1,2,3]", "1,2,3"),
        ("[1, 2, 3]", "1,2,3"),
        ("[1 2 3]", "1,2,3"),
        ("(1)", "1"),
        ("(1, 2)", "1,2"),
        ("(1 2)", "1,2"),
        ("[1,2,3,4]", "1,2,3,4"),
        ("[1, 2, 3, 4]", "1,2,3,4"),
        ("[1 2 3 4]", "1,2,3,4"),
    ]

    for original, expected in numeric_cases:
        citations = citation_extractor.extract_citations(f"Text {original} more text")
        assert len(citations) == 1, f"Failed to extract numeric citation from '{original}'"
        assert citations[0].normalized_text == expected, (
            f"Expected normalized text '{expected}' but got '{citations[0].normalized_text}' for '{original}'"
        )

    # Test author-year citations
    author_cases = [
        ("Smith et al. (2023)", "smith_et_al_2023"),
        ("(Smith et al., 2023)", "smith_et_al_2023"),
        ("Jones (2022)", "jones_2022"),
    ]

    for original, expected in author_cases:
        citations = citation_extractor.extract_citations(f"Text {original} more text")
        assert len(citations) == 1, f"Failed to extract author citation from '{original}'"
        assert citations[0].normalized_text == expected, (
            f"Expected normalized text '{expected}' but got '{citations[0].normalized_text}' for '{original}'"
        )


def test_citation_context():
    """Test citation context extraction."""
    citation_extractor = CitationExtractor()

    text = """This is a sentence before the citation.
    An important finding [1] was reported.
    This is a sentence after the citation."""

    citations = citation_extractor.extract_citations(text)
    assert len(citations) == 1
    assert "important finding" in citations[0].context
    assert "was reported" in citations[0].context


def test_reference_linking():
    """Test linking citations to references."""
    citation_extractor = CitationExtractor()

    # Create test references
    references = [
        Reference(title="Test Paper", authors=[Author(full_name="Smith, J.")], year=2023, reference_id="ref_1")
    ]

    # Create test citation
    citations = citation_extractor.extract_citations("As shown in [1]")

    # Link citations to references
    linked_citations = citation_extractor.link_citations_to_references(citations, references)

    assert len(linked_citations) == 1
    assert linked_citations[0].reference_id == "ref_1"


def test_citation_extraction_with_validation(output_dir, sample_references):
    """Test citation extraction with enhanced validation."""
    pdf_extractor = PDFExtractor()
    citation_extractor = CitationExtractor()
    test_pdfs = list(Path("tests/pdfs").glob("*.pdf"))

    assert len(test_pdfs) > 0, "No test PDFs found"

    # Process each PDF
    for pdf_path in test_pdfs:
        print(f"\nProcessing: {pdf_path.name}")

        # Extract text and markdown
        pdf_content = pdf_extractor.extract_all(pdf_path)
        text = pdf_content["text"]
        markdown = pdf_content["markdown"]

        # Save Marker output for comparison
        marker_dir = output_dir / "marker"
        marker_text = marker_dir / f"{pdf_path.stem}_text.txt"
        marker_md = marker_dir / f"{pdf_path.stem}_markdown.md"

        with marker_text.open("w", encoding="utf-8") as f:
            f.write(text)
        with marker_md.open("w", encoding="utf-8") as f:
            f.write(markdown)

        # Extract and validate citations
        citations = citation_extractor.extract_citations(text)

        # Validate citation format
        for citation in citations:
            assert citation.text, "Citation text cannot be empty"
            assert citation.context, "Citation must have context"
            assert citation.citation_type in ["numeric", "author-year"], (
                f"Invalid citation type: {citation.citation_type}"
            )
            assert citation.location, "Citation must have location information"

        # Link citations to references
        linked_citations = citation_extractor.link_citations_to_references(citations, sample_references)

        # Extract unique references from citations
        unique_refs = citation_extractor.extract_unique_references(linked_citations)

        # Prepare results with validation info
        results = {
            "filename": pdf_path.name,
            "total_citations": len(citations),
            "unique_references": len(unique_refs),
            "citations": [citation_to_dict(c) for c in linked_citations],
            "unique_reference_ids": sorted(unique_refs),
            "validation": {
                "timestamp": datetime.now().isoformat(),
                "citation_format_valid": all(c.text and c.context for c in citations),
                "reference_linking_valid": all(
                    not c.reference_id or c.reference_id in {ref.reference_id for ref in sample_references}
                    for c in linked_citations
                ),
                "citation_types": {
                    ctype: len([c for c in citations if c.citation_type == ctype])
                    for ctype in ["numeric", "author-year"]
                },
            },
        }

        # Save citation results
        citations_dir = output_dir / "citations"
        output_file = citations_dir / f"{pdf_path.stem}_citations.json"
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Save human-readable version with validation info
        readable_output = citations_dir / f"{pdf_path.stem}_citations.txt"
        with readable_output.open("w", encoding="utf-8") as f:
            f.write(f"Citations Analysis for {pdf_path.name}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total Citations Found: {len(citations)}\n")
            f.write(f"Unique References: {len(unique_refs)}\n\n")

            f.write("Validation Results:\n")
            f.write("-" * 80 + "\n")
            f.write(f"Citation Format Valid: {results['validation']['citation_format_valid']}\n")
            f.write(f"Reference Linking Valid: {results['validation']['reference_linking_valid']}\n")
            f.write("\nCitation Types Distribution:\n")
            for ctype, count in results["validation"]["citation_types"].items():
                f.write(f"- {ctype}: {count}\n")
            f.write("\n")

            f.write("Citation Details:\n")
            f.write("-" * 80 + "\n")
            for i, citation in enumerate(linked_citations, 1):
                f.write(f"\n{i}. Citation: {citation.text}\n")
                f.write(f"   Type: {citation.citation_type}\n")
                f.write(f"   Context: {citation.context}\n")
                f.write(f"   Reference ID: {citation.reference_id or 'Not linked'}\n")
                f.write(f"   Normalized: {citation.normalized_text}\n")
                f.write("-" * 40 + "\n")

            # Add reference list
            f.write("\nUnique References:\n")
            f.write("-" * 80 + "\n")
            for ref in sorted(unique_refs):
                f.write(f"- {ref}\n")

        print(f"Found {len(citations)} citations ({len(unique_refs)} unique references)")
