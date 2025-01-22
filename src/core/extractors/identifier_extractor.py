"""Extract DOI/arXiv identifiers from PDFs."""
from pathlib import Path
from typing import Optional, Dict, Any
import pdf2doi
from ...utils.logger import logger
from ...utils.constants import SUCCESS_MESSAGES, ERROR_MESSAGES

class IdentifierExtractor:
    """Extract DOI or arXiv ID from PDFs using pdf2doi."""
    
    def extract_identifier(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract identifier and type from PDF."""
        try:
            logger.info(f"Extracting identifier from {file_path}")
            
            # Try to extract DOI/identifier
            result = pdf2doi.pdf2doi(str(file_path))
            if not result:
                logger.warning("No identifier found in PDF")
                return None
                
            identifier = result.get('identifier')
            identifier_type = result.get('identifier_type', '').lower()
            method = result.get('method')
            
            if not identifier:
                logger.warning("No identifier found in PDF")
                return None
                
            # Clean up arXiv ID if needed
            if "arxiv" in identifier.lower():
                identifier = self._clean_arxiv_id(identifier)
                identifier_type = "arxiv"
            elif identifier.startswith("10."):
                identifier_type = "doi"
            
            logger.info(SUCCESS_MESSAGES["identifier_found"].format(
                identifier_type=identifier_type,
                identifier=identifier
            ))
            
            return {
                "identifier": identifier,
                "identifier_type": identifier_type,
                "method": method
            }
            
        except Exception as e:
            logger.error(ERROR_MESSAGES["extraction_failed"].format(
                step="identifier",
                error=str(e)
            ))
            return None
            
    def _clean_arxiv_id(self, arxiv_id: str) -> str:
        """Clean and standardize arXiv ID format."""
        # Remove 'arxiv:' prefix if present
        arxiv_id = arxiv_id.lower()
        if 'arxiv.' in arxiv_id:
            arxiv_id = arxiv_id.split('arxiv.')[-1]
        if 'arxiv:' in arxiv_id:
            arxiv_id = arxiv_id.split('arxiv:')[-1]
            
        # Remove version number if present
        if 'v' in arxiv_id:
            arxiv_id = arxiv_id.split('v')[0]
            
        # Remove any remaining special characters
        arxiv_id = arxiv_id.strip('/')
        return arxiv_id.strip() 