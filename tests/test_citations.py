import pytest
from pathlib import Path
import json
import shutil
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

def test_citation_extraction_with_output(output_dir):
    """Test citation extraction and save results for inspection."""
    pdf_extractor = PDFExtractor()
    citation_extractor = CitationExtractor()
    test_pdfs = list(Path("tests/pdfs").glob("*.pdf"))
    
    assert len(test_pdfs) > 0, "No test PDFs found"
    
    # Process each PDF
    for pdf_path in test_pdfs:
        print(f"\nProcessing: {pdf_path.name}")
        
        # Extract text and markdown from PDF
        pdf_content = pdf_extractor.extract_all(pdf_path)
        text = pdf_content["text"]
        markdown = pdf_content["markdown"]
        
        # Save Marker output for comparison
        marker_dir = output_dir / "marker"
        marker_text = marker_dir / f"{pdf_path.stem}_text.txt"
        marker_md = marker_dir / f"{pdf_path.stem}_markdown.md"
        
        with marker_text.open('w', encoding='utf-8') as f:
            f.write(text)
        with marker_md.open('w', encoding='utf-8') as f:
            f.write(markdown)
        
        # Extract citations
        citations = citation_extractor.extract_citations(text)
        unique_refs = citation_extractor.extract_unique_references(citations)
        
        # Prepare results
        results = {
            "filename": pdf_path.name,
            "total_citations": len(citations),
            "unique_references": len(unique_refs),
            "citations": [citation_to_dict(c) for c in citations],
            "unique_reference_ids": sorted(list(unique_refs))
        }
        
        # Save citation results
        citations_dir = output_dir / "citations"
        output_file = citations_dir / f"{pdf_path.stem}_citations.json"
        with output_file.open('w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save human-readable version
        readable_output = citations_dir / f"{pdf_path.stem}_citations.txt"
        with readable_output.open('w', encoding='utf-8') as f:
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
            
            # Add reference list
            f.write("\nUnique References:\n")
            f.write("-" * 80 + "\n")
            for ref in sorted(unique_refs):
                f.write(f"- {ref}\n")
        
        print(f"Found {len(citations)} citations ({len(unique_refs)} unique references)")
        
        # Basic assertions
        assert len(citations) > 0, f"No citations found in {pdf_path.name}"
        assert len(unique_refs) > 0, f"No unique references found in {pdf_path.name}" 