"""End-to-end tests for PDF processing pipeline."""
import pytest
from pathlib import Path
from typing import Dict, Any
from src.processing.pipeline import ProcessingPipeline
from src.core.store.manager import StoreManager
from src.utils.constants import ProcessingState, DEFAULT_STORE_PATH

pytestmark = pytest.mark.asyncio  # Mark all tests as async

# Test data directory
TEST_PDFS_DIR = Path("tests/pdfs")
TEST_STORE_PATH = DEFAULT_STORE_PATH / "test_store"

@pytest.fixture(scope="module")
def store_manager():
    """Create test store manager."""
    store_path = TEST_STORE_PATH
    if store_path.exists():
        for file in store_path.glob("*"):
            file.unlink()
        store_path.rmdir()
    return StoreManager(store_path=store_path)

@pytest.fixture(scope="module")
def pipeline(store_manager):
    """Create test pipeline."""
    return ProcessingPipeline(store_manager=store_manager)

def validate_metadata(metadata: Dict[str, Any]) -> bool:
    """Validate metadata structure."""
    required_fields = ['file_hash', 'identifier_info', 'references', 'equations']
    return all(field in metadata for field in required_fields)

def test_process_all_pdfs(pipeline, store_manager):
    """Test processing all PDFs in test directory."""
    pdf_files = list(TEST_PDFS_DIR.glob("*.pdf"))
    assert len(pdf_files) > 0, "No PDF files found in test directory"
    
    for pdf_file in pdf_files:
        # Process PDF
        result = pipeline.process_document(pdf_file)
        
        # Check processing result
        assert result["state"] in [state.value for state in ProcessingState]
        assert isinstance(result["success"], bool)
        assert isinstance(result["errors"], list)
        
        if result["success"]:
            # Verify metadata was stored
            metadata = store_manager.get_document_metadata(pdf_file)
            assert metadata is not None
            assert validate_metadata(metadata)
            
            # Check identifier info
            assert metadata["identifier_info"]["identifier"]
            assert metadata["identifier_info"]["identifier_type"] in ["doi", "arxiv"]
            
            # Check references
            assert isinstance(metadata["references"], list)
            if metadata["references"]:
                ref = metadata["references"][0]
                assert "title" in ref
                assert "authors" in ref
                
            # Check equations
            assert isinstance(metadata["equations"], list)
            if metadata["equations"]:
                eq = metadata["equations"][0]
                assert "content" in eq
                assert "context" in eq

def test_store_consistency(store_manager):
    """Test store consistency after processing."""
    # Check metadata store
    all_metadata = store_manager.get_all_metadata()
    assert len(all_metadata) > 0
    
    # Check LightRAG store
    stats = store_manager.get_store_stats()
    assert stats["document_count"] == len(all_metadata)
    assert "lightrag_stats" in stats

def test_search_functionality(store_manager):
    """Test search functionality."""
    # Perform search
    results = store_manager.search(
        query="machine learning",
        mode="hybrid",
        max_results=3
    )
    
    assert isinstance(results, dict)
    if results:
        assert "matches" in results or "results" in results

def test_error_handling(pipeline):
    """Test error handling with invalid file."""
    result = pipeline.process_document(Path("nonexistent.pdf"))
    assert not result["success"]
    assert result["state"] == ProcessingState.FAILED.value
    assert len(result["errors"]) > 0

def test_duplicate_processing(pipeline, store_manager):
    """Test processing same file twice."""
    pdf_file = next(TEST_PDFS_DIR.glob("*.pdf"))
    
    # First processing
    result1 = pipeline.process_document(pdf_file)
    metadata1 = store_manager.get_document_metadata(pdf_file)
    
    # Second processing
    result2 = pipeline.process_document(pdf_file)
    metadata2 = store_manager.get_document_metadata(pdf_file)
    
    # Check results
    assert result1["success"] == result2["success"]
    assert metadata1["file_hash"] == metadata2["file_hash"] 