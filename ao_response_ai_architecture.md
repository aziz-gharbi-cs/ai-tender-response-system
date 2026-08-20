# AI System for Automated IT Tender Responses

## 1. Project Context

This internship project aims to design and implement an AI-powered system capable of analyzing an IT tender / Request for Proposal (RFP) and automatically producing a structured technical proposal.

The target users are ESNs (digital services companies) and IT consulting companies that regularly respond to tenders issued by IT departments.

The system should reduce the repetitive work involved in:

- Analyzing tender documents
- Extracting technical and business requirements
- Finding relevant internal project references
- Finding suitable employee profiles / CVs
- Performing external market research
- Generating a technical proposal
- Checking the generated proposal for quality and security
- Versioning and storing generated proposals

The system will combine:

- FastAPI
- LangChain
- LangGraph
- RAG
- Qdrant
- Embedding models
- AnythingLLM concepts
- GPT Researcher
- LLM Guard
- PostgreSQL
- Redis
- Celery
- SSE
- PDF/DOCX/OCR processing
- Docker

---

# 2. Main Problem

The central problem is:

> How can we design a secure multi-agent AI system capable of automatically analyzing an IT tender and generating a relevant technical proposal using the company's internal document corpus?

The system must combine internal knowledge with external research while keeping the architecture modular and maintainable.

---

# 3. Most Important Development Principle

## We are NOT building a toy application first.

The project must use the **real target architecture from the beginning**.

Bad approach:

```text
Toy application
    ↓
Make it work
    ↓
Add architecture
    ↓
Rewrite everything
```

Our approach:

```text
Real architecture
    ↓
Implement one component
    ↓
Implement another component
    ↓
Plug in real infrastructure
    ↓
Expand progressively
```

Every new technology should be an addition to the architecture rather than a reason to rewrite the existing system.

The first implementation can be minimal, but the **boundaries and interfaces must already support the final system**.

---

# 4. High-Level Architecture

```text
                         ┌──────────────────────┐
                         │       CLIENT         │
                         │ Web UI / Postman     │
                         └──────────┬───────────┘
                                    │
                              HTTP / SSE
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │        FastAPI API        │
                    │                           │
                    │  /api/v1/tenders         │
                    │  /api/v1/documents       │
                    │  /api/v1/jobs             │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │   Application Services    │
                    │                           │
                    │ ProposalService           │
                    │ DocumentService           │
                    │ JobService                │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                 ┌────────────────────────────────┐
                 │       LANGGRAPH WORKFLOW       │
                 │                                │
                 │        Shared State            │
                 │              │                 │
                 │              ▼                 │
                 │       ┌─────────────┐          │
                 │       │  Verifier   │          │
                 │       └──────┬──────┘          │
                 │              ▼                 │
                 │       ┌─────────────┐          │
                 │       │ Extraction  │          │
                 │       └──────┬──────┘          │
                 │              ▼                 │
                 │       ┌─────────────┐          │
                 │       │  Research   │          │
                 │       └──────┬──────┘          │
                 │              ▼                 │
                 │       ┌─────────────┐          │
                 │       │ Generation  │          │
                 │       └──────┬──────┘          │
                 │              ▼                 │
                 │       ┌─────────────┐          │
                 │       │   Quality   │          │
                 │       └─────────────┘          │
                 └────────────────────────────────┘
                                  │
                                  ▼
          ┌────────────────────────────────────────────┐
          │              DOMAIN / SERVICES             │
          │                                            │
          │ RAG Service                                │
          │ Research Service                           │
          │ LLM Service                                │
          │ Security Service                           │
          │ Document Service                           │
          │ Proposal Service                           │
          └──────────────────────┬─────────────────────┘
                                 │
                                 ▼
             ┌────────────────────────────────────────┐
             │             INFRASTRUCTURE             │
             │                                        │
             │ PostgreSQL                             │
             │ Qdrant                                 │
             │ Redis                                  │
             │ Celery                                 │
             │ GPT Researcher                         │
             │ LLM Guard                              │
             │ LLM Provider                           │
             │ PDF/DOCX/OCR                           │
             │ File Storage                           │
             └────────────────────────────────────────┘
```

