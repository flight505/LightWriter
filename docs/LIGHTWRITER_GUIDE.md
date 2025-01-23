# LightWriter Development Guide 🚀

## Table of Contents
1. [Project Objective](#1-project-objective)
2. [Core Functionality](#2-core-functionality)
3. [Development Process](#3-development-process)
4. [Implementation Guide](#4-implementation-guide)
5. [Best Practices](#5-best-practices)
6. [UI/UX Mapping](#6-uiux-mapping)

---

# LightWriter: Academic Research and Writing Assistant

## Project Description
LightWriter is a sophisticated **local-first** academic research and writing platform designed to transform how researchers interact with their scholarly materials. It combines advanced document processing with intelligent writing assistance powered by a **knowledge graph-based retrieval-augmented generation (RAG)** system.

- **Local-First Privacy**: Your documents are processed locally, ensuring privacy while extracting rich metadata such as citations, references, and mathematical equations.
- **Knowledge Graph**: LightRAG constructs a comprehensive graph from your research materials, revealing relationships between papers, concepts, and citations.
- **Intelligent Writing Assistance**: Built on **PydanticAI** agents, LightWriter maintains awareness of your entire manuscript and assists with section-specific writing tasks, including:
  - Suggesting relevant citations
  - Integrating new research findings
  - Maintaining consistent academic style

The sleek web interface (Next.js + React) makes it easy to manage documents, explore knowledge graphs, and receive real-time writing guidance. Whether you’re drafting new sections, refining existing content, or expanding literature reviews, LightWriter works as a complete research assistant from start to finish.

---

## 1. Project Objective

### 1.1 Overview
LightWriter is a **local-first** academic research assistant application that runs securely on a researcher’s machine. It uses cloud services for AI tasks **only where needed**, without compromising document privacy. Built on:
- **Next.js 14+** and **React** (UI with shadcn/ui components)
- **LightRAG** (local knowledge graph for advanced research insights)
- **PydanticAI Agents** (intelligent writing support)
- **Zustand + TanStack Query** (state management)

### 1.2 Key Goals
1. **Core Functionality**
   - PDF processing with Marker
   - DOI/arXiv identification with pdf2doi
   - Metadata enrichment via APIs (CrossRef, arXiv)
   - Knowledge graph construction with LightRAG
   - AI-assisted writing with PydanticAI

2. **Architecture**
   - Local-first storage & processing
   - Next.js 14+ with React Server Components
   - shadcn/ui for a modern, accessible UI
   - State management via Zustand + TanStack Query

---

## 2. Core Functionality

### 2.1 Python Project Structure
A recommended Python backend project layout:
```
.
├── src
│   ├── __init__.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── extractors
│   │   ├── metadata
│   │   └── store
│   ├── processing
│   │   ├── __init__.py
│   │   ├── pipeline.py
│   │   └── steps.py
│   └── utils
│       ├── __init__.py
│       ├── constants.py
│       └── logger.py
├── storage
│   ├── logs
│   │   └── lightwriter.log
│   ├── metadata.json
│   └── processed
│       └── test_results
├── test.txt
├── tests
│   ├── pdfs
│   ├── test_citations.py
│   ├── test_extractors.py
│   ├── test_pdf_processing.py
│   ├── test_pipeline.py
│   └── test_store.py
```

### 2.2 Required Directory Structure
```
frontend/           # Next.js application
├── app/            # App router pages
├── components/     # React components
└── lib/            # Shared utilities

src/                # Python backend
├── processing/     # Document processing
├── metadata/       # Metadata handling
└── agents/         # PydanticAI agents

storage/            # Local document storage
├── documents/      # Original PDFs
├── metadata/       # Extracted metadata
└── vectors/        # Vector embeddings
```

### 2.3 Processing Pipeline
1. **PDF Text Extraction** (Marker)  
2. **Identifier Detection** (pdf2doi)  
3. **Metadata Retrieval** (CrossRef/arXiv)  
4. **Knowledge Graph Construction** (LightRAG)  
5. **AI-Assisted Analysis** (PydanticAI)

---

### 2.4 Citation Processing System (TODO)
LightWriter processes citations in academic papers using the following approach:

- **Citation Styles**  
  - Numeric (square brackets): e.g., `[1]`, `[1,2,3]`, `[1-3]`  
  - Author-year: e.g., *Smith et al. (2023)*  
  - *(Superscript citations not yet supported)*  

- **Citation-Reference Linking**  
  - Each citation is matched to corresponding references  
  - Multiple citations of the same reference are preserved  
  - Context surrounding each citation is captured for analysis  
  - Citations must match reference list numbering, requiring normalization

- **Citation Graph Generation**  
  - Directed graph of citations  
  - Tracks citation frequency and patterns  
  - Enables network visualization  
  - Assists in citation validation

---

### 2.5 Equation Processing System (We Might Need to Implement This)
1. **Equation Detection**  
   ```python
   EQUATION_PATTERNS = [
       (r'\$\$(.*?)\$\$', EquationType.DISPLAY),  
       (r'\$(.*?)\$', EquationType.INLINE),  
       (r'\\begin\{equation\}(.*?)\\end\{equation\}', EquationType.DISPLAY),
       (r'\\[(.*?)\\]', EquationType.DISPLAY),
       (r'\\begin\{align\*?\}(.*?)\\end\{align\*?\}', EquationType.DISPLAY),
       (r'\\begin\{eqnarray\*?\}(.*?)\\end\{eqnarray\*?\}', EquationType.DISPLAY)
   ]
   ```

2. **Symbol Extraction**  
   ```python
   SYMBOL_PATTERNS = [
       r'\\alpha', r'\\beta', r'\\gamma', r'\\delta',   # Greek letters
       r'\\sum', r'\\prod', r'\\int',                   # Operators
       r'\\frac', r'\\sqrt', r'\\partial',              # Functions
       r'\\mathcal', r'\\mathbf', r'\\mathrm'           # Styles
   ]
   ```

3. **Equation Object Structure**  
   ```python
   class Equation:
       raw_text: str
       symbols: Set[str]
       equation_type: EquationType
       context: Optional[str]
   ```

4. **Equation Classification**  
   - **INLINE**: Appears within text  
   - **DISPLAY**: Standalone or centered equations  
   - **DEFINITION**: Mathematical definitions (TODO)  
   - **THEOREM**: Theorems (TODO)

---

## 3. Development Process

### 3.1 Implementation Order
1. **Phase 1: Local Processing**  
   - Document processing setup  
   - Storage management  
   - Python backend structure  

2. **Phase 2: Frontend Development**  
   - Next.js application scaffolding  
   - Core UI components (shadcn/ui)  
   - State management via Zustand + TanStack Query  

3. **Phase 3: Integration**  
   - Backend-frontend communication  
   - LightRAG integration  
   - PydanticAI agent setup

---

### 3.2 Additional Implementation Details
Below are important supplementary points for integrating the architecture, knowledge graph, and user interfaces.

#### Architecture Proposal
```
Frontend (Next.js 14+)               Backend (Python)                Storage
┌─────────────────────┐           ┌─────────────────────┐         ┌─────────────────────┐
│ React + shadcn/ui   │ ←API→     │ FastAPI Endpoints   │  ←→     │ LightRAG Store      │
│ (Components)        │           └─────────────────────┘         │  - Documents        │
└─────────────────────┘                   ↓                       │  - Vectors          │
        ↓                           ┌─────────────────────┐        │  - Metadata         │
┌─────────────────────┐            │ LightRAG Processing │        │  - Graph            │
│ Zustand + Query      │            └─────────────────────┘        └─────────────────────┘
│ (State Management)   │                   ↓                              ↓
└─────────────────────┘            ┌─────────────────────┐        ┌─────────────────────┐
                                   │ Extractors, Agents  │        │ OpenAI API          │
                                   └─────────────────────┘        │ - Embeddings        │
                                                                   │ - LLM Model         │
                                                                   └─────────────────────┘
```

- **Local-first** document processing
- **OpenAI** for embeddings and advanced LLM tasks
- **LightRAG** for building and querying the local knowledge graph

#### Integration Flow
1. **Frontend** sends documents or queries to **FastAPI** endpoints.  
2. **FastAPI** routes the requests to **LightRAG** for processing or retrieval.  
3. **LightRAG** handles local data storage, knowledge graph updates, and queries.  
4. **OpenAI** API handles embeddings and advanced LLM-based tasks.  
5. Results return to the frontend, updating the UI.

#### Interface Approach
- **Modes**: Naive, Local, Global, Hybrid, or Mixed Search  
- **Storage**: JSON-based key-value store for fast local reads/writes  
- **Graph**: NetworkX for knowledge graph representation  
- **Embedding**: OpenAI-based embeddings for vector searches  

#### Recommended Features to Implement
1. **Phase 1**: Document upload/processing, basic search, result display  
2. **Phase 2**: Graph visualization, entity management, custom KG input  
3. **Phase 3**: Caching, batch processing, advanced search modes

#### Unique Advantages
- Local-first approach for privacy and offline resilience  
- Built-in caching for performance  
- Flexible storage for future scaling  
- Graph visualization for deep knowledge exploration

---

## 4. Implementation Guide

### 4.1 Storage Setup

```
/storage
├── processed/
│   ├── lightrag_store/  # Our LightRAG storage
│   │   ├── documents/   # Document store
│   │   ├── vectors/     # Vector embeddings
│   │   └── metadata/    # Document metadata
│   └── test_results/    # Test outputs
```

- **kv_storage**: `JsonKVStorage` (simple local JSON-based KV store)  
- **vector_storage**: `NanoVectorDBStorage` (efficient local embeddings)  
- **graph_storage**: `NetworkXStorage` (lightweight local graph)  
- **embedding_func**: `openai_embedding`  
- **llm_model_func**: `gpt-4o-mini` or your preferred model

### 4.2 Architecture Proposal
Refer to the diagram in [Section 3.2](#architecture-proposal) for a high-level view. The system includes:

- **Frontend** (Next.js 14+)
- **Backend** (FastAPI + Python)
- **Local Storage** (LightRAG)
- **Optional Cloud AI** (OpenAI for embeddings, completions)

### 4.3 Integration Flow
1. **Document Upload** → **Python Processing**  
2. **Metadata & Citation Enrichment**  
3. **Storage in LightRAG** → Local JSON or vector DB  
4. **Search & Analysis** → Calls to knowledge graph + embeddings  
5. **Frontend Display** with React + shadcn/ui

### 4.4 Interface Approach
- **Frontend**:  
  - Next.js **App Router** for pages  
  - shadcn/ui for **accessible** component design  
  - Zustand + TanStack Query for state management  

- **Backend**:  
  - Python with **FastAPI** for serving endpoints  
  - LightRAG for local knowledge graph processing and storage

### 4.5 Frontend Implementation
```typescript
// Example Next.js app structure
app/
├── layout.tsx       // Root layout
├── page.tsx         // Home page
└── documents/
    ├── page.tsx     // Documents list
    └── [id]/        // Single document view
```

**Directory Structure Example**:
```
frontend/
├── src/
│   ├── app/                # App Router
│   │   ├── academic/       # Academic content
│   │   ├── documents/      # Document processing
│   │   └── knowledge/      # Knowledge graph exploration
│   ├── components/         # React UI components
│   │   ├── ui/             # shadcn/ui
│   │   └── custom/         # Custom components
│   ├── lib/                # Shared utilities
│   │   ├── utils/          # Utility functions
│   │   └── hooks/          # React hooks
│   └── store/              # Zustand stores
```

### 4.6 Backend Implementation
```python
# Python backend structure
src/
├── processing/
│   └── document_processor.py
├── metadata/
│   └── metadata_manager.py
└── agents/
    └── writing_agent.py
```
- **document_processor.py**: Pipeline for PDF extraction, metadata, and equation/citation analysis  
- **metadata_manager.py**: Local storage and retrieval of enriched metadata  
- **writing_agent.py**: PydanticAI integration for context-aware writing

---

## 5. Best Practices

### 5.1 Development Guidelines
- **Local-First Mindset**: Ensure minimal external dependencies for privacy  
- **Error Handling**: Graceful fallback and logging  
- **Security**: Store API keys securely, handle files safely  
- **Modular Frontend**: Use TypeScript and modular components in Next.js  
- **Documentation & Testing**: Thorough unit/integration tests and clear docs

### 5.2 Security Considerations
- **Local File System Access**: Validate input files, limit read/write scope  
- **API Key Management**: Use environment variables or secret management  
- **Error Logging**: Avoid leaking sensitive info  
- **Data Validation**: Enforce strict data schemas in both Python and TS

---

## 6. UI/UX Mapping

### 6.1 Core Interface Components

1. **Document Processing Hub**  
   ```typescript
   interface ProcessingHub {
     upload: {
       pdfEngine: "Marker",
       validation: "Size, encoding, format checks",
       batchProcessing: "Multiple documents",
       progress: "Real-time indicators"
     },
     extraction: {
       metadata: "DOI/arXiv detection",
       references: "Citation linking",
       equations: "LaTeX extraction",
       citations: "Pattern matching + linking"
     }
   }
   ```

2. **Academic Content Manager**  
   ```typescript
   interface ContentManager {
     metadata: {
       display: "Structured view",
       edit: "Manual correction",
       enrichment: "CrossRef/arXiv integration"
     },
     references: {
       list: "Reference management",
       validation: "DOI/URL checks",
       linking: "Citation-reference mapping"
     },
     equations: {
       viewer: "LaTeX rendering",
       symbols: "Symbol extraction",
       classification: "Equation type"
     }
   }
   ```

3. **Knowledge Graph Interface**  
   ```typescript
   interface KnowledgeGraph {
     search: {
       modes: "Naive | Local | Global | Hybrid | Mix",
       visualization: "Interactive graph",
       filtering: "Content or metadata filters"
     },
     analysis: {
       citations: "Citation network analysis",
       patterns: "Research pattern detection",
       insights: "AI-powered suggestions"
     }
   }
   ```

4. **Academic Writing Interface**  
   ```typescript
   interface AcademicWriter {
     paperContext: {
       fullManuscript: "Complete paper context",
       activeSection: "Current working section",
       outlineStructure: "Paper organization",
       citationContext: "Related references"
     },
     writingAssistance: {
       sectionDrafting: "AI section writing",
       literatureIntegration: "KG-based citations",
       iterativeRefinement: "Section-by-section improvement",
       styleConsistency: "Academic style maintenance"
     },
     researchTools: {
       knowledgeExploration: "Local KG exploration",
       onlineResearch: "New source integration",
       citationSuggestions: "Context-aware references",
       factChecking: "Source verification"
     }
   }
   ```

### 6.2 User Workflows

1. **Document Processing**  
   - **Upload** → **Validate** → **Process** → **Enrich**  
   - Real-time status updates  
   - Error handling with recovery options  
   - Batch processing support  

2. **Academic Analysis**  
   - **Browse** → **Search** → **Analyze** → **Export**  
   - Multiple search modes  
   - Citation network exploration  
   - Equation analysis  

3. **Knowledge Management**  
   - **Organize** → **Link** → **Discover** → **Share**  
   - Metadata management  
   - Reference organization  
   - Graph exploration

### 6.3 Component Architecture

1. **Frontend Components**  
   ```typescript
   {
     shared: {
       Layout: "App layout + navigation",
       ErrorBoundary: "Error handling",
       LoadingStates: "Processing indicators"
     },
     documents: {
       Uploader: "PDF upload + status",
       Processor: "Processing controls",
       Viewer: "Document preview"
     },
     academic: {
       MetadataEditor: "Metadata editing",
       ReferenceManager: "Reference linking",
       EquationViewer: "Equation display"
     },
     knowledge: {
       GraphViewer: "KG visualization",
       SearchInterface: "Multi-mode search",
       AnalyticsPanel: "Research insights"
     }
   }
   ```

2. **State Management**  
   ```typescript
   {
     stores: {
       documents: "Document processing state",
       metadata: "Academic metadata state",
       search: "Search & filter state",
       ui: "Theme & layout preferences"
     },
     queries: {
       processing: "Document pipeline tasks",
       enrichment: "Metadata enrichment calls",
       search: "Search operations"
     }
   }
   ```

### 6.4 Academic Writing System

1. **Paper Context Management**  
   ```typescript
   interface PaperContext {
     structure: {
       fullText: "Complete manuscript",
       sections: "Section-based organization",
       metadata: "Paper details + status"
     },
     knowledge: {
       localSources: "KG references",
       externalSources: "Online findings",
       citationNetwork: "Citation relationships"
     }
   }
   ```

2. **Writing Workflows**  
   ```typescript
   interface WritingWorkflow {
     modes: {
       sectionDrafting: "New section creation",
       revision: "Content improvement",
       integration: "Citations & references",
       refinement: "Style + clarity"
     },
     context: {
       paperScope: "Full manuscript awareness",
       sectionContext: "Focused writing section",
       sourceContext: "Reference/citation data"
     }
   }
   ```

3. **Agent Interaction System**  
   ```typescript
   interface AgentSystem {
     capabilities: {
       contextAwareness: "Paper-wide knowledge",
       sourceIntegration: "KG-based citation suggestions",
       styleAdherence: "Academic standards",
       iterativeImprovement: "Progressive refinement"
     },
     tasks: {
       draftGeneration: "Initial content creation",
       sourceIntegration: "Reference + citation inclusion",
       contentRefinement: "Iterative improvement",
       styleEnhancement: "Academic tone + formatting"
     }
   }
   ```

### 6.5 Writing Assistant Integration
- **Knowledge Integration**: Real-time knowledge graph updates, citation suggestions, and local or cloud-based research.  
- **Writing Process**: Section-aware drafting, context-preserving refinements, and consistent academic style.  
- **Agent Capabilities**: Full manuscript context, cross-section coherence, knowledge graph-based citations, and style adherence.

---
