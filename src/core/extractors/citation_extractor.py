"""Extract and process citations from academic text."""

import re
from typing import List, Set

from src.core.metadata.models import Citation, Reference
from src.utils.constants import CONTEXT_WINDOW


class CitationExtractor:
    """Extracts citations from academic text."""

    def __init__(self):
        # Numeric citation patterns
        self.numeric_patterns = [
            # [1] or [1,2] or [1, 2] or [1 2]
            r"\[(\d+(?:[,\s]+\d+)*)\]",
            # (1) or (1,2) or (1, 2) or (1 2)
            r"\((\d+(?:[,\s]+\d+)*)\)",
        ]

        # Author-year patterns
        self.author_patterns = [
            # Smith et al. (2023)
            r"([A-Z][a-z]+(?:\s+et\s+al\.)?)\s*\((\d{4}[a-z]?)\)",
            # (Smith et al., 2023)
            r"\(([A-Z][a-z]+(?:\s+et\s+al\.)?),\s*(\d{4}[a-z]?)\)",
        ]

        # Patterns to identify equation contexts
        self.equation_markers = [
            r"\$\$.*?\$\$",  # Display math $$...$$
            r"\$.*?\$",  # Inline math $...$
            r"\\begin\{equation\}.*?\\end\{equation\}",
            r"\\begin\{align\*?\}.*?\\end\{align\*?\}",
        ]

    def extract_citations(self, text: str) -> List[Citation]:
        """Extract citations from text."""
        citations = []

        # Extract numeric citations
        for pattern in self.numeric_patterns:
            for match in re.finditer(pattern, text):
                # Skip if within equation
                if self._is_in_equation(text, match.start()):
                    continue

                # Extract and normalize numbers
                content = match.group(1)
                numbers = [
                    num.strip()
                    for num in re.split(r"[,\s]+", content)
                    if num.strip().isdigit() and len(num.strip()) <= 3
                ]

                if numbers:
                    # Get context window
                    start_ctx = max(0, match.start() - CONTEXT_WINDOW)
                    end_ctx = min(len(text), match.end() + CONTEXT_WINDOW)

                    citation = Citation(
                        text=match.group(0),
                        context=text[start_ctx:end_ctx].strip(),
                        citation_type="numeric",
                        reference_id=f"ref_{numbers[0]}",
                        location={"start": match.start(), "end": match.end()},
                        normalized_text=",".join(sorted(numbers, key=int)),
                    )
                    citations.append(citation)

        # Extract author-year citations
        for pattern in self.author_patterns:
            for match in re.finditer(pattern, text):
                # Skip if within equation
                if self._is_in_equation(text, match.start()):
                    continue

                # Get context window
                start_ctx = max(0, match.start() - CONTEXT_WINDOW)
                end_ctx = min(len(text), match.end() + CONTEXT_WINDOW)

                # Create citation
                citation = Citation(
                    text=match.group(0),
                    context=text[start_ctx:end_ctx].strip(),
                    citation_type="author-year",
                    reference_id=self._normalize_author_citation(match.group(0)),
                    location={"start": match.start(), "end": match.end()},
                    normalized_text=self._normalize_author_citation(match.group(0)),
                )
                citations.append(citation)

        return citations

    def _is_in_equation(self, text: str, position: int) -> bool:
        """Check if position is within any equation block."""
        for pattern in self.equation_markers:
            for match in re.finditer(pattern, text, re.DOTALL):
                if match.start() <= position <= match.end():
                    return True
        return False

    def _normalize_author_citation(self, text: str) -> str:
        """Normalize author-year citation text."""
        text = text.lower()
        text = re.sub(r"[\(\),]", "", text)  # Remove parentheses and commas
        text = re.sub(r"\s*et\s+al\.\s*", "_et_al_", text)  # Normalize et al.
        text = re.sub(r"\s+", "_", text.strip())  # Replace spaces with underscores
        return text

    def extract_unique_references(self, citations: List[Citation]) -> Set[str]:
        """Extract unique reference identifiers from citations."""
        unique_refs = set()
        for citation in citations:
            if citation.citation_type == "numeric":
                numbers = re.findall(r"\d+", citation.text)
                unique_refs.update(f"ref_{num}" for num in numbers)
            else:
                unique_refs.add(citation.reference_id)
        return unique_refs

    def link_citations_to_references(self, citations: List[Citation], references: List[Reference]) -> List[Citation]:
        """Link citations to their corresponding references."""
        # Build reference lookup maps
        ref_by_id = {ref.reference_id: ref for ref in references}
        ref_by_normalized = {self._normalize_reference(ref): ref for ref in references}

        linked_citations = []
        for citation in citations:
            if citation.citation_type == "numeric":
                # For numeric citations, use reference ID directly
                ref_id = citation.reference_id
                if ref_id in ref_by_id:
                    citation.reference_id = ref_id
            else:
                # For author-year citations, try to match normalized text
                normalized = citation.normalized_text
                if normalized in ref_by_normalized:
                    citation.reference_id = ref_by_normalized[normalized].reference_id

            linked_citations.append(citation)

        return linked_citations

    def _normalize_reference(self, ref: Reference) -> str:
        """Normalize reference for matching with citations."""
        if not ref.authors:
            return ""

        # Get first author's family name
        first_author = ref.authors[0].family or ref.authors[0].full_name.split()[-1]

        # Add year if available
        if ref.year:
            return f"{first_author.lower()}_{ref.year}"

        return first_author.lower()