---

# 5. Main Components

## 5.1 FastAPI

FastAPI is the external API layer.

Its responsibilities are:

- Receive HTTP requests
- Validate input
- Authenticate/authorize users if authentication is added
- Call application services
- Return responses
- Provide OpenAPI documentation
- Provide SSE endpoints for progress streaming

FastAPI should NOT contain:

- RAG logic
- Agent logic
- Database implementation
- LLM calls
- Business logic

Example:

```text
POST /api/v1/proposals
        ↓
ProposalService
        ↓
LangGraph
```

---

# 6. Application Layer

The application layer coordinates business use cases.

Main services:

```text
ProposalService
DocumentService
JobService
```

Example:

```text
ProposalService
      ↓
WorkflowService
      ↓
LangGraph
```

The application layer should not know implementation details such as:

- Which vector database is used
- Which LLM provider is used
- How PDF extraction works
- How GPT Researcher works internally

Those details belong to infrastructure/services.

---

# 7. LangGraph

LangGraph is the orchestration engine of the multi-agent system.

It represents the workflow as a graph.

Example:

```text
START
  ↓
Verifier
  ↓
Extraction
  ↓
RAG Retrieval
  ↓
Research
  ↓
Generation
  ↓
Quality & Security
  ↓
END
```

The graph can contain conditional edges.

For example:

```text
Quality
   │
   ├── score acceptable → END
   │
   └── score insufficient → Generation
```

This allows automatic regeneration.

---

# 8. Shared LangGraph State

Agents communicate through a shared state.

Example:

```python
class ProposalState(TypedDict):
    request_id: str

    input_documents: list

    extracted_text: dict

    requirements: dict

    internal_references: list

    candidate_profiles: list

    external_research: dict

    proposal_draft: str

    quality_report: dict

    errors: list

    status: str
```

The state progressively grows:

```text
Initial State
    ↓
+ input documents
    ↓
+ extracted text
    ↓
+ requirements
    ↓
+ internal references
    ↓
+ external research
    ↓
+ proposal draft
    ↓
+ quality report
    ↓
Final State
```

This state is one of the most important concepts in the architecture.

---

# 9. Multi-Agent System

## 9.1 Verifier Agent

Responsibility:

- Check that required files exist
- Check file formats
- Verify that the tender document exists
- Verify that the response template exists
- Block the workflow when mandatory inputs are missing

Flow:

```text
AO Package
    ↓
Verifier
    ↓
Valid?
 ┌──┴──┐
NO    YES
 ↓      ↓
STOP  Extraction
```

---

## 9.2 Extraction Agent

Responsibility:

Analyze the tender and extract structured requirements.

Possible output:

```json
{
  "technologies": [
    "Python",
    "PostgreSQL"
  ],
  "deliverables": [
    "API",
    "Documentation"
  ],
  "duration": "6 months",
  "constraints": [],
  "evaluation_criteria": []
}
```

The agent can use:

- Document extraction
- LLM
- RAG where appropriate

---

## 9.3 Research Agent

Responsibility:

Perform external research.

Examples:

- Market context
- Competitors
- Similar projects
- Technology trends
- Industry information
- Positioning

Architecture:

```text
Research Agent
      ↓
ResearchService
      ↓
GPT Researcher
      ↓
Web
      ↓
Research results
```

---

## 9.4 Generation Agent

Responsibility:

Generate the technical proposal.

It combines:

```text
Requirements
+
Internal project references
+
Candidate profiles
+
External research
+
Company template
+
LLM
```

Result:

```text
Technical Proposal
```

Possible sections:

- Executive summary
- Understanding of the requirements
- Proposed methodology
- Technical architecture
- Implementation approach
- Planning
- Team
- Project references
- Risk management
- Quality approach
- Conclusion

---

## 9.5 Quality & Security Agent

Responsibility:

Validate the generated document before final delivery.

Checks can include:

