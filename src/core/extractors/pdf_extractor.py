"""PDF text extraction using marker-pdf."""

import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

from ...utils.constants import ERROR_MESSAGES, SUCCESS_MESSAGES
from ...utils.logger import logger


class PDFExtractor:
    """Extract text and metadata from PDFs using marker-pdf."""

    def __init__(self):
        """Initialize marker-pdf extractor with configuration."""
        # Initialize with just the model dict, no additional config
        self.marker = PdfConverter(artifact_dict=create_model_dict())

    def extract_text(self, file_path: Path) -> Optional[str]:
        """Extract text content from PDF."""
        try:
            logger.info(f"Extracting text from {file_path}")
            rendered = self.marker(str(file_path))
            text, _, _ = text_from_rendered(rendered)
            logger.info(SUCCESS_MESSAGES["text_extraction"])
            return text

        except Exception as e:
            logger.error(ERROR_MESSAGES["extraction_failed"].format(step="text", error=str(e)))
            return None

    def extract_markdown(self, file_path: Path) -> Optional[str]:
        """Extract markdown content from PDF."""
        try:
            logger.info(f"Converting {file_path} to markdown")
            rendered = self.marker(str(file_path))
            markdown = rendered.markdown
            logger.info("✓ Markdown conversion successful")
            return markdown

        except Exception as e:
            logger.error(ERROR_MESSAGES["extraction_failed"].format(step="markdown", error=str(e)))
            return None

    def get_file_hash(self, file_path: Path) -> str:
        """Generate SHA-256 hash of file content."""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error generating file hash: {e}")
            return ""

    def extract_all(self, file_path: Path) -> Dict[str, Any]:
        """Extract both text and markdown with file hash."""
        text = self.extract_text(file_path)
        markdown = self.extract_markdown(file_path)
        return {"text": text, "markdown": markdown, "file_hash": self.get_file_hash(file_path)}
