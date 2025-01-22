"""Unit tests for extractors."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.core.extractors.pdf_extractor import PDFExtractor
from src.core.extractors.identifier_extractor import IdentifierExtractor
from src.core.extractors.reference_extractor import ReferenceExtractor
from src.core.extractors.equation_extractor import EquationExtractor

# Test data
TEST_PDFS_DIR = Path("tests/pdfs")
SAMPLE_DOI = "10.1234/sample.123"
SAMPLE_ARXIV = "2301.12345"
SAMPLE_TEXT = """
Abstract
This is a sample paper.

References
1. Author, A. (2023) Title of paper. Journal, 1(1).
2. Author, B. (2022) Another paper. Conference.
"""

SAMPLE_MARKDOWN = """
Here is an inline equation $E = mc^2$ and a display equation:

$$
F = ma
$$

And a numbered equation:
\\begin{equation}
PV = nRT
\\end{equation}
"""

@pytest.fixture
def pdf_file():
    """Get first PDF from test directory."""
    return next(TEST_PDFS_DIR.glob("*.pdf"))

def test_pdf_extraction(pdf_file):
    """Test PDF text extraction."""
    extractor = PDFExtractor()
    results = extractor.extract_all(pdf_file)
    
    assert results is not None
    assert "text" in results
    assert "markdown" in results
    assert "file_hash" in results
    assert len(results["text"]) > 0
    assert len(results["markdown"]) > 0
    assert len(results["file_hash"]) > 0

@patch('pdf2doi.pdf2doi')
def test_identifier_extraction_doi(mock_pdf2doi, pdf_file):
    """Test DOI extraction."""
    mock_pdf2doi.return_value = {
        'identifier': SAMPLE_DOI,
        'identifier_type': 'doi',
        'method': 'extraction'
    }
    
    extractor = IdentifierExtractor()
    result = extractor.extract_identifier(pdf_file)
    
    assert result is not None
    assert result["identifier"] == SAMPLE_DOI
    assert result["identifier_type"] == "doi"

@patch('pdf2doi.pdf2doi')
def test_identifier_extraction_arxiv(mock_pdf2doi, pdf_file):
    """Test arXiv ID extraction."""
    mock_pdf2doi.return_value = {
        'identifier': SAMPLE_ARXIV,
        'identifier_type': 'arxiv',
        'method': 'extraction'
    }
    
    extractor = IdentifierExtractor()
    result = extractor.extract_identifier(pdf_file)
    
    assert result is not None
    assert result["identifier"] == SAMPLE_ARXIV
    assert result["identifier_type"] == "arxiv"

@patch('requests.get')
def test_reference_extraction_crossref(mock_get):
    """Test reference extraction using Crossref."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {
            "reference": [
                {
                    "article-title": "Sample Paper",
                    "author": "Author A",
                    "year": "2023"
                }
            ]
        }
    }
    mock_get.return_value = mock_response
    
    extractor = ReferenceExtractor()
    refs = extractor._extract_from_crossref(SAMPLE_DOI)
    
    assert len(refs) > 0
    assert refs[0].title == "Sample Paper"
    assert len(refs[0].authors) > 0
    assert refs[0].year == 2023

def test_reference_extraction_text():
    """Test reference extraction from text."""
    extractor = ReferenceExtractor()
    refs = extractor._extract_from_text(SAMPLE_TEXT)
    
    assert isinstance(refs, list)
    if extractor.anystyle_available:
        assert len(refs) > 0

def test_equation_extraction():
    """Test equation extraction."""
    extractor = EquationExtractor()
    equations = extractor.extract_equations(SAMPLE_MARKDOWN)
    
    assert len(equations) == 3
    
    # Check inline equation
    assert any(eq.content == "E = mc^2" for eq in equations)
    
    # Check display equation
    assert any(eq.content == "F = ma" for eq in equations)
    
    # Check numbered equation
    assert any(eq.content == "PV = nRT" for eq in equations)

def test_equation_context():
    """Test equation context extraction."""
    extractor = EquationExtractor()
    equations = extractor.extract_equations(SAMPLE_MARKDOWN)
    
    for eq in equations:
        assert eq.context
        assert isinstance(eq.context, str)
        assert len(eq.context) > 0 