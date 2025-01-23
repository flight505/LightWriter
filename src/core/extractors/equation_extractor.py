"""Extract equations from academic text."""

import re
from typing import List

from ..metadata.models import Equation, Symbol


class EquationExtractor:
    """Extract equations from academic text."""

    def __init__(self):
        """Initialize equation patterns."""
        self.patterns = [
            (r"\$\$(.*?)\$\$", "display"),  # Display equations
            (r"\$(.*?)\$", "inline"),  # Inline equations
            (r"\\begin\{equation\}(.*?)\\end\{equation\}", "numbered"),
            (r"\\[(.*?)\\]", "display"),
            (r"\\begin\{align\*?\}(.*?)\\end\{align\*?\}", "display"),
            (r"\\begin\{eqnarray\*?\}(.*?)\\end\{eqnarray\*?\}", "display"),
        ]

    def extract_equations(self, markdown: str) -> List[Equation]:
        """Extract equations from markdown text."""
        equations = []

        try:
            # Process each type of equation
            for pattern, eq_type in self.patterns:
                for match in re.finditer(pattern, markdown, re.DOTALL):
                    content = match.group(1).strip()
                    if not content:
                        continue

                    # Get equation context
                    start_pos = match.start()
                    end_pos = match.end()
                    context = self._get_equation_context(markdown, start_pos, end_pos)

                    # Extract symbols
                    symbols = self._extract_symbols(content)

                    # Create equation object
                    equation = Equation(
                        content=content,
                        context=context,
                        symbols=symbols,
                        equation_type=eq_type,
                        location={"start": start_pos, "end": end_pos},
                    )
                    equations.append(equation)

            return equations

        except Exception as e:
            print(f"Error extracting equations: {str(e)}")
            return []

    def _get_equation_context(self, text: str, start_pos: int, end_pos: int, context_size: int = 100) -> str:
        """Get surrounding context for an equation."""
        # Get context before equation
        context_start = max(0, start_pos - context_size)
        before_context = text[context_start:start_pos].strip()

        # Get context after equation
        context_end = min(len(text), end_pos + context_size)
        after_context = text[end_pos:context_end].strip()

        # Combine contexts
        return f"{before_context} ... {after_context}"

    def _extract_symbols(self, equation: str) -> List[Symbol]:
        """Extract mathematical symbols from equation."""
        symbols = []

        # Common mathematical symbols
        greek_letters = [
            "alpha",
            "beta",
            "gamma",
            "delta",
            "epsilon",
            "zeta",
            "eta",
            "theta",
            "iota",
            "kappa",
            "lambda",
            "mu",
            "nu",
            "xi",
            "omicron",
            "pi",
            "rho",
            "sigma",
            "tau",
            "upsilon",
            "phi",
            "chi",
            "psi",
            "omega",
        ]

        operators = [
            "sum",
            "prod",
            "int",
            "oint",
            "partial",
            "nabla",
            "infty",
            "pm",
            "mp",
            "times",
            "div",
            "cdot",
            "equiv",
            "approx",
            "propto",
        ]

        # Look for Greek letters
        for letter in greek_letters:
            pattern = rf"\\{letter}\b"
            if re.search(pattern, equation):
                symbols.append(Symbol(symbol=f"\\{letter}", type="greek", latex_command=f"\\{letter}"))

        # Look for operators
        for op in operators:
            pattern = rf"\\{op}\b"
            if re.search(pattern, equation):
                symbols.append(Symbol(symbol=f"\\{op}", type="operator", latex_command=f"\\{op}"))

        return symbols
