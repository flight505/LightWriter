from dataclasses import dataclass
from typing import List, Dict, Optional, Set, Tuple
import re
from src.utils.constants import CitationType, CONTEXT_WINDOW

@dataclass
class Citation:
    """Represents a citation found in text."""
    text: str
    context: str
    citation_type: CitationType
    position: Dict[str, int]
    reference_key: Optional[str] = None
    normalized_text: Optional[str] = None

class CitationExtractor:
    """Extracts citations from academic text."""
    
    def __init__(self):
        # More specific patterns to avoid capturing years and equations
        self.patterns = {
            CitationType.NUMERIC: [
                # [1] or [1,2] or [1-3] - must be short numbers
                r'\[(\d{1,3}(?:[-–,]\d{1,3})*)\](?!\d)',  
                # (1) or (1,2) or (1-3) - not preceded by $ (equation)
                r'(?<!\$)\((\d{1,3}(?:[-–,]\d{1,3})*)\)(?!\d)'  
            ],
            CitationType.AUTHOR_YEAR: [
                # Smith et al. (2023) - capture full pattern
                r'([A-Z][a-z]+(?:\s+et\s+al\.)?)\s*\((\d{4}[a-z]?)\)',
                # (Smith et al., 2023)
                r'\(([A-Z][a-z]+(?:\s+et\s+al\.)?),\s*(\d{4}[a-z]?)\)'
            ]
        }
        
        # Patterns to identify equation contexts
        self.equation_markers = [
            r'\$\$.*?\$\$',          # Display math $$...$$
            r'\$.*?\$',              # Inline math $...$
            r'\\begin\{equation\}.*?\\end\{equation\}',
            r'\\begin\{align\*?\}.*?\\end\{align\*?\}'
        ]
    
    def _is_in_equation(self, text: str, position: int) -> bool:
        """Check if position is within any equation block."""
        for pattern in self.equation_markers:
            for match in re.finditer(pattern, text, re.DOTALL):
                if match.start() <= position <= match.end():
                    return True
        return False

    def _is_likely_year(self, number: str) -> bool:
        """Check if a number is likely a year."""
        num = int(number)
        return len(number) == 4 and 1900 <= num <= 2100

    def _extract_reference_numbers(self, text: str) -> List[str]:
        """Extract reference numbers, handling ranges and lists."""
        numbers = []
        # Split by common separators
        parts = re.split(r'[-–,]', text)
        for part in parts:
            num = re.search(r'\d+', part)
            if num:
                num = num.group()
                # Only include if it's not a year and is a reasonable reference number
                if not self._is_likely_year(num) and len(num) <= 3:
                    numbers.append(num)
        return numbers

    def extract_citations(self, text: str) -> List[Citation]:
        """Extract citations from text."""
        citations = []
        
        for cit_type, patterns in self.patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text):
                    # Skip if within equation
                    if self._is_in_equation(text, match.start()):
                        continue
                        
                    # Get context window
                    start_ctx = max(0, match.start() - CONTEXT_WINDOW)
                    end_ctx = min(len(text), match.end() + CONTEXT_WINDOW)
                    
                    citation = Citation(
                        text=match.group(0),
                        context=text[start_ctx:end_ctx].strip(),
                        citation_type=cit_type,
                        position={"start": match.start(), "end": match.end()},
                        normalized_text=self._normalize_citation(match.group(0), cit_type)
                    )
                    citations.append(citation)
        
        return citations
    
    def _normalize_citation(self, text: str, cit_type: CitationType) -> str:
        """Normalize citation text for matching."""
        if cit_type == CitationType.NUMERIC:
            numbers = self._extract_reference_numbers(text)
            return ','.join(sorted(numbers))
        else:
            # Normalize author-year format
            text = text.lower()
            text = re.sub(r'[\(\)]', '', text)  # Remove parentheses
            return text.strip()
    
    def extract_unique_references(self, citations: List[Citation]) -> Set[str]:
        """Extract unique reference identifiers from citations."""
        unique_refs = set()
        for citation in citations:
            if citation.citation_type == CitationType.NUMERIC:
                numbers = self._extract_reference_numbers(citation.text)
                unique_refs.update(numbers)
            else:
                unique_refs.add(citation.normalized_text)
        return unique_refs 