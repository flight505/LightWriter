"""Unit tests for store and metadata components."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.core.store.manager import StoreManager
from src.core.store.lightrag import LightRAGStore
from src.core.metadata.consolidator import MetadataConsolidator
from src.utils.constants import DEFAULT_STORE_PATH

pytestmark = pytest.mark.asyncio  # Mark all tests as async

# Test data
TEST_STORE_PATH = DEFAULT_STORE_PATH / "test_store"
SAMPLE_METADATA = {
    'file_hash': 'abc123',
    'identifier_info': {
        'identifier': '10.1234/sample',
        'identifier_type': 'doi',
        'method': 'extraction'
    },
    'references': [
        {
            'title': 'Sample Paper',
            'authors': [{'full_name': 'Author A'}],
            'year': 2023
        }
    ],
    'equations': [
        {
            'content': 'E = mc^2',
            'context': 'Einstein equation'
        }
    ],
    'errors': []
}

@pytest.fixture(scope="module")
def test_file():
    """Create test file path."""
    return Path("test_doc.pdf")

@pytest.fixture(scope="module")
def store_path():
    """Create and clean test store path."""
    path = TEST_STORE_PATH
    if path.exists():
        for file in path.glob("*"):
            file.unlink()
        path.rmdir()
    path.mkdir(parents=True)
    return path

@pytest.fixture
def metadata_consolidator(store_path):
    """Create test metadata consolidator."""
    return MetadataConsolidator(store_path=store_path)

@pytest.fixture
def lightrag_store(store_path):
    """Create test LightRAG store."""
    return LightRAGStore(store_path=store_path)

@pytest.fixture
def store_manager(store_path):
    """Create test store manager."""
    return StoreManager(store_path=store_path)

def test_metadata_consolidation(metadata_consolidator, test_file):
    """Test metadata consolidation."""
    metadata = metadata_consolidator.consolidate_metadata(
        file_path=test_file,
        file_hash=SAMPLE_METADATA['file_hash'],
        identifier_info=SAMPLE_METADATA['identifier_info'],
        references=SAMPLE_METADATA['references'],
        equations=SAMPLE_METADATA['equations']
    )
    
    assert metadata is not None
    assert metadata.file_hash == SAMPLE_METADATA['file_hash']
    assert metadata.identifier == SAMPLE_METADATA['identifier_info']['identifier']
    assert len(metadata.references) == len(SAMPLE_METADATA['references'])
    assert len(metadata.equations) == len(SAMPLE_METADATA['equations'])

def test_metadata_storage(metadata_consolidator, test_file):
    """Test metadata storage and retrieval."""
    # Store metadata
    metadata_consolidator.consolidate_metadata(
        file_path=test_file,
        file_hash=SAMPLE_METADATA['file_hash'],
        identifier_info=SAMPLE_METADATA['identifier_info']
    )
    
    # Retrieve metadata
    stored_metadata = metadata_consolidator.get_metadata(test_file)
    assert stored_metadata is not None
    assert stored_metadata.file_hash == SAMPLE_METADATA['file_hash']
    
    # Remove metadata
    metadata_consolidator.remove_metadata(test_file)
    assert metadata_consolidator.get_metadata(test_file) is None

@patch('lightrag.LightRAG')
def test_lightrag_store(mock_lightrag, lightrag_store):
    """Test LightRAG store operations."""
    # Mock LightRAG instance
    mock_instance = MagicMock()
    mock_lightrag.return_value = mock_instance
    
    # Test document addition
    success = lightrag_store.add_document(SAMPLE_METADATA)
    assert success
    mock_instance.insert.assert_called_once()
    
    # Test search
    mock_instance.query.return_value = {"matches": [{"text": "sample"}]}
    results = lightrag_store.search("test query")
    assert "matches" in results
    mock_instance.query.assert_called_once()

def test_store_manager_operations(store_manager, test_file):
    """Test store manager operations."""
    # Add document
    success = store_manager.add_document(test_file, SAMPLE_METADATA)
    assert success
    
    # Get metadata
    metadata = store_manager.get_document_metadata(test_file)
    assert metadata is not None
    assert metadata['file_hash'] == SAMPLE_METADATA['file_hash']
    
    # Get all metadata
    all_metadata = store_manager.get_all_metadata()
    assert len(all_metadata) > 0
    assert str(test_file) in all_metadata
    
    # Get stats
    stats = store_manager.get_store_stats()
    assert stats['document_count'] > 0
    assert 'lightrag_stats' in stats
    
    # Remove document
    success = store_manager.remove_document(test_file)
    assert success
    assert store_manager.get_document_metadata(test_file) is None 