- Sensitive information / PII
- Prompt injection
- Template compliance
- Output quality
- Consistency
- Unsupported claims
- Potential hallucinations

Architecture:

```text
Generated Proposal
        ↓
Quality Agent
        ↓
LLM Guard
        ↓
Quality Checks
        ↓
Score
   ┌────┴────┐
PASS       FAIL
 ↓           ↓
END       Regenerate
```

---

# 10. RAG

RAG means:

> Retrieval-Augmented Generation.

Instead of sending the entire company document corpus to the LLM, the system retrieves only the relevant pieces.

Without RAG:

```text
1000 company documents
        ↓
LLM
```

This is inefficient and expensive.

With RAG:

```text
1000 company documents
        ↓
Index
        ↓
Search
        ↓
Top relevant chunks
        ↓
LLM
```

---

# 11. Internal RAG Pipeline

```text
PDF / DOCX / Scanned documents
              ↓
       Document Extraction
              ↓
             OCR
              ↓
           Chunking
              ↓
          Embeddings
              ↓
          Vector DB
              ↓
          Retrieval
              ↓
          Re-ranking
              ↓
      Relevant Context
              ↓
             LLM
```

---

# 12. Document Ingestion

Supported documents:

- PDF
- DOCX
- Scanned documents
- Images when necessary

Tools:

### pdfplumber

Used for extracting native PDF text.

### Camelot

Used for structured tables in PDFs.

### Surya OCR

Used for scanned/image-based documents.

Architecture:

```text
Document
   ↓
DocumentParser
   ↓
┌───────────────┬───────────────┐
│ PDF           │ DOCX          │
│ pdfplumber    │ python-docx   │
└───────────────┴───────────────┘
        +
      Surya
        ↓
Normalized text
```

The rest of the system should not care whether the original document was PDF, DOCX, or scanned.

---

# 13. Chunking

Extracted text is divided into semantic chunks.

Initial target:

```text
~512 tokens per chunk
~50 tokens overlap
```

The exact values should be evaluated experimentally rather than treated as universal constants.

Each chunk should contain metadata such as:

```json
{
  "source": "proposal_2025.pdf",
  "section": "Technical Approach",
  "document_type": "proposal",
  "project": "Banking Platform"
}
```

Metadata is important because it allows filtering and traceability.

---

# 14. Embeddings

Each chunk is converted into a numerical vector.

Possible implementation:

```text
sentence-transformers
```

Flow:

```text
Text Chunk
    ↓
Embedding Model
    ↓
Vector
    ↓
Qdrant
```

---

# 15. Vector Database

Recommended initial choice:

```text
Qdrant
```

Responsibilities:

- Store embeddings
- Store chunk metadata
- Perform similarity search
- Filter results
- Retrieve relevant chunks

Architecture:

```text
RAG Service
    ↓
VectorStore Interface
    ↓
QdrantVectorStore
    ↓
Qdrant
```

This abstraction is intentional.

If Qdrant is replaced later, the agents do not need to change.

---

# 16. Retrieval and Re-ranking

Initial retrieval:

```text
User/Agent Query
       ↓
Embedding
       ↓
Similarity Search
       ↓
Top K chunks
```

Then re-ranking:

```text
Top K chunks
       ↓
Re-ranker
       ↓
Best relevant chunks
       ↓
LLM
```

The internship evaluation should measure:

- Precision
- Recall
- Relevance
- Retrieval latency

---

# 17. AnythingLLM

AnythingLLM is mainly useful as a reference for understanding a complete RAG workflow.

Conceptually:

```text
Documents
    ↓
Workspace
    ↓
Chunking
    ↓
Embeddings
    ↓
Vector retrieval
    ↓
LLM
```

In our final architecture, we do not have to make AnythingLLM the core application.

Instead, we can implement our own RAG pipeline using:

```text
Python
+
sentence-transformers
+
Qdrant
```

This demonstrates actual understanding and gives us more control.

AnythingLLM can therefore be considered:

> A reference implementation / RAG platform whose concepts inform our own RAG module.

