"""Application constants and configuration."""

from enum import Enum
from pathlib import Path


# Processing states
class ProcessingState(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Storage paths
PROCESSED_OUTPUT_PATH = Path("storage/processed")
DEFAULT_STORE_PATH = PROCESSED_OUTPUT_PATH / "lightrag_store"


# API configurations
CROSSREF_API_URL = "https://api.crossref.org/works/"
ARXIV_API_URL = "http://export.arxiv.org/api/query?"
API_TIMEOUT = 10
CROSSREF_HEADERS = {"User-Agent": "LightWriter/1.0 (mailto:your@email.com)"}

# Processing parameters
CONTEXT_WINDOW = 3  # Sentences around citations for context
MAX_FILE_SIZE_MB = 50

# Vector storage
DEFAULT_EMBEDDING_DIM = 384  # Dimension for vector embeddings
VECTOR_STORE_PATH = PROCESSED_OUTPUT_PATH / "vector_store"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Vector storage
DEFAULT_EMBEDDING_DIM = 384  # Dimension for vector embeddings
ALLOWED_MIME_TYPES = ["application/pdf"]

# Application messages
ERROR_MESSAGES = {
    "extraction_failed": "Failed to extract {step}: {error}",
    "validation_failed": "Validation failed for {field}: {reason}",
    "api_connection": "API connection failed: {error}",
    "xml_parse": "XML parsing failed: {error}",
}

SUCCESS_MESSAGES = {
    "text_extraction": "Text extraction successful",
    "markdown_conversion": "Markdown conversion successful",
    "reference_lookup": "Reference lookup successful",
}

# PDF processing configuration
MARKER_CONFIG = {
    "output_format": "markdown",
    "layout_analysis": True,
    "detect_equations": True,
    "equation_detection_confidence": 0.3,
    "detect_inline_equations": True,
    "detect_tables": True,
    "detect_lists": True,
    "detect_code_blocks": True,
    "detect_footnotes": True,
    "equation_output": "latex",
    "preserve_math": True,
    "equation_detection_mode": "aggressive",
    "equation_context_window": 3,
    "equation_pattern_matching": True,
    "equation_symbol_extraction": True,
    "header_detection": {
        "enabled": True,
        "style": "atx",
        "levels": {"title": 1, "section": 2, "subsection": 3},
        "remove_duplicate_markers": True,
    },
    "list_detection": {
        "enabled": True,
        "unordered_marker": "-",
        "ordered_marker": "1.",
        "preserve_numbers": True,
        "indent_spaces": 2,
    },
    "layout": {
        "paragraph_breaks": True,
        "line_spacing": 2,
        "remove_redundant_whitespace": True,
        "preserve_line_breaks": True,
        "preserve_blank_lines": True,
    },
    "preserve": {
        "links": True,
        "tables": True,
        "images": True,
        "footnotes": True,
        "formatting": True,
        "lists": True,
        "headers": True,
    },
}
