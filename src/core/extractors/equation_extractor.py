"""Extract equations and their context from markdown content."""
import re
from typing import List, Dict, Any
from ...utils.logger import logger
from ...utils.constants import SUCCESS_MESSAGES, ERROR_MESSAGES
from ..metadata.models import Equation

class EquationExtractor:
    """Extract equations and their context from markdown content."""
    
    # Regex patterns for equation extraction
    INLINE_MATH = r'\$([^\$]+)\$'
    DISPLAY_MATH = r'\$\$([\s\S]+?)\$\$'
    NUMBERED_MATH = r'\\begin{equation}([\s\S]+?)\\end{equation}'
    
    def extract_equations(self, markdown: str) -> List[Equation]:
        """Extract equations with context from markdown text."""
        try:
            equations = []
            
            # Split markdown into lines for context tracking
            lines = markdown.split('\n')
            current_line = 0
            
            # Process each type of equation
            equations.extend(self._extract_display_math(markdown, lines))
            equations.extend(self._extract_inline_math(lines))
            equations.extend(self._extract_numbered_equations(lines))
            
            logger.info(SUCCESS_MESSAGES["equations_found"].format(
                count=len(equations)
            ))
            
            return equations
            
        except Exception as e:
            logger.error(ERROR_MESSAGES["extraction_failed"].format(
                step="equations",
                error=str(e)
            ))
            return []
            
    def _extract_context(self, lines: List[str], line_number: int, window: int = 2) -> str:
        """Extract context around an equation."""
        start = max(0, line_number - window)
        end = min(len(lines), line_number + window + 1)
        return '\n'.join(lines[start:end]).strip()
        
    def _extract_display_math(self, markdown: str, lines: List[str]) -> List[Equation]:
        """Extract display math equations ($$ ... $$)."""
        equations = []
        matches = re.finditer(self.DISPLAY_MATH, markdown, re.MULTILINE | re.DOTALL)
        for match in matches:
            content = match.group(1).strip()
            # Find line number by counting newlines before match
            line_number = markdown[:match.start()].count('\n')
            equations.append(Equation(
                content=content,
                context=self._extract_context(lines, line_number),
                location={"line": line_number + 1, "start": match.start(), "end": match.end()}
            ))
        return equations
        
    def _extract_inline_math(self, lines: List[str]) -> List[Equation]:
        """Extract inline math equations ($ ... $)."""
        equations = []
        for i, line in enumerate(lines):
            matches = re.finditer(self.INLINE_MATH, line)
            for match in matches:
                content = match.group(1).strip()
                if len(content) > 5:  # Skip very short inline math
                    equations.append(Equation(
                        content=content,
                        context=self._extract_context(lines, i),
                        location={"line": i + 1, "start": match.start(), "end": match.end()}
                    ))
        return equations
        
    def _extract_numbered_equations(self, lines: List[str]) -> List[Equation]:
        """Extract numbered equations (\begin{equation} ... \end{equation})."""
        equations = []
        combined_text = '\n'.join(lines)
        matches = re.finditer(self.NUMBERED_MATH, combined_text)
        
        for match in matches:
            content = match.group(1).strip()
            # Find line number by counting newlines before match
            line_number = combined_text[:match.start()].count('\n')
            
            # Try to find equation number
            eq_num_match = re.search(r'\\label{([^}]+)}', content)
            equation_number = eq_num_match.group(1) if eq_num_match else None
            
            # Clean content by removing labels
            content = re.sub(r'\\label{[^}]+}', '', content).strip()
            
            equations.append(Equation(
                content=content,
                context=self._extract_context(lines, line_number),
                equation_number=equation_number,
                location={"line": line_number + 1, "start": match.start(), "end": match.end()}
            ))
            
        return equations 