---

# 18. GPT Researcher

GPT Researcher handles external web research.

It is different from RAG.

### RAG

Searches:

```text
Internal company knowledge
```

### GPT Researcher

Searches:

```text
External Internet knowledge
```

Example:

```text
Tender
  ↓
Research Agent
  ↓
GPT Researcher
  ↓
Web search
  ↓
Sources
  ↓
Synthesis
```

The distinction is important:

```text
                Knowledge
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
 Internal                  External
 RAG                       Research
        │                     │
        └──────────┬──────────┘
                   ↓
               Generation
```

---

# 19. LLM Guard

LLM Guard is the security layer around LLM interactions.

Conceptually:

```text
Input
  ↓
LLM Guard
  ↓
LLM
  ↓
LLM Guard
  ↓
Output
```

Possible checks include:

- Prompt injection
- Sensitive data / PII
- Unsafe inputs
- Unsafe outputs
- Other scanner-specific risks

In our architecture:

```text
QualityAgent
     ↓
SecurityService
     ↓
LLM Guard
```

Agents should not directly depend on the internal implementation of LLM Guard.

---

# 20. LLM Abstraction

Agents should not directly call a specific LLM provider.

Bad:

```text
GenerationAgent
      ↓
OpenAI API directly
```

Better:

```text
GenerationAgent
      ↓
LLMService
      ↓
LLMProvider
      ↓
OpenAI / Ollama / Other provider
```

Example abstraction:

```python
class LLMProvider(Protocol):

    async def generate(...):
        ...
```

Possible implementations:

```text
OpenAIProvider
OllamaProvider
OtherProvider
```

This makes the system model/provider-independent.

---

# 21. Security Abstraction

Use:

```text
SecurityService
      ↓
LLM Guard implementation
```

Possible operations:

```text
scan_input()
scan_output()
detect_pii()
detect_prompt_injection()
```

The rest of the application should depend on the service/interface rather than the concrete security library.

---

# 22. Async Architecture

Proposal generation may take a long time.

Therefore the final architecture should support asynchronous execution.

```text
Client
   │
   │ POST /proposals
   ▼
FastAPI
   │
   ▼
Create Job
   │
   ▼
Redis
   │
   ▼
Celery Worker
   │
   ▼
LangGraph
```

The API immediately returns a job ID:

```json
{
  "job_id": "abc123",
  "status": "processing"
}
```

---

# 23. SSE

Server-Sent Events will stream progress to the client.

Example:

```text
10%  Verifying documents
25%  Extracting requirements
45%  Searching internal references
60%  Performing web research
80%  Generating proposal
95%  Quality verification
100% Completed
```

Architecture:

```text
Client
  ↓
SSE connection
  ↓
FastAPI
  ↓
Job progress
  ↓
Client
```

SSE is preferable here because the client mainly needs to receive server-side progress updates.

---

# 24. Persistence

Use PostgreSQL for application metadata.

Possible tables:

```text
users
projects
tenders
documents
jobs
proposals
proposal_versions
evaluations
```

Qdrant should store vectorized document chunks.

Redis should support:

```text
Celery broker
+
temporary job/progress state
```

File storage:

```text
uploaded/
processed/
generated/
```

Later the storage implementation can be replaced by S3/MinIO without rewriting business logic.

---

# 25. Separation of Responsibilities

This is a critical architectural rule.

## Bad

```text
GenerationAgent
 ├── opens Qdrant
 ├── reads PDF files
 ├── calls OpenAI
 ├── calls GPT Researcher
 ├── calls LLM Guard
 └── writes PostgreSQL
```

This creates a tightly coupled system.

## Good

```text
GenerationAgent
       │
       ├── RAGService
       ├── LLMService
       └── ProposalService
```

And those services communicate with infrastructure through interfaces.

---

# 26. Project Structure

Recommended initial structure:

