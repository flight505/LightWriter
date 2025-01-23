"""Unit tests for store and metadata components."""

import shutil
from pathlib import Path

import numpy as np
import pytest

from src.core.metadata.consolidator import MetadataConsolidator
from src.core.metadata.models import DocumentMetadata
from src.core.store.lightrag import LightRAGStore
from src.core.store.manager import StoreManager
from src.utils.constants import DEFAULT_STORE_PATH

pytestmark = pytest.mark.asyncio  # Mark all tests as async

# Test data
TEST_STORE_PATH = DEFAULT_STORE_PATH / "test_results" / "test_store"
SAMPLE_METADATA = {
    "file_hash": "abc123",
    "identifier": "10.1234/sample",
    "identifier_type": "doi",
    "title": "Sample Paper",
    "authors": [{"full_name": "Author A"}],
    "abstract": "Sample abstract",
    "year": 2023,
    "references": [
        {"title": "Sample Paper", "authors": [{"full_name": "Author A"}], "year": 2023, "reference_id": "ref_1"}
    ],
    "equations": [{"content": "E = mc^2", "context": "Einstein equation", "equation_type": "inline"}],
    "citations": [
        {
            "text": "[1]",
            "context": "Sample citation",
            "citation_type": "numeric",
            "reference_id": "ref_1",
            "location": {"start": 0, "end": 3},
        }
    ],
    "processing_status": "completed",
    "validated": True,
    "validation_errors": [],
}


@pytest.fixture(scope="function")
def test_file():
    """Create test file path."""
    return Path("test_doc.pdf")


@pytest.fixture(scope="function")
async def store_path():
    """Create and clean test store path."""
    path = TEST_STORE_PATH
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)

    # Create required subdirectories
    (path / "lightrag" / "documents").mkdir(parents=True)
    (path / "lightrag" / "vectors").mkdir(parents=True)
    (path / "lightrag" / "metadata").mkdir(parents=True)

    yield path
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture(scope="function")
async def metadata_consolidator(store_path):
    """Create test metadata consolidator."""
    consolidator = MetadataConsolidator(store_path=store_path)
    # Initialize metadata file
    consolidator._ensure_metadata_file()
    return consolidator


@pytest.fixture(scope="function")
async def lightrag_store(store_path):
    """Create test LightRAG store."""

    # Mock embedding function
    def mock_embedding_func(texts):
        return np.random.rand(len(texts), 384)  # Return random embeddings

    mock_embedding_func.embedding_dim = 384

    return LightRAGStore(store_path=store_path, embedding_dim=384, embedding_func=mock_embedding_func)


@pytest.fixture(scope="function")
async def store_manager(store_path):
    """Create test store manager."""
    manager = StoreManager(store_path=store_path)
    # Initialize metadata file
    manager.metadata_consolidator._ensure_metadata_file()
    return manager


async def test_metadata_consolidation(metadata_consolidator, test_file):
    """Test metadata consolidation."""
    metadata = await metadata_consolidator.consolidate_metadata_async(
        file_path=test_file,
        file_hash=SAMPLE_METADATA["file_hash"],
        identifier_info={
            "identifier": SAMPLE_METADATA["identifier"],
            "identifier_type": SAMPLE_METADATA["identifier_type"],
        },
        metadata={
            "title": SAMPLE_METADATA["title"],
            "authors": SAMPLE_METADATA["authors"],
            "abstract": SAMPLE_METADATA["abstract"],
            "year": SAMPLE_METADATA["year"],
        },
        references=SAMPLE_METADATA["references"],
        equations=SAMPLE_METADATA["equations"],
        citations=SAMPLE_METADATA["citations"],
    )

    assert metadata is not None
    assert metadata.file_hash == SAMPLE_METADATA["file_hash"]
    assert metadata.identifier == SAMPLE_METADATA["identifier"]
    assert len(metadata.references) == len(SAMPLE_METADATA["references"])
    assert len(metadata.equations) == len(SAMPLE_METADATA["equations"])
    assert len(metadata.citations) == len(SAMPLE_METADATA["citations"])
    assert metadata.validated


async def test_metadata_storage(metadata_consolidator, test_file):
    """Test metadata storage and retrieval."""
    # Store metadata
    stored_metadata = await metadata_consolidator.consolidate_metadata_async(
        file_path=test_file,
        file_hash=SAMPLE_METADATA["file_hash"],
        identifier_info={
            "identifier": SAMPLE_METADATA["identifier"],
            "identifier_type": SAMPLE_METADATA["identifier_type"],
        },
    )

    # Verify stored metadata
    assert stored_metadata is not None
    assert stored_metadata.file_hash == SAMPLE_METADATA["file_hash"]

    # Remove metadata
    metadata_consolidator.remove_metadata(test_file)
    assert metadata_consolidator.get_metadata(test_file) is None


async def test_lightrag_store(lightrag_store):
    """Test LightRAG store operations."""
    # Create test metadata
    metadata = DocumentMetadata(**SAMPLE_METADATA)

    # Test document addition
    success = await lightrag_store.add_document_async(metadata)
    assert success

    # Verify files were created
    doc_path = lightrag_store.store_path / "documents" / f"{metadata.file_hash}.txt"
    vec_path = lightrag_store.store_path / "vectors" / f"{metadata.file_hash}.npy"
    meta_path = lightrag_store.store_path / "metadata" / f"{metadata.file_hash}.json"

    assert doc_path.exists()
    assert vec_path.exists()
    assert meta_path.exists()

    # Test search
    results = await lightrag_store.search_async("test query")
    assert isinstance(results, dict)
    assert "matches" in results


async def test_store_manager_operations(store_manager, test_file):
    """Test store manager operations."""
    # Create test metadata
    metadata = DocumentMetadata(**SAMPLE_METADATA)

    # Add document
    success = await store_manager.add_document_async(test_file, metadata.model_dump())
    assert success

    # Get metadata
    stored_metadata = await store_manager.get_document_metadata_async(test_file)
    assert stored_metadata is not None
    assert stored_metadata.file_hash == metadata.file_hash

    # Get all metadata
    all_metadata = await store_manager.get_all_metadata_async()
    assert len(all_metadata.get("documents", {})) > 0

    # Get stats
    stats = await store_manager.get_store_stats_async()
    assert stats["document_count"] > 0
    assert "lightrag_stats" in stats

    # Remove document
    success = await store_manager.remove_document_async(test_file)
    assert success
    assert await store_manager.get_document_metadata_async(test_file) is None
