"""Extract references using Crossref API and Anystyle."""
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
import requests
import arxiv
from ...utils.logger import logger
from ...utils.constants import SUCCESS_MESSAGES, ERROR_MESSAGES, CROSSREF_API_URL
from ..metadata.models import Reference, Author

class ReferenceExtractor:
    """Extract references using Crossref API and Anystyle fallback."""
    
    def __init__(self):
        """Initialize reference extractor and check Anystyle availability."""
        self.anystyle_available = False
        try:
            result = subprocess.run(['anystyle', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✓ Found Anystyle: {result.stdout.strip()}")
                self.anystyle_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("⚠️ Anystyle not found. Please install it with: gem install anystyle-cli")
    
    def extract_references(self, identifier: str, identifier_type: str, text: Optional[str] = None) -> List[Reference]:
        """Extract references based on identifier type, falling back to text extraction."""
        if identifier_type.lower() == 'doi':
            # Try Crossref first for DOIs
            refs = self._extract_from_crossref(identifier)
            if refs:
                return refs
                
        # For arXiv IDs or if Crossref failed, try text extraction
        if text:
            return self._extract_from_text(text)
        return []
    
    def _extract_from_crossref(self, doi: str) -> List[Reference]:
        """Extract references from Crossref API."""
        try:
            url = f"{CROSSREF_API_URL}{doi}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if "reference" not in data.get("message", {}):
                logger.warning("No references found in Crossref data")
                return []
                
            refs_data = data["message"]["reference"]
            logger.info(SUCCESS_MESSAGES["references_found"].format(count=len(refs_data)))
            
            references = []
            for ref in refs_data:
                try:
                    # Extract title
                    title = ref.get('article-title', '') or ref.get('title', '')
                    
                    # Extract authors
                    authors = []
                    if 'author' in ref:
                        author_str = ref['author']
                        # Split multiple authors if present
                        author_names = [a.strip() for a in author_str.split(' and ') if a.strip()]
                        for name in author_names:
                            authors.append(Author(full_name=name))
                    
                    # Extract year
                    year = None
                    if 'year' in ref:
                        try:
                            year = int(ref['year'])
                        except (ValueError, TypeError):
                            pass
                    
                    # Extract DOI if available
                    doi = ref.get('DOI') or ref.get('doi')
                    
                    # Create reference
                    reference = Reference(
                        title=title,
                        authors=authors,
                        year=year,
                        doi=doi,
                        raw_text=ref.get('unstructured', '')
                    )
                    references.append(reference)
                    
                except Exception as e:
                    logger.error(f"⚠️ Error parsing Crossref reference: {str(e)}")
                    continue
            
            return references
            
        except Exception as e:
            logger.error(ERROR_MESSAGES["api_error"].format(
                service="Crossref",
                error=str(e)
            ))
            return []
    
    def _extract_from_text(self, text: str) -> List[Reference]:
        """Extract references from text using Anystyle."""
        if not self.anystyle_available:
            logger.warning("Anystyle not available for text extraction")
            return []
            
        try:
            # First try to extract references section
            ref_section = self._extract_references_section(text)
            if not ref_section:
                logger.warning("No references section found in text")
                return []
                
            # Create temporary file for Anystyle input
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_in:
                temp_in.write(ref_section)
                temp_in_path = temp_in.name
                
            try:
                # Run Anystyle and capture output
                result = subprocess.run(
                    ['anystyle', '--format', 'json', 'parse', temp_in_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Parse JSON output
                references_data = json.loads(result.stdout)
                logger.info(SUCCESS_MESSAGES["references_found"].format(count=len(references_data)))
                
                # Parse references
                references = []
                for ref in references_data:
                    try:
                        # Extract title
                        title = ref.get('title', [''])[0] if isinstance(ref.get('title'), list) else ref.get('title', '')
                        
                        # Extract authors
                        authors = []
                        author_list = ref.get('author', [])
                        if isinstance(author_list, list):
                            for author in author_list:
                                if isinstance(author, dict):
                                    given = author.get('given', '')
                                    family = author.get('family', '')
                                    if given or family:
                                        full_name = f"{given} {family}".strip()
                                        authors.append(Author(full_name=full_name))
                                elif isinstance(author, str):
                                    authors.append(Author(full_name=author))
                        elif isinstance(author_list, str):
                            authors.append(Author(full_name=author_list))
                        
                        # Extract year
                        year = None
                        year_data = ref.get('year', [''])[0] if isinstance(ref.get('year'), list) else ref.get('year', '')
                        if year_data and isinstance(year_data, str):
                            try:
                                year = int(year_data)
                            except ValueError:
                                pass
                        
                        # Create reference
                        reference = Reference(
                            title=title,
                            authors=authors,
                            year=year,
                            raw_text=ref.get('original', '')
                        )
                        references.append(reference)
                        
                    except Exception as e:
                        logger.error(f"⚠️ Error parsing reference: {str(e)}")
                        continue
                    
                return references
                
            finally:
                # Clean up temp file
                Path(temp_in_path).unlink()
            
        except Exception as e:
            logger.error(ERROR_MESSAGES["extraction_failed"].format(
                step="references",
                error=str(e)
            ))
            return []
    
    def _extract_references_section(self, text: str) -> Optional[str]:
        """Extract references section from text."""
        try:
            lines = text.split('\n')
            references_text = []
            in_references = False
            
            for line in lines:
                if not in_references:
                    if any(marker in line.lower() for marker in ['references', 'bibliography']):
                        in_references = True
                        continue
                else:
                    if any(marker in line.lower() for marker in ['appendix', 'acknowledgments']):
                        break
                    references_text.append(line)
            
            return '\n'.join(references_text) if references_text else None
            
        except Exception as e:
            logger.error(f"⚠️ Error extracting references section: {str(e)}")
            return None 