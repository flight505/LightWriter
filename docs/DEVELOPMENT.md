# Development Guide

## Environment Setup

1. **Python Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Dependencies**
   ```bash
   # Install development dependencies
   uv pip install -e ".[dev]"
   
   # Install Anystyle
   gem install anystyle-cli
   ```

## Project Structure

```
Lightwriter_CLI/
├── src/
│   ├── core/                  # Core functionality
│   │   ├── extractors/        # Content extraction
│   │   │   ├── pdf.py        # PDF text extraction
│   │   │   ├── identifier.py # DOI/arXiv extraction
│   │   │   ├── reference.py  # Reference extraction
│   │   │   └── equation.py   # Equation extraction
│   │   ├── metadata/         # Metadata handling
│   │   │   ├── models.py     # Data models
│   │   │   └── consolidator.py # Metadata consolidation
│   │   └── store/           # Storage components
│   │       ├── lightrag.py  # LightRAG integration
│   │       └── manager.py   # Store management
│   ├── processing/          # Processing pipeline
│   │   ├── pipeline.py     # Main pipeline
│   │   └── steps.py       # Processing steps
│   └── utils/             # Utilities
│       ├── constants.py   # Configuration
│       └── logger.py     # Logging setup
├── tests/               # Test suite
├── docs/               # Documentation
└── pyproject.toml     # Project configuration
```

## Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Run Tests**
   ```bash
   # Run all tests
   python -m pytest
   
   # Run specific test file
   python -m pytest tests/test_extractors.py
   
   # Run with coverage
   python -m pytest --cov=src
   ```

3. **Code Style**
   - Follow PEP 8
   - Use type hints
   - Write docstrings (Google style)
   - Keep functions focused and small

4. **Error Handling**
   - Use try/except blocks
   - Log errors with context
   - Return meaningful error messages

## Adding New Features

1. **New Extractor**
   - Create new file in `src/core/extractors/`
   - Implement extractor class
   - Add to pipeline in `src/processing/pipeline.py`
   - Create tests in `tests/`

2. **New Processing Step**
   - Add step class in `src/processing/steps.py`
   - Implement `process()` method
   - Update pipeline to include step
   - Add tests

3. **New Store Feature**
   - Modify store components in `src/core/store/`
   - Update store manager if needed
   - Add tests for new functionality

## Testing

### Test Organization

- `test_extractors.py`: Test content extraction
- `test_store.py`: Test storage components
- `test_pdf_processing.py`: End-to-end tests

### Test Data

- Use files in `tests/pdfs/` for testing
- Keep test files small and focused
- Include various edge cases

### Mocking

- Mock external APIs in tests
- Use `unittest.mock` for mocking
- Create realistic mock responses

## Documentation

1. **Code Documentation**
   - Write clear docstrings
   - Include type hints
   - Document exceptions

2. **API Documentation**
   - Update `docs/API.md`
   - Include examples
   - Document changes

3. **README**
   - Keep installation current
   - Update usage examples
   - List new features

## Common Tasks

### Adding Dependencies

1. Update `pyproject.toml`:
   ```toml
   [project]
   dependencies = [
       "new-package",
   ]
   ```

2. Install dependencies:
   ```bash
   uv pip install -e .
   ```

### Running Specific Tests

```bash
# Run tests matching pattern
python -m pytest -k "test_pdf"

# Run tests with print output
python -m pytest -s

# Run tests verbosely
python -m pytest -v
```

### Debugging

1. Use logging:
   ```python
   from ..utils.logger import logger
   logger.debug("Debug message")
   ```

2. Use debugger:
   ```python
   import pdb; pdb.set_trace()
   ```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create GitHub release
6. Publish to PyPI

## Troubleshooting

### Common Issues

1. **PDF Extraction Fails**
   - Check PDF is readable
   - Verify marker installation
   - Check file permissions

2. **Reference Extraction Fails**
   - Verify DOI/arXiv ID
   - Check API access
   - Verify Anystyle installation

3. **Store Issues**
   - Check file permissions
   - Verify store path exists
   - Check disk space

### Getting Help

1. Check existing issues
2. Create detailed bug report
3. Include:
   - Error message
   - Steps to reproduce
   - Environment details
   - Sample file (if possible) 