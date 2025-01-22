# LightWriter CLI Development Guide

## Table of Contents
1. [Project Objective](#1-project-objective)
2. [Pre-Development Analysis](#2-pre-development-analysis)
3. [Core Functionality](#3-core-functionality)
4. [Development Process](#4-development-process)
5. [Implementation Guide](#5-implementation-guide)
6. [Testing Strategy](#6-testing-strategy)
7. [Best Practices & Common Pitfalls](#7-best-practices--common-pitfalls)
8. [Code Examples](#8-code-examples)
9. [Migration Checklist](#9-migration-checklist)
10. [Framework Separation Strategy](#10-framework-separation-strategy)
11. [Performance Considerations](#11-performance-considerations)
12. [Command Implementation Examples](#12-command-implementation-examples)
13. [Detailed Migration Steps](#13-detailed-migration-steps)
    - [13.1 Document Core Functionalities and Their TUI Mappings](#131-document-core-functionalities-and-their-tui-mappings)
    - [13.2 Map Web Dependencies to Textual Components](#132-map-web-dependencies-to-textual-components)
    - [13.3 List Existing CLI Commands and Their TUI Counterparts](#133-list-existing-cli-commands-and-their-tui-counterparts)
14. [Additional Considerations](#14-additional-considerations)
15. [Final Thoughts](#15-final-thoughts)

---

## 1. Project Objective

### 1.1 Overview
Transform LightWriter into a focused command-line interface (CLI) application, creating a clean, well-structured project using Typer, questionary, and Rich console for an enhanced user experience.

LightWriter is an advanced academic research framework that seamlessly integrates knowledge graph (KG) architectures with retrieval-augmented generation (RAG) techniques to facilitate comprehensive analysis and synthesis of scholarly literature. The system employs a robust pipeline for processing academic papers, which includes automated PDF text extraction using Marker, DOI and arXiv identification via pdf2doi, and metadata enrichment through CrossRef and arXiv APIs. Leveraging Anystyle for precise reference extraction and specialized modules for equation metadata processing, LightWriter constructs a highly interconnected semantic knowledge graph. This graph serves as the backbone for sophisticated query answering and context-aware content generation, enabling the extraction and utilization of intricate relationships and entities within the academic domain.

### 1.2 Key Goals
1. **Core Functionality**: Preserve essential academic paper processing:
   - PDF text extraction (Marker)
   - DOI/arXiv identification (pdf2doi)
   - Metadata fetching (CrossRef/arXiv APIs)
   - Reference extraction (Anystyle)
   - Equation metadata processing
   - Knowledge graph capabilities

2. **CLI Architecture**:
   - Typer for command-line interface
   - questionary for interactive prompts
   - Rich console for enhanced output
   - Efficient state management
   - Clear separation of concerns

3. **User Experience**:
   - Intuitive command structure
   - Interactive prompts when needed
   - Rich progress indicators
   - Clear error messages
   - Colorful and informative output

4. **Quality**:
   - Comprehensive test coverage
   - Proper error handling
   - Python best practices
   - Code maintainability

### 1.3 Core Processing Chain
```
PDF -> pdf2doi -> DOI/arXiv ID -> CrossRef/arXiv API -> Metadata -> Anystyle -> Raw References
```

## 2. Pre-Development Analysis

### 2.1 Core Processing Chain to Preserve
```
PDF -> pdf2doi -> DOI/arXiv ID -> CrossRef/arXiv API -> Metadata -> Anystyle -> Raw References
```

### 2.2 Critical Test Files
- `tests/*`
- `tests/test_citation_processor.py`
- `tests/test_metadata.py`

### 2.3 Critical Rules
1. **DO NOT**:
   - Modify working PDF processing pipeline
   - Change store structure
   - Remove error handling
   - Modify test assertions

2. **DO**:
   - Read test files first
   - Preserve metadata extraction
   - Maintain processing chain
   - Keep equation/citation extraction
   - Check the real-time project monitoring file periodically to see current progress and file status, the file is `Focus.md`

## 3. Core Functionality

### 3.1 Required Final Directory Structure
```
store/
├── documents/     # Original PDFs
├── metadata/      # Extracted metadata
├── converted/     # Converted text
├── cache/         # Processing cache
└── exports/       # Generated exports
```

### 3.2 Required Files
1. **Metadata Files**:
   - `metadata.json`
   - `consolidated.json`

### 3.3 Processing Pipeline
1. PDF Text Extraction
2. Identifier Detection
3. Metadata Retrieval
4. Reference Processing
5. Equation Analysis

## 4. Development Process

### 4.2 Implementation Order
1. **Phase 1: CLI Foundation**
   - Basic Typer app structure
   - Core command groups
   - Rich console integration

2. **Phase 2: Core Features**
   - Document processing
   - Store operations
   - Search functionality

3. **Phase 3: Enhanced UX**
   - Interactive prompts
   - Progress indicators
   - Error handling

4. **Phase 4: Polish**
   - Documentation
   - Testing
   - Performance optimization

## 5. Implementation Guide

### 5.1 Project Structure
```
cli/
├── __init__.py
├── main.py           # Typer app entry point
└── commands/         # Command modules
    ├── pdf.py       # PDF processing commands
    ├── store.py     # Store management
    ├── search.py    # Search functionality
    └── metadata.py  # Metadata operations
```

### 5.2 Command Implementation
1. **Store Commands** (First)
   - Create/delete stores
   - List contents
   - Validate structure

2. **PDF Commands** (Second)
   - Process documents
   - Extract metadata
   - Convert formats

3. **Search Commands** (Third)
   - Query documents
   - Generate graphs
   - Analyze content

### 5.3 Progress Handling
```python:cli/commands/pdf.py
def process_file(self, file_path: str, progress_callback: Optional[Callable] = None):
    try:
        if progress_callback:
            progress_callback(0, 100)
        # Processing steps...
        if progress_callback:
            progress_callback(100, 100)
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise
```

## 6. Testing Strategy

### 6.1 Test Structure
```
tests/
├── conftest.py      # Shared fixtures
├── test_processor.py
└── cli/
    ├── test_pdf.py
    ├── test_store.py
    └── test_search.py
```

### 6.2 Test Implementation
```python:tests/cli/test_pdf.py
def test_process_command(runner):
    """Test basic PDF processing."""
    result = runner.invoke(cli, [
        'pdf', 'process', 
        'tests/pdfs/sample.pdf', 
        'test_store'
    ])
    assert result.exit_code == 0
    assert "Processing complete" in result.output
```

### 6.3 Test Fixtures
```python:tests/conftest.py
@pytest.fixture
def test_env(tmp_path):
    """Setup test environment."""
    # Setup store
    store_path = setup_test_store(tmp_path)
    
    # Copy test files
    test_files = setup_test_files(tmp_path)
    
    yield {
        "store_path": store_path,
        "test_files": test_files
    }
    
    # Cleanup
    cleanup_test_env(tmp_path)
```

## 7. Best Practices & Common Pitfalls

### 7.1 Store Management
- **Problem**: Store validation fails
- **Solution**:
  ```python:cli/commands/store.py
  def create_store(name: str):
      store_path = Path(name)
      # Create ALL directories first
      for dir_name in ["documents", "metadata", "converted", "cache"]:
          (store_path / dir_name).mkdir(parents=True, exist_ok=True)
      # Initialize metadata files
      init_metadata_files(store_path)
  ```

### 7.2 Error Handling
- **Problem**: Silent failures
- **Solution**:
  ```python:cli/commands/pdf.py
  def process_pdf(file_path: str):
      # 1. Validate file
      if not Path(file_path).exists():
          raise FileNotFoundError(f"PDF not found: {file_path}")
      
      # 2. Validate store
      if not validate_store_structure(store_path):
          raise ValueError("Invalid store structure")
      
      # 3. Process with error handling
      try:
          result = process_with_marker(file_path)
          if not result:
              raise ProcessingError("No text extracted")
      except Exception as e:
          raise ProcessingError(f"Processing failed: {str(e)}")
  ```

## 8. Code Examples

### 8.1 Command Group Example
```python:cli/commands/pdf.py
def pdf():
    """PDF processing commands."""
    pass

@pdf.command()
def process(file: str, store: str):
    """Process a PDF file."""
    try:
        processor = DocumentProcessor()
        result = processor.process_file(Path(file))
        console.print("✓ Processing complete", style="green")
    except Exception as e:
        console.print(f"Error: {str(e)}", style="red")
        raise Abort()
```

### 8.2 Search Implementation
```python:cli/commands/search.py
@search.command()
def query(query: str, store: str, mode: str = typer.Option('mix', help='Search mode')):
    """Search documents in store."""
    try:
        results = search_documents(query, store, mode=mode)
        display_results(results)
    except Exception as e:
        handle_error(e)
        raise Abort()
```

## 9. Migration Checklist

### 9.1 Before Starting
- [ ] Backup codebase
- [ ] Document core functionality
- [ ] Map web dependencies
- [ ] List CLI commands

### 9.2 During Migration
- [ ] Remove web files systematically
- [ ] Test after each removal
- [ ] Track broken dependencies
- [ ] Document API changes

### 9.3 After Migration
- [ ] Verify core functionality
- [ ] Run all tests
- [ ] Check CLI commands
- [ ] Update docs 

## 10. Framework Separation Strategy

### 10.2 Progress Handling Separation
```python:src/processing/base.py
from typing import Protocol
from pathlib import Path

class ProgressCallback(Protocol):
    def update(self, current: int, total: int): ...

class BaseProcessor:
    def __init__(self, progress_callback: Optional[ProgressCallback] = None):
        self.progress_callback = progress_callback

    def process_file(self, file_path: Path):
        if self.progress_callback:
            self.progress_callback.update(1, 100)
```

### 10.3 Error Handling Hierarchy
```python:src/processing/base.py
class LightRAGError(Exception):
    """Base exception for all LightRAG errors"""
    pass

class PDFProcessingError(LightRAGError):
    """PDF processing specific errors"""
    pass

class MetadataError(LightRAGError):
    """Metadata handling errors"""
    pass

def handle_error(error: LightRAGError):
    error_styles = {
        PDFProcessingError: "red bold",
        MetadataError: "yellow bold",
        LightRAGError: "red"
    }
    style = error_styles.get(type(error), "red")
    console.print(f"Error: {str(error)}", style=style)
```

## 11. Performance Considerations

### 11.1 Caching Strategy
1. Use `lru_cache` for expensive operations:
```python:src/processing/document_processor.py
from functools import lru_cache
from typing import Dict, Any

class DocumentProcessor:
    @lru_cache(maxsize=32)
    def process_document(self, file_path: str) -> Dict[str, Any]:
        # Expensive document processing
        pass
```

2. Cache API responses:
```python:src/utils/api_cache.py
import json
from pathlib import Path
from typing import Optional, Dict

class APICache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

    def get_cached_response(self, key: str) -> Optional[Dict]:
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text())
        return None

    def cache_response(self, key: str, data: Dict):
        cache_file = self.cache_dir / f"{key}.json"
        cache_file.write_text(json.dumps(data))
```

### 11.2 Memory Management
1. Process large PDFs in chunks:
```python:src/processing/large_pdf_processor.py
def process_large_pdf(file_path: str, chunk_size: int = 1000):
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            process_chunk(chunk)
            yield len(chunk)
```

2. Use generators for large datasets:
```python:src/search/document_search.py
from pathlib import Path

def search_documents(query: str, store_path: Path):
    for doc_path in store_path.glob('**/*.pdf'):
        if match := search_single_doc(doc_path, query):
            yield match
```

## 12. Command Implementation Examples

Refer to Code Examples section for detailed implementations.

## 13. Detailed Migration Steps

To ensure a smooth transition from your existing web-based or CLI application to a Textual-based TUI, it's essential to methodically document how each core functionality and dependency will be mapped and adapted. This section provides detailed steps for:
1. Documenting Core Functionalities and Their TUI Mappings.
2. Mapping Web Dependencies to Textual Components.
3. Listing Existing CLI Commands and Determining Their TUI Counterparts.

### 13.1 Document Core Functionalities and Their TUI Mappings

**Objective:**  
Identify each core functionality of LightRAG and determine how it will be represented within the Textual-based TUI.

**Approach:**  
Create a comprehensive table that maps each core functionality to its corresponding TUI component or workflow. This ensures that all essential features are accounted for and appropriately integrated into the new interface.

**Core Functionalities Mapping:**

| **Core Functionality**                                         | **Description**                                                                                       | **TUI Component/Mapping**                                    | **Notes**                                                                 |
|----------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|--------------------------------------------------------------|--------------------------------------------------------------------------|
| **PDF Text Extraction (Marker)**                               | Extracts text content from PDF documents.                                                            | **Processing Widget**: Display progress bar and status.      | Use a dedicated section for uploading/selecting PDFs and initiating processing. |
| **DOI/arXiv Identification (pdf2doi)**                        | Identifies DOIs and arXiv IDs from PDFs.                                                              | **Processing Widget**: Show extracted identifiers alongside PDF details. | Integrate within the PDF processing workflow in the TUI.                 |
| **Metadata Fetching (CrossRef/arXiv APIs)**                    | Retrieves metadata based on identified DOIs/arXiv IDs.                                                | **Metadata Management Widget**: Display and edit metadata.   | Allow users to view, confirm, or manually edit fetched metadata.          |
| **Reference Extraction (Anystyle)**                             | Extracts references from the PDF content.                                                             | **Processing Widget**: Show list of extracted references.    | Include options to export or analyze references further.                 |
| **Equation Metadata Processing**                               | Processes and extracts metadata related to equations within the documents.                           | **Processing Widget**: Display equations and related metadata. | Provide tools for searching and analyzing equations.                      |
| **Knowledge Graph Construction**                               | Builds a semantic knowledge graph from the processed data.                                           | **Dashboard Widget**: Visualize the knowledge graph.         | Integrate graph visualization libraries compatible with Textual if needed. |
| **Agent-Driven Tasks (Synthesis, Hypothesis Generation, Draft Composition)** | Autonomous agents perform specialized tasks using the knowledge graph.                               | **Agents Management Widget**: Control and monitor agents.    | Provide controls to start, stop, and monitor agent activities.           |
| **State Management and Caching**                               | Manages the application state and caches processed data for efficiency.                             | **Backend Integration**: Ensure state and cache are managed outside the TUI. | TUI should reflect the current state but not manage it directly.         |
| **Error Handling and Logging**                                 | Captures and displays errors and logs for debugging and user information.                           | **Notifications and Alerts**: Display error messages and logs. | Use modal dialogs or notification banners for errors and important messages. |
| **Progress Indicators**                                        | Shows real-time progress of long-running operations like processing or fetching data.               | **Progress Bars**: Integrated within processing widgets.     | Utilize Textual's built-in progress bar components for visual feedback.   |
| **User Authentication (if applicable)**                        | Handles user login and authentication (assuming it exists in the web version).                      | **Login Widget**: Securely capture and manage user credentials. | Ensure security best practices are followed for handling sensitive data.   |
| **Export and Import Functionality**                            | Allows exporting processed data and importing data from other sources.                               | **Export/Import Widgets**: Provide interfaces for data operations. | Facilitate file browsing and selection within the TUI.                    |
| **Search Functionality**                                       | Enables searching within the knowledge graph and processed documents.                               | **Search Widget**: Input fields and result displays.         | Implement advanced search features with filtering options.                |
| **Store Management**                                           | Create, delete, list, and manage data stores.                                                        | **Store Management Widget**: Interface for managing stores.  | Align with existing store management logic from CLI/Web versions.         |
| **User Preferences and Settings**                              | Allow users to configure application settings and preferences.                                      | **Settings Widget**: Forms and toggles for various settings. | Persist user settings and provide a user-friendly interface for adjustments. |

**Detailed Descriptions:**

1. **Processing Widget:**
   - **Purpose:** Handle all document processing tasks, including PDF extraction, DOI identification, metadata fetching, reference extraction, and equation processing.
   - **Features:**
     - Upload or select PDF files for processing.
     - Display progress bars indicating the status of each processing step.
     - Show real-time updates and results of each processing stage.
     - Provide options to pause, resume, or cancel processing tasks.

2. **Metadata Management Widget:**
   - **Purpose:** Display and manage metadata fetched from external APIs.
   - **Features:**
     - List of documents with associated metadata.
     - Editable fields for manual corrections or additions.
     - Options to save, export, or synchronize metadata.

3. **Dashboard Widget:**
   - **Purpose:** Provide an overview of the knowledge graph and overall application status.
   - **Features:**
     - Visual representation of the knowledge graph (nodes and edges).
     - Statistics on processed documents, references, and equations.
     - Quick access to recent activities and summaries.

4. **Agents Management Widget:**
   - **Purpose:** Control and monitor autonomous agents performing specialized tasks.
   - **Features:**
     - List of active agents with their current tasks.
     - Controls to start, stop, or configure agents.
     - Logs and status updates for each agent.

5. **Store Management Widget:**
   - **Purpose:** Manage data stores including creation, deletion, and listing.
   - **Features:**
     - Forms to create new stores.
     - Options to delete existing stores with confirmation prompts.
     - Display of all available stores with their statuses.

6. **Search Widget:**
   - **Purpose:** Enable users to search within the knowledge graph and processed documents.
   - **Features:**
     - Input fields for search queries with advanced filtering options.
     - Display of search results in a structured format (e.g., tables).
     - Options to navigate to specific documents or graph nodes from results.

7. **Export/Import Widgets:**
   - **Purpose:** Facilitate exporting processed data and importing data from other sources.
   - **Features:**
     - File selection dialogs for importing/exporting data.
     - Status indicators for ongoing export/import operations.
     - Logs or summaries of completed actions.

8. **Settings Widget:**
   - **Purpose:** Allow users to configure application settings and preferences.
   - **Features:**
     - Toggle switches, dropdowns, and input fields for various settings.
     - Options to customize themes, logging levels, and processing parameters.
     - Save and reset buttons for applying or discarding changes.

**Benefits of This Mapping:**
- **Clarity:** Each core functionality has a dedicated TUI component, ensuring organized and intuitive navigation.
- **Modularity:** Facilitates maintenance and future enhancements by isolating functionalities within specific widgets.
- **User Experience:** Enhances usability by providing visual feedback, structured layouts, and interactive elements.

### 13.2 Map Web Dependencies to Textual Components

**Objective:**  
Identify dependencies from the existing web-based application and map them to equivalent or alternative components within the Textual framework to ensure seamless functionality in the TUI.

**Approach:**  
Review each web dependency and determine how its functionality can be replicated or adapted within Textual. Replace web-specific libraries with Textual-compatible alternatives or implement new solutions using Textual's capabilities.

**Dependency Mapping:**

| **Web Dependency**                                    | **Purpose in Web Application**                                  | **Textual Equivalent/Alternative**                                      | **Notes**                                                                                      |
|-------------------------------------------------------|----------------------------------------------------------------|------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| **Flask/Django/FastAPI**                              | Backend web framework handling HTTP requests and routing.      | **Python Modules and Textual App**                                     | Replace web routing with TUI navigation and command handling. Utilize Python modules directly.  |
| **React/Vue/Angular**                                 | Frontend JavaScript frameworks for building dynamic UIs.       | **Textual Widgets and Layouts**                                        | Use Textual's built-in widgets, custom widgets, and layout management for dynamic interfaces.    |
| **RESTful APIs**                                      | Communication between frontend and backend via HTTP.            | **Direct Function Calls or IPC**                                       | Replace HTTP API calls with direct function invocations or inter-process communication if needed.|
| **WebSockets**                                        | Real-time communication between client and server.             | **Textual's Event Loop and Async Features**                            | Utilize Textual's asynchronous capabilities to handle real-time updates.                        |
| **JavaScript Libraries (e.g., D3.js for graphs)**     | Data visualization in the frontend.                            | **Rich Libraries (e.g., Rich's built-in tables, Textual's graph widgets)** | Use Rich for text-based visualizations; for complex graphs, explore integrating with libraries that can render in the terminal or use simplified representations. |
| **CSS/Styled Components**                             | Styling and theming of web components.                          | **Textual's Theming and Styling Options**                              | Leverage Textual's theming system to style widgets and overall application appearance.          |
| **HTML Templates**                                    | Structuring content in the web frontend.                        | **Textual Layouts and Widgets**                                        | Organize content using Textual's layout management and widget hierarchy.                        |
| **Database ORMs (e.g., SQLAlchemy, Django ORM)**      | Managing database interactions.                                 | **Direct ORM Usage or Textual-Integrated Data Handlers**               | Continue using existing ORMs; integrate them with Textual's backend components.                  |
| **Authentication Libraries (e.g., OAuth, JWT)**       | Handling user authentication and authorization.                | **Python Authentication Libraries**                                    | Use Python libraries for authentication and manage sessions within the Textual app as needed.    |
| **Form Handling Libraries (e.g., WTForms)**           | Managing user input forms in the web interface.                | **Textual Input Widgets (e.g., Input, Forms)**                        | Implement forms using Textual's input widgets and handle validation within the TUI logic.        |
| **File Upload Mechanisms (e.g., multipart/form-data)** | Uploading files from the user to the server.                   | **Textual File Selection and Upload Widgets**                          | Provide file browsing and selection dialogs within the TUI for uploading documents.              |
| **Session Management**                                | Maintaining user sessions across requests.                     | **State Management within Textual App**                                | Manage application state using Textual's reactive system and state management features.          |
| **Logging Libraries (e.g., Loguru)**                  | Logging application activities and errors.                      | **Python Logging Module**                                              | Continue using Python's logging module, integrating log displays within the TUI if needed.       |
| **Error Tracking Services (e.g., Sentry)**            | Monitoring and tracking application errors.                      | **Local Error Handling and Logging**                                  | Implement robust local error handling; consider integrating with remote error tracking if necessary. |

**Detailed Mapping Examples:**

1. **Frontend Frameworks (React/Vue/Angular) to Textual Widgets:**
   - **Component Replacement:**
     - **React Components:** Replace with **Textual Widgets**. For example, a React `Button` can be replaced with Textual's `Button` widget.
     - **State Management (Redux):** Utilize Textual's reactive properties or Python's state management to handle application state.
     - **Routing (React Router):** Implement navigation between different TUI screens using Textual's routing or screen management features.

2. **Data Visualization Libraries (D3.js) to Rich/Textual Alternatives:**
   - **Graph Visualization:**
     - **D3.js:** Highly interactive and customizable.
     - **Textual:** Use Rich's `Table` and `Panel` widgets for structured data display. For simple graphs, leverage Textual's drawing capabilities or integrate ASCII-based graph representations.
     - **Advanced Visualization:** If complex visualizations are necessary, consider generating images and displaying them as static assets within the TUI or using terminal-based graph libraries compatible with Textual.

3. **WebSockets to Textual's Asynchronous Event Handling:**
   - **Real-Time Updates:**
     - **WebSockets:** Used for pushing real-time data to the frontend.
     - **Textual:** Use asynchronous tasks and event handlers to push updates to the TUI dynamically. Textual's event loop can manage real-time data without needing WebSockets.

4. **CSS/Theming to Textual's Theming System:**
   - **Styling:**
     - **CSS:** Defines the look and feel of web components.
     - **Textual:** Utilize Textual's theming capabilities to style widgets and overall application appearance. Customize colors, fonts, and layouts using Textual's configuration files or theming APIs.

5. **HTML Templates to Textual Layouts:**
   - **Content Structuring:**
     - **HTML Templates:** Define the structure of web pages.
     - **Textual:** Use Textual's layout management to arrange widgets within the TUI. Organize content using containers, grids, and hierarchical widget structures.

**Benefits of Mapping Dependencies:**
- **Seamless Transition:** Ensures that all functionalities from the web application are accounted for in the TUI.
- **Consistency:** Maintains feature parity between the web and TUI versions, providing users with a similar experience.
- **Maintainability:** Keeps the codebase organized by clearly separating TUI components from processing logic.

### 13.3 List Existing CLI Commands and Determine Their TUI Counterparts

**Objective:**  
Map each existing CLI command to its equivalent functionality within the Textual-based TUI. This ensures that all command-line capabilities are accessible through the TUI interface, providing users with both interactive and scripted usage options.

**Approach:**  
Create a table that lists all existing CLI commands, their descriptions, and how they will be represented or replaced within the TUI. This facilitates comprehensive coverage of features and ensures no functionality is lost during the transition.

**Existing CLI Commands Mapping:**

| **CLI Command**                         | **Description**                                                        | **TUI Counterpart**                                              | **Notes**                                                                                      |
|-----------------------------------------|------------------------------------------------------------------------|------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| `lightrag store create <name>`          | Create a new document store with the specified name.                  | **Store Management Widget**: "Create Store" button and input field. | Provide a form within the Store Management interface to input the store name and initiate creation. |
| `lightrag store delete <name>`          | Delete an existing document store by name.                            | **Store Management Widget**: "Delete Store" button and input field with confirmation prompt. | Implement safety measures like confirmation dialogs to prevent accidental deletions.           |
| `lightrag store list`                   | List all existing document stores.                                    | **Store Management Widget**: "List Stores" button with display area. | Display a list within the widget, allowing users to view and select stores for further actions. |
| `lightrag pdf process <file> <store>`   | Process a specified PDF file and store its data in the given store.    | **Processing Widget**: File selection dialog and store selection dropdown/menu. | Allow users to browse and select PDF files and choose the target store through the TUI.          |
| `lightrag search query <query> <store> --mode <mode>` | Search documents within a store using a specified query and mode.    | **Search Widget**: Input fields for query and store selection, mode selection dropdown. | Provide intuitive search forms with options to select search mode and initiate the search.       |
| `lightrag metadata consolidate <store>` | Consolidate metadata within a specified store.                        | **Metadata Management Widget**: "Consolidate Metadata" button and store selection. | Enable users to trigger metadata consolidation through a dedicated button within the widget.    |
| `lightrag export <store> <format>`      | Export data from a store in a specified format (e.g., JSON, CSV).     | **Export/Import Widgets**: Export section with store selection and format options. | Provide dropdowns for selecting export formats and initiate export with progress indicators.     |
| `lightrag import <file> <store>`        | Import data from a specified file into a store.                       | **Export/Import Widgets**: Import section with file selection and store selection. | Allow users to browse and select files for import, associating them with the chosen store.        |
| `lightrag agent start <agent_name>`     | Start a specific autonomous agent (e.g., synthesis, hypothesis generation). | **Agents Management Widget**: List of agents with "Start" buttons. | Display available agents and provide controls to start or stop each agent as needed.            |
| `lightrag agent stop <agent_name>`      | Stop a running autonomous agent.                                       | **Agents Management Widget**: List of running agents with "Stop" buttons. | Allow users to manage agent activities directly through the TUI interface.                      |
| `lightrag config set <key> <value>`     | Set a configuration parameter.                                         | **Settings Widget**: Input fields or toggle switches for configuration parameters. | Facilitate easy configuration adjustments through interactive forms within the TUI.            |
| `lightrag config get <key>`             | Retrieve the value of a configuration parameter.                       | **Settings Widget**: Display current configuration values.      | Show current settings within the Settings Widget, allowing users to view and modify them.      |
| `lightrag help`                         | Display help information for LightRAG commands.                       | **Help Section Widget**: Integrated help screens or tooltips within the TUI. | Include accessible help documentation within the TUI, possibly via a dedicated Help widget or modal dialogs. |

**Detailed Mapping Examples:**

1. **Store Management Commands:**
   - **CLI Command:** `lightrag store create <name>`
   - **TUI Counterpart:**  
     - **Widget:** Store Management Widget
     - **UI Elements:**  
       - **Input Field:** For entering the store name.
       - **Button:** "Create Store" to initiate the creation process.
     - **Workflow:** User navigates to the Store Management section, enters the desired store name into the input field, and clicks the "Create Store" button. Upon successful creation, a confirmation message is displayed within the widget.

2. **PDF Processing Command:**
   - **CLI Command:** `lightrag pdf process <file> <store>`
   - **TUI Counterpart:**  
     - **Widget:** Processing Widget
     - **UI Elements:**  
       - **File Selection Dialog:** To browse and select the PDF file.
       - **Store Selection Dropdown/Menu:** To choose the target store.
       - **Button:** "Process PDF" to start processing.
     - **Workflow:** User selects the PDF file and the target store, then initiates processing. The widget displays real-time progress indicators and status updates.

3. **Search Command:**
   - **CLI Command:** `lightrag search query <query> <store> --mode <mode>`
   - **TUI Counterpart:**  
     - **Widget:** Search Widget
     - **UI Elements:**  
       - **Input Field:** For entering the search query.
       - **Store Selection Dropdown/Menu:** To choose the store to search within.
       - **Mode Selection Dropdown:** To select the search mode (e.g., mix, hybrid, local, global).
       - **Button:** "Search" to execute the query.
     - **Workflow:** User enters the search criteria, selects the desired options, and clicks "Search." Results are displayed within the widget in a structured format.

4. **Agent Management Commands:**
   - **CLI Commands:**  
     - `lightrag agent start <agent_name>`
     - `lightrag agent stop <agent_name>`
   - **TUI Counterpart:**  
     - **Widget:** Agents Management Widget
     - **UI Elements:**  
       - **List/Table:** Display available agents with their current statuses.
       - **Buttons:** "Start" and "Stop" buttons next to each agent.
     - **Workflow:** User views the list of agents, starts or stops agents by clicking the respective buttons, and sees real-time status updates.

5. **Configuration Commands:**
   - **CLI Commands:**  
     - `lightrag config set <key> <value>`
     - `lightrag config get <key>`
   - **TUI Counterpart:**  
     - **Widget:** Settings Widget
     - **UI Elements:**  
       - **Input Fields/Toggles:** For various configuration parameters.
       - **Buttons:** "Save Settings" and "Reset to Defaults."
     - **Workflow:** User navigates to the Settings section, adjusts desired parameters, and saves changes. Current settings are displayed for reference.

6. **Export/Import Commands:**
   - **CLI Commands:**  
     - `lightrag export <store> <format>`
     - `lightrag import <file> <store>`
   - **TUI Counterpart:**  
     - **Widget:** Export/Import Widgets
     - **UI Elements:**  
       - **File Browsers:** For selecting files to export/import.
       - **Dropdowns:** For choosing export formats and target stores.
       - **Buttons:** "Export" and "Import" to initiate actions.
     - **Workflow:** User selects the data to export/import, chooses the desired options, and starts the operation. Progress indicators and success/error messages are displayed accordingly.

**Benefits of Mapping CLI Commands to TUI:**
- **Enhanced Accessibility:** Users can perform all command-line operations through an interactive interface without needing to remember specific command syntax.
- **User-Friendly Experience:** Provides visual cues, structured layouts, and interactive elements that can make complex operations more intuitive.
- **Feature Parity:** Ensures that all functionalities available via the CLI are accessible within the TUI, maintaining consistency and comprehensive feature coverage.
- **Flexibility:** Allows users to choose between interactive TUI usage and traditional CLI scripting based on their preferences and needs.

**Summary of TUI Counterparts**

| **CLI Command**                | **TUI Widget**             | **UI Elements**                                     |
|--------------------------------|----------------------------|-----------------------------------------------------|
| `store create <name>`          | Store Management Widget    | Input Field, "Create Store" Button                  |
| `store delete <name>`          | Store Management Widget    | Input Field, "Delete Store" Button, Confirmation    |
| `store list`                   | Store Management Widget    | "List Stores" Button, Display Area                  |
| `pdf process <file> <store>`   | Processing Widget          | File Selector, Store Dropdown, "Process PDF" Button |
| `search query <query> <store> --mode` | Search Widget          | Query Input, Store Dropdown, Mode Dropdown, "Search" Button |
| `metadata consolidate <store>` | Metadata Management Widget | "Consolidate Metadata" Button, Store Selection      |
| `export <store> <format>`      | Export/Import Widgets      | Store Dropdown, Format Dropdown, "Export" Button    |
| `import <file> <store>`        | Export/Import Widgets      | File Selector, Store Dropdown, "Import" Button      |
| `agent start <agent_name>`     | Agents Management Widget   | "Start" Button next to Agent List                   |
| `agent stop <agent_name>`      | Agents Management Widget   | "Stop" Button next to Agent List                    |
| `config set <key> <value>`     | Settings Widget            | Input Fields, "Save Settings" Button                |
| `config get <key>`             | Settings Widget            | Display Current Settings                            |
| `help`                         | Help Section Widget        | Integrated Help Screens, Tooltips                   |

## 14. Additional Considerations

While the above mappings provide a structured approach to migrating LightRAG to a Textual-based TUI, consider the following additional factors to ensure a comprehensive and user-friendly transition:

### 14.1 User Roles and Permissions
- **Scenario:** If LightRAG supports multiple user roles with varying permissions (e.g., admin, researcher, guest), ensure that the TUI accommodates these roles.
- **Implementation:**
  - **Role-Based Widgets:** Display or hide certain widgets and functionalities based on the user's role.
  - **Authentication Integration:** Secure login mechanisms within the TUI to manage user sessions and permissions.

### 14.2 Internationalization (i18n) and Localization (l10n)
- **Scenario:** Supporting multiple languages can broaden LightRAG's accessibility.
- **Implementation:**
  - **Textual's Support:** Utilize Python's localization libraries (e.g., `gettext`) in conjunction with Textual to manage multi-language support.
  - **Dynamic Content:** Ensure that all textual content within widgets can be translated based on user preferences.

### 14.3 Accessibility
- **Scenario:** Ensuring that the TUI is accessible to users with disabilities (e.g., screen reader compatibility, keyboard navigation).
- **Implementation:**
  - **Keyboard Shortcuts:** Implement comprehensive keyboard navigation to allow efficient use without a mouse.
  - **Screen Reader Support:** While Textual itself may have limitations, strive to use standard text representations and ARIA-like roles where possible.
  - **Contrast and Visibility:** Ensure that color schemes and text contrasts meet accessibility standards.

### 14.4 Performance Optimization
- **Scenario:** Handling large datasets and ensuring the TUI remains responsive.
- **Implementation:**
  - **Asynchronous Processing:** Leverage Textual's asynchronous capabilities to manage long-running tasks without freezing the interface.
  - **Efficient Rendering:** Optimize widget rendering, especially for components like knowledge graphs and large tables.
  - **Resource Management:** Monitor and manage memory usage, especially when dealing with extensive data.

### 14.5 User Training and Onboarding
- **Scenario:** Users transitioning from the web or CLI to the TUI may require guidance.
- **Implementation:**
  - **In-App Tutorials:** Integrate guided walkthroughs or tutorials within the TUI.
  - **Documentation:** Provide comprehensive user manuals and help sections accessible from within the application.
  - **Tooltips and Help Icons:** Embed contextual help elements to assist users in understanding various features.

### 14.6 Integration with Existing Systems
- **Scenario:** LightRAG may need to integrate with other tools or systems used by academic researchers.
- **Implementation:**
  - **API Integrations:** Maintain or develop APIs that allow other applications to interact with LightRAG's backend.
  - **Export Formats:** Ensure that exported data is compatible with commonly used academic tools (e.g., citation managers, data analysis software).

### 14.7 Continuous Improvement and Feedback
- **Scenario:** Gathering user feedback to iteratively improve the TUI.
- **Implementation:**
  - **Feedback Mechanisms:** Incorporate features within the TUI for users to submit feedback or report issues.
  - **Analytics:** If applicable, track usage patterns to identify areas for enhancement.

## 15. Final Thoughts

The implementation of LightWriter as a CLI application using Typer, questionary, and Rich console presents an opportunity to create a powerful, user-friendly tool that effectively supports academic research workflows. By following this guide and leveraging modern CLI libraries, we'll create an intuitive and maintainable application.

**Key Takeaways:**
- **Modern CLI Design:** Utilize Typer for command structure, questionary for interactive inputs, and Rich for beautiful output
- **User-Centric Approach:** Focus on intuitive commands and helpful feedback
- **Robust Architecture:** Maintain clean separation of concerns and efficient state management
- **Quality Focus:** Emphasize testing, documentation, and maintainability

**Next Steps:**
1. **Setup Core CLI Structure:**
   - Initialize Typer application
   - Set up command groups
   - Configure Rich console styling
2. **Implement Core Commands:**
   - Build store management commands
   - Create document processing pipeline
   - Develop search functionality
3. **Enhance User Experience:**
   - Add progress indicators
   - Implement interactive prompts
   - Design rich output formats
4. **Testing and Documentation:**
   - Write comprehensive tests
   - Document all commands
   - Create user guides

By following this implementation guide, LightWriter will evolve into a powerful CLI tool that effectively supports academic research workflows while maintaining clean architecture and excellent user experience.