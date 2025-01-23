"""Individual processing steps for the pipeline."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from ..utils.constants import ProcessingState
from ..utils.logger import logger


class ProcessingStep(ABC):
    """Base class for processing steps."""

    def __init__(self, next_step: Optional['ProcessingStep'] = None):
        """Initialize step with optional next step."""
        self.next_step = next_step

    @abstractmethod
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the step and update context."""
        pass

    def _continue(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Continue to next step if available."""
        if self.next_step:
            return self.next_step.process(context)
        return context

class ValidationStep(ProcessingStep):
    """Validate input file."""

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate file exists and is PDF."""
        try:
            file_path = Path(context['file_path'])
            if not file_path.exists():
                raise ValueError(f"File not found: {file_path}")
            if file_path.suffix.lower() != '.pdf':
                raise ValueError(f"Not a PDF file: {file_path}")

            context['state'] = ProcessingState.INITIALIZED
            return self._continue(context)

        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            context['state'] = ProcessingState.FAILED
            context['errors'] = [str(e)]
            return context

class TextExtractionStep(ProcessingStep):
    """Extract text and markdown from PDF."""

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text content."""
        try:
            file_path = Path(context['file_path'])
            extractor = context['extractors']['pdf']

            results = extractor.extract_all(file_path)
            if not results.get('text') or not results.get('markdown'):
                raise ValueError("Text extraction failed")

            context.update({
                'text': results['text'],
                'markdown': results['markdown'],
                'file_hash': results['file_hash'],
                'state': ProcessingState.EXTRACTING_TEXT
            })

            return self._continue(context)

        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            context['state'] = ProcessingState.FAILED
            context['errors'] = [str(e)]
            return context

class IdentifierExtractionStep(ProcessingStep):
    """Extract DOI/arXiv identifier."""

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract identifier."""
        try:
            file_path = Path(context['file_path'])
            extractor = context['extractors']['identifier']

            identifier_info = extractor.extract_identifier(file_path)
            if not identifier_info:
                raise ValueError("No identifier found")

            context['identifier_info'] = identifier_info
            context['state'] = ProcessingState.EXTRACTING_IDENTIFIER

            return self._continue(context)

        except Exception as e:
            logger.error(f"Identifier extraction failed: {str(e)}")
            context['state'] = ProcessingState.FAILED
            context['errors'] = [str(e)]
            return context

class ReferenceExtractionStep(ProcessingStep):
    """Extract references."""

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract references."""
        try:
            extractor = context['extractors']['reference']
            identifier_info = context['identifier_info']

            references = extractor.extract_references(
                identifier=identifier_info['identifier'],
                identifier_type=identifier_info['identifier_type'],
                text=context.get('text')
            )

            context['references'] = references
            context['state'] = ProcessingState.EXTRACTING_REFERENCES

            return self._continue(context)

        except Exception as e:
            logger.error(f"Reference extraction failed: {str(e)}")
            context['state'] = ProcessingState.FAILED
            context['errors'] = [str(e)]
            return context

class EquationExtractionStep(ProcessingStep):
    """Extract equations."""

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract equations."""
        try:
            extractor = context['extractors']['equation']

            equations = extractor.extract_equations(context['markdown'])

            context['equations'] = equations
            context['state'] = ProcessingState.EXTRACTING_EQUATIONS

            return self._continue(context)

        except Exception as e:
            logger.error(f"Equation extraction failed: {str(e)}")
            context['state'] = ProcessingState.FAILED
            context['errors'] = [str(e)]
            return context

class StorageStep(ProcessingStep):
    """Store extracted information."""

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Store metadata."""
        try:
            store_manager = context['store_manager']
            file_path = Path(context['file_path'])

            metadata = {
                'file_hash': context['file_hash'],
                'identifier_info': context['identifier_info'],
                'references': context['references'],
                'equations': context['equations'],
                'errors': context.get('errors', [])
            }

            success = store_manager.add_document(
                file_path=file_path,
                metadata=metadata
            )

            if not success:
                raise ValueError("Store update failed")

            context['state'] = ProcessingState.COMPLETED
            return self._continue(context)

        except Exception as e:
            logger.error(f"Storage failed: {str(e)}")
            context['state'] = ProcessingState.FAILED
            context['errors'] = [str(e)]
            return context
