import pytest
from pathlib import Path
import json
from src.core.extractors.citation_extractor import CitationExtractor, Citation
from src.core.extractors.pdf_extractor import PDFExtractor
from src.utils.constants import PROCESSED_OUTPUT_PATH

def citation_to_dict(citation: Citation) -> dict:
    """Convert Citation object to dictionary for JSON serialization."""
    return {
        "text": citation.text,
        "context": citation.context,
        "citation_type": citation.citation_type.value,
        "position": citation.position,
        "normalized_text": citation.normalized_text
    }

@pytest.fixture
def output_dir():
    """Create and return output directory for test results."""
    path = PROCESSED_OUTPUT_PATH / "test_results" / "citations"
    path.mkdir(parents=True, exist_ok=True)
    return path

def test_citation_extraction_with_output(output_dir):
    """Test citation extraction and save results for inspection."""
    pdf_extractor = PDFExtractor()
    citation_extractor = CitationExtractor()
    test_pdfs = list(Path("tests/pdfs").glob("*.pdf"))
    
    assert len(test_pdfs) > 0, "No test PDFs found"
    
    # Process each PDF
    for pdf_path in test_pdfs:
        # Extract text from PDF
        pdf_content = pdf_extractor.extract_all(pdf_path)
        text = pdf_content["text"]
        
        # Extract citations
        citations = citation_extractor.extract_citations(text)
        
        # Get unique references
        unique_refs = citation_extractor.extract_unique_references(citations)
        
        # Prepare results
        results = {
            "filename": pdf_path.name,
            "total_citations": len(citations),
            "unique_references": len(unique_refs),
            "citations": [citation_to_dict(c) for c in citations],
            "unique_reference_ids": sorted(list(unique_refs))
        }
        
        # Save results
        output_file = output_dir / f"{pdf_path.stem}_citations.json"
        with output_file.open('w') as f:
            json.dump(results, f, indent=2)
        
        # Also save a human-readable version
        readable_output = output_dir / f"{pdf_path.stem}_citations.txt"
        with readable_output.open('w') as f:
            f.write(f"Citations Analysis for {pdf_path.name}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total Citations Found: {len(citations)}\n")
            f.write(f"Unique References: {len(unique_refs)}\n\n")
            
            f.write("Citation Details:\n")
            f.write("-" * 80 + "\n")
            for i, citation in enumerate(citations, 1):
                f.write(f"\n{i}. Citation: {citation.text}\n")
                f.write(f"   Type: {citation.citation_type.value}\n")
                f.write(f"   Context: {citation.context}\n")
                f.write(f"   Normalized: {citation.normalized_text}\n")
                f.write("-" * 40 + "\n")
        
        # Basic assertions
        assert len(citations) > 0, f"No citations found in {pdf_path.name}"
        assert len(unique_refs) > 0, f"No unique references found in {pdf_path.name}" 