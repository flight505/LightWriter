# Lightwriter CLI API Documentation

## Core Components

### PDFExtractor

```python
class PDFExtractor:
    """Extract text and markdown from PDF files."""
    
    def extract_all(self, file_path: Path) -> Dict[str, str]:
        """
        Extract text, markdown and file hash from PDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dict containing 'text', 'markdown' and 'file_hash'
        """
```

### IdentifierExtractor

```python
class IdentifierExtractor:
    """Extract DOI and arXiv identifiers from PDFs."""
    
    def extract_identifier(self, file_path: Path) -> Optional[Dict[str, str]]:
        """
        Extract identifier from PDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dict with 'identifier', 'identifier_type' and 'method'
        """
```

### ReferenceExtractor

```python
class ReferenceExtractor:
    """Extract references using Crossref API and Anystyle."""
    
    def extract_references(
        self,
        identifier: str,
        identifier_type: str,
        text: Optional[str] = None
    ) -> List[Reference]:
        """
        Extract references from identifier or text.
        
        Args:
            identifier: DOI or arXiv ID
            identifier_type: 'doi' or 'arxiv'
            text: Optional text for Anystyle fallback
            
        Returns:
            List of Reference objects
        """
```

### EquationExtractor

```python
class EquationExtractor:
    """Extract equations with context from markdown."""
    
    def extract_equations(self, markdown: str) -> List[Equation]:
        """
        Extract equations from markdown text.
        
        Args:
            markdown: Markdown text
            
        Returns:
            List of Equation objects with content and context
        """
```

## Store Components

### MetadataConsolidator

```python
class MetadataConsolidator:
    """Consolidate and manage document metadata."""
    
    def consolidate_metadata(
        self,
        file_path: Path,
        file_hash: str,
        identifier_info: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        references: Optional[list] = None,
        equations: Optional[list] = None,
        errors: Optional[list] = None
    ) -> DocumentMetadata:
        """
        Consolidate metadata from various sources.
        
        Args:
            file_path: Path to source file
            file_hash: File hash
            identifier_info: DOI/arXiv info
            metadata: Additional metadata
            references: Extracted references
            equations: Extracted equations
            errors: Processing errors
            
        Returns:
            DocumentMetadata object
        """
```

### LightRAGStore

```python
class LightRAGStore:
    """Manage document storage and retrieval using LightRAG."""
    
    def add_document(self, metadata: Dict[str, Any]) -> bool:
        """
        Add document to store.
        
        Args:
            metadata: Document metadata
            
        Returns:
            Success status
        """
    
    def search(
        self,
        query: str,
        mode: str = "hybrid",
        max_results: int = 5,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Search documents.
        
        Args:
            query: Search query
            mode: Search mode ('hybrid', 'semantic', 'keyword')
            max_results: Maximum results
            include_metadata: Include document metadata
            
        Returns:
            Search results
        """
```

### StoreManager

```python
class StoreManager:
    """High-level store management."""
    
    def add_document(self, file_path: Path, metadata: Dict[str, Any]) -> bool:
        """
        Add document to stores.
        
        Args:
            file_path: Source file path
            metadata: Document metadata
            
        Returns:
            Success status
        """
    
    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Search documents.
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            Search results
        """
```

## Processing Components

### ProcessingPipeline

```python
class ProcessingPipeline:
    """Coordinate document processing steps."""
    
    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Process document through pipeline.
        
        Args:
            file_path: Path to document
            
        Returns:
            Processing results with status
        """
```

### ProcessingStep

```python
class ProcessingStep(ABC):
    """Base class for processing steps."""
    
    @abstractmethod
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process step and update context.
        
        Args:
            context: Processing context
            
        Returns:
            Updated context
        """
```

## Data Models

### DocumentMetadata

```python
class DocumentMetadata(BaseModel):
    """Document metadata model."""
    
    file_path: str
    file_hash: str
    title: str = ""
    authors: List[Author] = []
    abstract: Optional[str] = None
    year: Optional[int] = None
    identifier: Optional[str] = None
    identifier_type: Optional[str] = None
    extraction_method: Optional[str] = None
    references: List[Reference] = []
    equations: List[Equation] = []
    errors: List[str] = []
```

### Reference

```python
class Reference(BaseModel):
    """Reference metadata model."""
    
    title: str = ""
    authors: List[Author] = []
    year: Optional[int] = None
    doi: Optional[str] = None
    raw_text: str = ""
```

### Equation

```python
class Equation(BaseModel):
    """Equation metadata model."""
    
    content: str
    context: str
    equation_type: str = "inline"  # inline, display, numbered
``` 