```text
ao-response-ai/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── proposals.py
│   │       ├── documents.py
│   │       └── jobs.py
│   │
│   ├── application/
│   │   ├── proposal_service.py
│   │   ├── document_service.py
│   │   └── job_service.py
│   │
│   ├── domain/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── interfaces/
│   │
│   ├── agents/
│   │   ├── verifier.py
│   │   ├── extraction.py
│   │   ├── research.py
│   │   ├── generation.py
│   │   └── quality.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   ├── nodes.py
│   │   └── workflow.py
│   │
│   ├── rag/
│   │   ├── ingestion/
│   │   ├── chunking/
│   │   ├── embeddings/
│   │   ├── retrieval/
│   │   └── reranking/
│   │
│   ├── llm/
│   │   ├── provider.py
│   │   ├── openai.py
│   │   └── ollama.py
│   │
│   ├── research/
│   │   └── gpt_researcher.py
│   │
│   ├── security/
│   │   └── llm_guard.py
│   │
│   ├── documents/
│   │   ├── pdf.py
│   │   ├── docx.py
│   │   ├── ocr.py
│   │   └── factory.py
│   │
│   ├── infrastructure/
│   │   ├── database/
│   │   ├── vectorstore/
│   │   ├── storage/
│   │   └── queue/
│   │
│   └── core/
│       ├── config.py
│       ├── logging.py
│       └── exceptions.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── evaluation/
│
├── alembic/
│
├── documents/
│
├── generated/
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

---

# 27. Why This Structure?

## api/

Only HTTP/API concerns.

## application/

Coordinates business use cases.

## domain/

Contains business concepts, schemas, and abstractions/interfaces.

## agents/

Contains individual AI agents.

## graph/

Contains LangGraph orchestration.

## rag/

Contains document indexing and retrieval.

## llm/

Contains LLM abstraction and providers.

## research/

Contains external research integration.

## security/

Contains LLM security.

## documents/

Contains PDF/DOCX/OCR processing.

## infrastructure/

Contains concrete implementations for:

- Database
- Vector DB
- File storage
- Queues

## core/

Contains cross-cutting infrastructure:

- Configuration
- Logging
- Exceptions

---

# 28. Development Roadmap

The project should be implemented in this order.

## Step 1 — Foundation

Create:

- Project structure
- Configuration
- Environment variables
- Logging
- Exceptions
- Domain models
- Interfaces
- FastAPI base application

Do not build agents yet.

---

## Step 2 — Document Processing

Implement:

```text
PDF
DOCX
OCR
    ↓
Normalized text
```

Create a unified document-processing interface.

---

## Step 3 — RAG

Implement:

```text
Ingestion
   ↓
Chunking
   ↓
Embeddings
   ↓
Qdrant
   ↓
Retrieval
   ↓
Re-ranking
```

At the end of this step, the system should be able to ask:

> Find previous projects relevant to this tender requirement.

and retrieve useful internal chunks.

---

## Step 4 — LangGraph

Create:

```text
ProposalState
```

and:

```text
START
 ↓
Verifier
 ↓
Extraction
 ↓
Research
 ↓
Generation
 ↓
Quality
 ↓
END
```

At first, integrations can return controlled/mock results where necessary, but the interfaces must already match the final architecture.

---

## Step 5 — Verifier Agent

Implement real validation of the AO package.

---

## Step 6 — Extraction Agent

Implement structured extraction of:

- Requirements
- Technologies
- Deliverables
- Constraints
- Criteria
- Deadlines
- Budget when available

---

## Step 7 — Generation Agent

Connect:

```text
Requirements
+
RAG results
+
LLM
```

to generate the proposal.

---

## Step 8 — GPT Researcher

Integrate external research.

```text
Research Agent
      ↓
GPT Researcher
```

---

## Step 9 — LLM Guard

Integrate security and quality validation.

```text
Generated Output
      ↓
LLM Guard
      ↓
Quality checks
```

---

## Step 10 — PostgreSQL

Persist:

- Tenders
- Documents
- Jobs
- Proposals
- Versions
- Evaluations

---

## Step 11 — Celery + Redis

Move long-running generation to workers.

```text
FastAPI
   ↓
