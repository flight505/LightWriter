"""Processing pipeline for document extraction."""
from pathlib import Path
from typing import Dict, Any, Optional
from ..utils.logger import logger
from ..utils.constants import ProcessingState
from ..core.extractors.pdf_extractor import PDFExtractor
from ..core.extractors.identifier_extractor import IdentifierExtractor
from ..core.extractors.reference_extractor import ReferenceExtractor
from ..core.extractors.equation_extractor import EquationExtractor
from ..core.store.manager import StoreManager

class ProcessingPipeline:
    """Coordinate document processing steps."""
    
    def __init__(self, store_manager: Optional[StoreManager] = None):
        """Initialize pipeline with extractors."""
        self.pdf_extractor = PDFExtractor()
        self.identifier_extractor = IdentifierExtractor()
        self.reference_extractor = ReferenceExtractor()
        self.equation_extractor = EquationExtractor()
        self.store_manager = store_manager or StoreManager()
        
    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process document through extraction pipeline."""
        try:
            logger.info(f"Processing document: {file_path}")
            state = ProcessingState.INITIALIZED
            errors = []
            
            # Step 1: Extract text and markdown
            state = ProcessingState.EXTRACTING_TEXT
            extraction_results = self.pdf_extractor.extract_all(file_path)
            if not extraction_results.get('text') or not extraction_results.get('markdown'):
                errors.append("Text extraction failed")
                return self._create_result(state, errors)
            
            # Step 2: Extract identifier
            state = ProcessingState.EXTRACTING_IDENTIFIER
            identifier_info = self.identifier_extractor.extract_identifier(file_path)
            if not identifier_info:
                errors.append("Identifier extraction failed")
                return self._create_result(state, errors)
            
            # Step 3: Extract references
            state = ProcessingState.EXTRACTING_REFERENCES
            references = self.reference_extractor.extract_references(
                identifier=identifier_info['identifier'],
                identifier_type=identifier_info['identifier_type'],
                text=extraction_results['text']
            )
            
            # Step 4: Extract equations
            state = ProcessingState.EXTRACTING_EQUATIONS
            equations = self.equation_extractor.extract_equations(
                extraction_results['markdown']
            )
            
            # Step 5: Consolidate and store
            state = ProcessingState.CONSOLIDATING
            metadata = {
                'file_hash': extraction_results['file_hash'],
                'identifier_info': identifier_info,
                'references': references,
                'equations': equations,
                'errors': errors
            }
            
            store_success = self.store_manager.add_document(
                file_path=file_path,
                metadata=metadata
            )
            
            if store_success:
                state = ProcessingState.COMPLETED
            else:
                state = ProcessingState.FAILED
                errors.append("Store update failed")
            
            return self._create_result(state, errors)
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return self._create_result(ProcessingState.FAILED, [str(e)])
    
    def _create_result(self, state: ProcessingState, errors: list) -> Dict[str, Any]:
        """Create standardized result dictionary."""
        return {
            "state": state.value,
            "success": state == ProcessingState.COMPLETED,
            "errors": errors
        } 