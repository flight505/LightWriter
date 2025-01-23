### LightWriter TODO List

1. **Document Processing Core**
   - [x] PDF text extraction with Marker
   - [x] DOI/arXiv identifier extraction with pdf2doi
   - [ ] Support for more document formats
   - [ ] Batch processing support
   - [ ] Processing queue system
   - [ ] Progress tracking system

2. **Extraction Systems**
   - **Equation Processing**
     - [x] Basic equation extraction (inline, display, numbered)
     - [ ] Symbol classification
     - [ ] Equation search functionality
     - [ ] LaTeX rendering support
     - [ ] Equation similarity matching

   - **Reference Processing**
     - [x] Reference extraction
     - [x] Crossref integration
     - [ ] Reference validation system
     - [ ] Reference deduplication

   - **Citation System**
     - [ ] Citation pattern extraction
     - [ ] Citation-reference linking
     - [ ] Citation network analysis
     - [ ] Citation validation system
     - [ ] Citation context extraction

3. **Storage and Knowledge System**
   - [x] Basic StoreManager implementation
   - [x] LightRAG basic integration
   - [x] Metadata consolidation
   - [x] Document storage and retrieval
   - [ ] Advanced hybrid search modes
   - [ ] Graph visualization data preparation
   - [ ] Relationship extraction
   - [ ] Concept linking system
   - [ ] Vector store optimization

4. **Processing Pipeline**
   - [x] Basic document processing workflow
   - [x] Error handling
   - [x] Duplicate detection
   - [x] Basic search functionality
   - [ ] Advanced pipeline orchestration
   - [ ] Parallel processing support
   - [ ] Processing status tracking
   - [ ] Recovery mechanisms

5. **Agent System**
   - [ ] PydanticAI agent framework
   - [ ] Writing assistance agents
   - [ ] Context-aware processing
   - [ ] Citation suggestion system
   - [ ] Style consistency checking
   - [ ] Content improvement suggestions

6. **API Layer**
   - [ ] FastAPI backend service
   - [ ] WebSocket support
   - [ ] Security measures
   - [ ] Rate limiting
   - [ ] API documentation
   - [ ] Client SDK

7. **Frontend Integration**
   - [ ] Next.js project structure
   - [ ] Document upload/processing UI
   - [ ] Knowledge graph visualization
   - [ ] Writing interface
   - [ ] Real-time collaboration features
   - [ ] Progress indicators

8. **Testing Infrastructure**
   - [x] Basic extractor tests
   - [x] Storage system tests
   - [x] Processing pipeline tests
   - [ ] Citation extraction tests
   - [ ] Batch processing tests
   - [ ] Graph relationship tests
   - [ ] Performance benchmark tests
   - [ ] Integration tests for full pipeline
   - [ ] Frontend component tests
   - [ ] E2E tests

9. **Documentation**
   - [ ] API documentation
   - [ ] User guide
   - [ ] Developer guide
   - [ ] Architecture documentation
   - [ ] Deployment guide
   - [ ] Contributing guide

10. **Deployment and DevOps**
    - [ ] Docker configuration
    - [ ] CI/CD pipeline
    - [ ] Monitoring setup
    - [ ] Logging system
    - [ ] Backup system
    - [ ] Performance optimization