Redis
   ↓
Celery
   ↓
LangGraph
```

---

## Step 12 — SSE

Stream job progress.

---

## Step 13 — DOCX/PDF

Generate final proposal documents.

---

## Step 14 — Testing

Create:

### Unit tests

For:

- Chunking
- Parsers
- Services
- Agents
- Retrieval
- Validation

### Integration tests

For:

- PostgreSQL
- Qdrant
- Redis
- LangGraph
- API

### Evaluation tests

For:

- RAG quality
- Output quality
- Hallucination
- Performance

---

# 29. Evaluation

The internship requires three main evaluation dimensions.

## RAG Quality

Measure:

```text
Precision
Recall
Retrieval relevance
Latency
```

---

## Output Quality

Measure:

```text
Template compliance
Coherence
Completeness
Hallucination rate
Security issues
```

---

## Performance

Measure:

```text
Time per agent
Total generation time
Retrieval latency
Research latency
Throughput
```

---

# 30. Final End-to-End Flow

The complete system should eventually work like this:

```text
                    USER
                      │
                      ▼
                Upload AO
                      │
                      ▼
                  FastAPI
                      │
                      ▼
                  Create Job
                      │
                      ▼
              Celery + Redis
                      │
                      ▼
                 LangGraph
                      │
                      ▼
                VERIFIER
                      │
                      ▼
                EXTRACTION
                      │
            ┌─────────┴──────────┐
            ▼                    ▼
        INTERNAL             EXTERNAL
           RAG                RESEARCH
            │                    │
         Qdrant            GPT Researcher
            │                    │
            └─────────┬──────────┘
                      ▼
                  GENERATION
                      │
                      ▼
               QUALITY + SECURITY
                      │
                 ┌────┴────┐
                 │         │
               FAIL       PASS
                 │         │
                 ▼         ▼
             Regenerate   Store
                           │
                           ▼
                       DOCX/PDF
                           │
                           ▼
                         SSE
                           │
                           ▼
                         USER
```

---

# 31. Architectural Mental Model

Keep these responsibilities in your head throughout the project:

```text
FastAPI
= How the outside world talks to us

Application Services
= What the system is asked to do

LangGraph
= In what order AI tasks happen

Agents
= Specialized AI responsibilities

RAG
= Company's internal knowledge

GPT Researcher
= External web knowledge

LLM
= Reasoning / generation

LLM Guard
= AI security and output protection

PostgreSQL
= Application data

Qdrant
= Semantic/vector knowledge

Redis
= Fast temporary communication/state

Celery
= Background execution

SSE
= Real-time progress to client

Infrastructure
= Concrete technology implementations
```

---

# 32. First Coding Milestone

The first milestone is NOT a toy application.

We start with the real architecture:

```text
Project skeleton
       ↓
Configuration
       ↓
Interfaces
       ↓
Document abstraction
       ↓
RAG abstraction
       ↓
LLM abstraction
       ↓
LangGraph State
       ↓
LangGraph Workflow
       ↓
FastAPI
```

Then we progressively implement the real components.

The goal is:

> **Minimal implementation of the final architecture — not a temporary architecture.**

---

# 33. Final Rule

Whenever we add a technology, ask:

> "Where does this belong architecturally?"

Examples:

```text
Qdrant
→ infrastructure/vectorstore

OpenAI
→ llm/provider

GPT Researcher
→ research/

LLM Guard
→ security/

Celery
→ infrastructure/queue

Redis
→ infrastructure/queue

PostgreSQL
→ infrastructure/database

pdfplumber
→ documents/

LangGraph
→ graph/

FastAPI
→ api/
```

If adding a new tool requires rewriting unrelated layers, the architecture is probably wrong.

---

# 34. Current Next Step

Start with:

```text
1. Create project structure
2. Configure environment
3. Define domain interfaces
4. Define ProposalState
5. Create LangGraph workflow
6. Create FastAPI application
```

Then implement the agents and infrastructure progressively.

**The architecture comes first. The implementation grows inside it.**
