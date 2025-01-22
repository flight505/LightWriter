# Lightwriter CLI

A command-line tool for processing academic papers, extracting metadata, and building a searchable knowledge base.

## Features

- **PDF Processing**: Extract text and markdown content from academic PDFs using marker
- **Identifier Extraction**: Automatically extract DOI and arXiv identifiers using pdf2doi
- **Reference Extraction**: Get references from Crossref API with fallback to Anystyle parsing
- **Equation Extraction**: Extract and contextualize mathematical equations from papers
- **Metadata Storage**: Consolidated JSON storage of paper metadata
- **Search**: Full-text and semantic search using LightRAG

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Lightwriter_CLI.git
cd Lightwriter_CLI

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### Additional Requirements

- **Anystyle**: For reference parsing fallback
  ```bash
  gem install anystyle-cli
  ```

## Usage

### Basic Usage

```bash
lightwriter process path/to/paper.pdf
```

### Search

```bash
lightwriter search "your query here"
```

### Store Management

```bash
# Get store statistics
lightwriter stats

# Remove a document
lightwriter remove path/to/paper.pdf
```

## Project Structure

```
Lightwriter_CLI/
├── src/
│   ├── core/
│   │   ├── extractors/      # PDF, DOI, reference, equation extractors
│   │   ├── metadata/        # Metadata models and consolidation
│   │   └── store/          # LightRAG store implementation
│   ├── processing/         # Processing pipeline
│   └── utils/             # Constants, logging, etc.
├── tests/                 # Test suite
└── pyproject.toml        # Project configuration
```

## Components

### Extractors

- **PDFExtractor**: Uses marker to convert PDFs to text/markdown
- **IdentifierExtractor**: Extracts DOI/arXiv IDs using pdf2doi
- **ReferenceExtractor**: Gets references from Crossref or parses with Anystyle
- **EquationExtractor**: Extracts equations with context from markdown

### Store

- **MetadataConsolidator**: Manages JSON metadata storage
- **LightRAGStore**: Handles document indexing and search
- **StoreManager**: High-level store operations

### Processing

- **ProcessingPipeline**: Coordinates extraction and storage steps
- **ProcessingSteps**: Individual processing steps with error handling

## Development

### Running Tests

```bash
python -m pytest
```

### Adding New Features

1. Implement feature in appropriate module
2. Add tests in `tests/` directory
3. Update documentation
4. Submit pull request

## Configuration

Key settings in `src/utils/constants.py`:
- `DEFAULT_STORE_PATH`: Location of metadata and index files
- `DEFAULT_CHUNK_SIZE`: Text chunk size for indexing
- `DEFAULT_OVERLAP`: Chunk overlap for better context

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

## License

MIT License 