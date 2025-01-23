# LightWriter Development Guide

## Table of Contents
1. [Project Objective](#1-project-objective)
2. [Core Functionality](#2-core-functionality)
3. [Development Process](#3-development-process)
4. [Implementation Guide](#4-implementation-guide)
5. [Best Practices](#5-best-practices)

# LightWriter: Academic Research and Writing Assistant

## Project Description

LightWriter is a sophisticated local-first academic research and writing platform that transforms how researchers interact with their scholarly materials. At its core, it combines advanced document processing with intelligent writing assistance, powered by a knowledge graph-based retrieval-augmented generation (RAG) system.

The platform processes academic documents locally, extracting rich metadata including citations, references, and mathematical equations. Using LightRAG, it constructs a comprehensive knowledge graph from your research materials, enabling deep understanding of relationships between papers, concepts, and citations. This local-first approach ensures document privacy while maintaining powerful analysis capabilities.

What sets LightWriter apart is its intelligent writing assistance system. Built on PydanticAI agents, it maintains awareness of your entire manuscript while helping with section-specific writing tasks. The system can suggest relevant citations from your knowledge graph, integrate new research findings, and maintain consistent academic style throughout your paper. Whether you're drafting new sections, refining existing content, or integrating literature reviews, the agents work with full context awareness to ensure coherent and well-supported academic writing.

The modern web interface, built with Next.js and React, provides an intuitive environment for document management, knowledge exploration, and writing assistance. It seamlessly integrates local document processing with cloud-based AI capabilities, offering features like real-time equation rendering, citation network visualization, and interactive knowledge graph exploration.

LightWriter is designed for researchers who need more than just a document manager or writing tool – it's a comprehensive research assistant that understands the interconnected nature of academic work and supports the entire research and writing process, from literature review to manuscript completion.

## 1. Project Objective

### 1.1 Overview
LightWriter is a local-first academic research assistant application with a modern web interface, built using Next.js 14+ and React + shadcn/ui. The application runs locally on researchers' machines, providing secure and private document processing while leveraging cloud services for specific AI capabilities. 

At its core, LightWriter creates a personal knowledge workspace that processes and stores academic documents locally, while providing a sophisticated web interface for interaction. The application employs LightRAG to construct a local knowledge graph (KG) from your research documents, enabling powerful retrieval-augmented generation (RAG) capabilities without compromising document privacy or requiring constant internet connectivity.

### 1.2 Key Goals
1. **Core Functionality**
   - PDF processing with Marker
   - DOI/arXiv identification with pdf2doi
   - Metadata enrichment via APIs
   - Knowledge graph construction with LightRAG
   - AI-assisted writing with PydanticAI agents

2. **Architecture**
   - Local-first document processing
   - Next.js 14+ with React Server Components
   - shadcn/ui for interface components
   - Zustand + TanStack Query for state management

## 2. Core Functionality

### 2.0 Python Project Structure
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
├── tests
│   ├── pdfs
│   │   ├── Brown et al. - 2020 - Pediatric acute lymphoblastic leukemia, version 2.2020-annotated.pdf
│   │   ├── Caldas, Soares - 2023 - A Temporal Fusion Transformer for Long-Term Explainable Prediction of Emergency Department Overcrowding-annotated.pdf
│   │   ├── Chen et al. - 2023 - TSMixer An All-MLP Architecture for Time Series Forecasting-annotated.pdf
│   │   ├── Choo et al. - 2023 - Deep-learning-based personalized prediction of absolute neutrophil count recovery and comparison with clinicians-annotated.pdf
│   │   └── Escobar et al. - 2020 - Automated Identification of Adults at Risk for In-Hospital Clinical Deterioration-annotated.pdf
│   ├── test_extractors.py
│   ├── test_pdf_processing.py
│   └── test_store.py

### 2.1 Required Directory Structure
```
frontend/           # Next.js application
├── app/           # App router pages
├── components/    # React components
└── lib/          # Shared utilities

src/               # Python backend
├── processing/    # Document processing
├── metadata/      # Metadata handling
└── agents/       # PydanticAI agents

storage/           # Local document storage
├── documents/    # Original PDFs
├── metadata/     # Extracted metadata
└── vectors/      # Vector embeddings
```

### 2.2 Processing Pipeline
1. PDF Text Extraction (Marker)
2. Identifier Detection (pdf2doi)
3. Metadata Retrieval (CrossRef/arXiv)
4. Knowledge Graph Construction (LightRAG)
5. AI-Assisted Analysis (PydanticAI)

## 3. Development Process

### 3.1 Implementation Order
1. **Phase 1: Local Processing**
   - Document processing setup
   - Storage management
   - Python backend structure

2. **Phase 2: Frontend Development**
   - Next.js application setup
   - Core UI components
   - State management implementation

3. **Phase 3: Integration**
   - Backend-frontend communication
   - LightRAG integration
   - PydanticAI agent setup

### Citation Processing System (TODO)

The system processes citations in academic papers using the following approach:

- **Citation Styles**: Currently should support:
  - Square bracket numeric citations (e.g., `[1]`, `[1,2,3]`, `[1-3]`)
  - Author-year citations (e.g., "Smith et al. (2023)")

- **Known Limitations**:
  - Superscript citations are not currently supported due to Marker conversion limitations
  - Only processes citations that follow strict formatting patterns to avoid false positives

- **Citation-Reference Linking**:
  - Each citation is linked to its corresponding reference(s)
  - Multiple citations of the same reference are preserved
  - Context around each citation is captured for analysis
  - Citations are validated against the reference list
  - Citations must exactly match reference list numbering, normalization is needed


4. **Citation Graph Generation**:
   - Builds directed graph of citations
   - Tracks citation frequency and patterns
   - Enables network visualization
   - Supports citation validation

### Equation Processing System (we might need to implement this)
1. **Equation Detection**:
   ```python
   EQUATION_PATTERNS = [
       (r'\$\$(.*?)\$\$', EquationType.DISPLAY),             # Display equations
       (r'\$(.*?)\$', EquationType.INLINE),                  # Inline equations
       (r'\\begin\{equation\}(.*?)\\end\{equation\}', EquationType.DISPLAY),
       (r'\\[(.*?)\\]', EquationType.DISPLAY),
       (r'\\begin\{align\*?\}(.*?)\\end\{align\*?\}', EquationType.DISPLAY),
       (r'\\begin\{eqnarray\*?\}(.*?)\\end\{eqnarray\*?\}', EquationType.DISPLAY)
   ]
   ```

2. **Symbol Extraction**:
   ```python
   SYMBOL_PATTERNS = [
       r'\\alpha', r'\\beta', r'\\gamma', r'\\delta',    # Greek letters
       r'\\sum', r'\\prod', r'\\int',                    # Operators
       r'\\frac', r'\\sqrt', r'\\partial',               # Functions
       r'\\mathcal', r'\\mathbf', r'\\mathrm'           # Styles
   ]
   ```

3. **Equation Object Structure**:
   ```python
   class Equation:
       raw_text: str
       symbols: Set[str]
       equation_type: EquationType
       context: Optional[str]
   ```

4. **Equation Classification**:
   - INLINE: Within text equations
   - DISPLAY: Standalone equations
   - DEFINITION: Mathematical definitions
   - THEOREM: Mathematical theorems (TODO)



## 4. Implementation Guide

### 4.1 Frontend Implementation
```typescript
// Next.js app structure
app/
├── layout.tsx       // Root layout
├── page.tsx         // Home page
└── documents/       // Document management
    ├── page.tsx    // Documents list
    └── [id]/       // Single document view
```

### 4.2 Backend Implementation
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

## 5. Best Practices

### 5.1 Development Guidelines
- Prioritize local processing and storage
- Implement proper error handling
- Follow Next.js and React best practices
- Maintain clear separation between frontend and backend
- Use TypeScript for frontend development
- Implement proper testing at all levels

### 5.2 Security Considerations
- Secure local file system access
- Safe API key management
- Proper error handling and logging
- Data validation at all levels


## 6. UI/UX Mapping

### 6.1 Core Interface Components

1. **Document Processing Hub**
   ```typescript
   interface ProcessingHub {
     upload: {
       pdfEngine: "Marker",
       validation: "Size, encoding, format checks",
       batchProcessing: "Multiple document handling",
       progress: "Real-time processing indicators"
     },
     extraction: {
       metadata: "DOI/arXiv identification",
       references: "Anystyle integration",
       equations: "LaTeX equation detection",
       citations: "Pattern matching and linking"
     }
   }
   ```

2. **Academic Content Manager**
   ```typescript
   interface ContentManager {
     metadata: {
       display: "Structured metadata view",
       edit: "Manual metadata correction",
       enrichment: "CrossRef/arXiv integration"
     },
     references: {
       list: "Reference management",
       validation: "DOI/URL verification",
       linking: "Citation-reference mapping"
     },
     equations: {
       viewer: "LaTeX equation rendering",
       symbols: "Symbol extraction view",
       classification: "Equation type management"
     }
   }
   ```

3. **Knowledge Graph Interface**
   ```typescript
   interface KnowledgeGraph {
     search: {
       modes: "Naive | Local | Global | Hybrid | Mix",
       visualization: "Interactive graph view",
       filtering: "Content/metadata filters"
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
       citationContext: "Related citations and references"
     },
     writingAssistance: {
       sectionDrafting: "AI-assisted section writing",
       literatureIntegration: "Knowledge graph-based citations",
       iterativeRefinement: "Section-by-section improvement",
       styleConsistency: "Academic writing style maintenance"
     },
     researchTools: {
       knowledgeExploration: "Local KG exploration",
       onlineResearch: "New source integration",
       citationSuggestions: "Context-aware reference suggestions",
       factChecking: "Source verification"
     }
   }
   ```

### 6.2 User Workflows

1. **Document Processing**
   - Upload → Validate → Process → Enrich
   - Real-time status updates
   - Error handling with recovery options
   - Batch processing capabilities

2. **Academic Analysis**
   - Browse → Search → Analyze → Export
   - Multiple search modes
   - Citation network exploration
   - Equation analysis and search

3. **Knowledge Management**
   - Organize → Link → Discover → Share
   - Metadata management
   - Reference organization
   - Knowledge graph exploration

### 6.3 Component Architecture

1. **Frontend Components**
   ```typescript
   {
     shared: {
       Layout: "App layout with navigation",
       ErrorBoundary: "Error handling wrapper",
       LoadingStates: "Processing indicators"
     },
     documents: {
       Uploader: "PDF upload interface",
       Processor: "Processing status/controls",
       Viewer: "Document preview/reading"
     },
     academic: {
       MetadataEditor: "Metadata management",
       ReferenceManager: "Reference handling",
       EquationViewer: "Equation display/search"
     },
     knowledge: {
       GraphViewer: "Knowledge graph interface",
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
       search: "Search and filter state",
       ui: "Interface preferences"
     },
     queries: {
       processing: "Document processing operations",
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
       fullText: "Complete manuscript storage",
       sections: "Section-by-section organization",
       metadata: "Paper metadata and status"
     },
     knowledge: {
       localSources: "KG-integrated references",
       externalSources: "Online research findings",
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
       integration: "Source incorporation",
       refinement: "Style and clarity enhancement"
     },
     context: {
       paperScope: "Full manuscript awareness",
       sectionContext: "Current section focus",
       sourceContext: "Reference material context"
     }
   }
   ```

3. **Agent Interaction System**
   ```typescript
   interface AgentSystem {
     capabilities: {
       contextAwareness: "Full paper understanding",
       sourceIntegration: "KG-based citation",
       styleAdherence: "Academic writing standards",
       iterativeImprovement: "Progressive refinement"
     },
     tasks: {
       draftGeneration: "Initial content creation",
       sourceIntegration: "Citation and reference inclusion",
       contentRefinement: "Iterative improvement",
       styleEnhancement: "Writing style optimization"
     }
   }
   ```

### 6.5 Writing Assistant Integration

1. **Knowledge Integration**
   - Full manuscript context preservation
   - Dynamic knowledge graph updates
   - Real-time citation network
   - Source verification and integration

2. **Writing Process**
   - Section-aware content generation
   - Context-preserving iterations
   - Style-consistent improvements
   - Source-backed assertions

3. **Agent Capabilities**
   - Complete paper context understanding
   - Cross-section consistency maintenance
   - Knowledge graph-based citations
   - Academic style adherence