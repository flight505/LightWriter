"""Centralized constants for Lightwriter_CLI."""
from enum import Enum
from pathlib import Path

# File System
DEFAULT_STORE_PATH = Path.home() / ".lightwriter"
SUPPORTED_EXTENSIONS = [".pdf"]
TEMP_DIR = DEFAULT_STORE_PATH / "temp"

# Processing
MAX_RETRIES = 3
RETRY_DELAY = 10  # seconds
CHUNK_SIZE = 1000
MAX_WORKERS = 4

# API Configuration
CROSSREF_API_URL = "https://api.crossref.org/works/"
ARXIV_API_BASE = "http://export.arxiv.org/api/query"

# LightRAG Configuration
DEFAULT_EMBEDDING_DIM = 1536
MAX_TOKEN_SIZE = 8192
DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP = 50

class ProcessingState(Enum):
    """Processing states for pipeline steps."""
    INITIALIZED = "initialized"
    EXTRACTING_TEXT = "extracting_text"
    EXTRACTING_IDENTIFIER = "extracting_identifier"
    FETCHING_METADATA = "fetching_metadata"
    EXTRACTING_REFERENCES = "extracting_references"
    EXTRACTING_EQUATIONS = "extracting_equations"
    CONSOLIDATING = "consolidating"
    COMPLETED = "completed"
    FAILED = "failed"

# Success Messages
SUCCESS_MESSAGES = {
    "text_extraction": "✓ Text extracted successfully",
    "identifier_found": "✓ Found {identifier_type}: {identifier}",
    "metadata_fetch": "✓ Metadata fetched successfully",
    "references_found": "✓ Found {count} references",
    "equations_found": "✓ Found {count} equations",
    "store_update": "✓ Store updated successfully"
}

# Error Messages
ERROR_MESSAGES = {
    "file_not_found": "⚠️ File not found: {file_path}",
    "extraction_failed": "⚠️ {step} extraction failed: {error}",
    "api_error": "⚠️ {service} API error: {error}",
    "validation_failed": "⚠️ Validation failed: {error}",
    "store_error": "⚠️ Store operation failed: {error}"
} 