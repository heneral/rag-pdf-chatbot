# RAG PDF Chatbot - Architecture & Workflow

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT / USER                                   │
│                     (Browser, cURL, Python script)                       │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ HTTP Requests
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI SERVER (main.py)                         │
│                         http://localhost:8000                            │
├─────────────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                              │
│  • POST /upload      - Upload PDF                                       │
│  • POST /chat        - Ask questions                                    │
│  • POST /conversation - Conversational mode                             │
│  • GET  /documents   - List documents                                   │
│  • GET  /health      - Health check                                     │
│  • GET  /stats       - Statistics                                       │
└────────────────┬───────────────┬───────────────┬────────────────────────┘
                 │               │               │
        ┌────────▼──────┐ ┌─────▼─────┐ ┌──────▼────────┐
        │ PDF Processor │ │ Embeddings│ │  Vector DB    │
        │ pdf_processor │ │ embeddings│ │  vector_db    │
        │     .py       │ │    .py    │ │     .py       │
        └────────┬──────┘ └─────┬─────┘ └──────┬────────┘
                 │               │               │
                 └───────────────┴───────────────┘
                                 │
                        ┌────────▼────────┐
                        │   ChatBot       │
                        │   chat.py       │
                        │   (RAG Logic)   │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │   OpenAI API    │
                        │   GPT-4/3.5     │
                        └─────────────────┘
```

## Data Flow - Upload Process

```
1. User uploads PDF
        │
        ▼
2. FastAPI receives file (/upload endpoint)
        │
        ▼
3. PDF Processor extracts text
   • Uses PyPDF2 or pdfplumber
   • Cleans text
   • Splits into chunks (1000 chars with 200 overlap)
        │
        ▼
4. Embedding Generator creates vectors
   • OpenAI API or Sentence Transformers
   • Each chunk → vector embedding
        │
        ▼
5. Vector Database stores embeddings
   • FAISS or Chroma
   • Associates vectors with text + metadata
        │
        ▼
6. Server responds with success
   • Document ID returned
   • Ready for querying
```

## Data Flow - Query Process

```
1. User asks question
        │
        ▼
2. FastAPI receives question (/chat endpoint)
        │
        ▼
3. Question is embedded
   • Same embedding model as documents
   • Question → vector
        │
        ▼
4. Vector Database searches
   • Finds k most similar chunks (default: 4)
   • Uses cosine similarity
   • Returns relevant document chunks
        │
        ▼
5. ChatBot builds prompt
   • Combines:
     - System instructions
     - Retrieved context chunks
     - User question
        │
        ▼
6. LLM generates answer
   • OpenAI GPT processes combined prompt
   • Generates contextual answer
        │
        ▼
7. Response formatted and returned
   • Answer
   • Source documents
   • Metadata
```

## Component Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                         config.py                                │
│              (Configuration & Environment Variables)             │
└────────┬──────────────────────────────────────────────┬─────────┘
         │                                               │
         │ Settings used by all components              │
         │                                               │
    ┌────▼──────────┐                             ┌─────▼────────┐
    │ pdf_processor │◄────────────────────────────┤   main.py    │
    └────┬──────────┘                             │  (FastAPI)   │
         │                                         └─────┬────────┘
         │ Provides documents                            │
         │                                               │
    ┌────▼──────────┐                                   │
    │  embeddings   │◄────────────────────────────┬─────┘
    └────┬──────────┘                             │
         │                                         │
         │ Provides embedding function            │
         │                                         │
    ┌────▼──────────┐                             │
    │  vector_db    │◄────────────────────────────┤
    └────┬──────────┘                             │
         │                                         │
         │ Provides retriever                     │
         │                                         │
    ┌────▼──────────┐                             │
    │    chat       │◄────────────────────────────┘
    └───────────────┘
```

## File Dependencies

```
main.py
  ├── config.py (settings)
  ├── pdf_processor.py (process PDFs)
  ├── embeddings.py (generate embeddings)
  ├── vector_db.py (store & retrieve)
  └── chat.py (generate answers)

pdf_processor.py
  ├── PyPDF2 (PDF reading)
  ├── pdfplumber (PDF reading alternative)
  └── LangChain (text splitting)

embeddings.py
  ├── langchain_openai (OpenAI embeddings)
  ├── sentence_transformers (local embeddings)
  └── config.py (API keys)

vector_db.py
  ├── FAISS (vector storage)
  ├── Chroma (vector storage alternative)
  └── embeddings.py (embedding function)

chat.py
  ├── langchain_openai (ChatGPT)
  ├── vector_db.py (retrieval)
  └── config.py (model settings)
```

## Directory Structure

```
rag-pdf-chatbot/
│
├── 📄 Core Application
│   ├── main.py              (FastAPI server & endpoints)
│   ├── pdf_processor.py     (PDF extraction & chunking)
│   ├── embeddings.py        (Embedding generation)
│   ├── vector_db.py         (Vector storage & retrieval)
│   ├── chat.py              (LLM & RAG logic)
│   └── config.py            (Configuration management)
│
├── 📋 Configuration
│   ├── requirements.txt     (Python dependencies)
│   ├── .env.example         (Environment template)
│   └── .gitignore          (Git ignore rules)
│
├── 🐳 Docker
│   ├── Dockerfile           (Container definition)
│   └── docker-compose.yml   (Orchestration)
│
├── 🧪 Testing & Examples
│   ├── test_api.py          (API tests)
│   └── example_usage.py     (Usage examples)
│
├── 🚀 Scripts
│   ├── setup.sh             (Setup automation)
│   └── start.sh             (Server start script)
│
├── 📚 Documentation
│   ├── README.md            (Main documentation)
│   ├── QUICKSTART.md        (Quick start guide)
│   ├── PROJECT_SUMMARY.md   (Project summary)
│   └── ARCHITECTURE.md      (This file)
│
└── 📁 Runtime Directories (created automatically)
    ├── uploads/             (Uploaded PDFs)
    ├── vector_store/        (Vector database)
    └── venv/                (Python virtual environment)
```

## API Endpoint Flow

```
GET /
  └── Returns API information

GET /health
  └── Health check status

POST /upload
  ├── Validate PDF file
  ├── Save to uploads/
  ├── Process with pdf_processor
  ├── Generate embeddings
  ├── Store in vector_db
  └── Return document ID

POST /chat
  ├── Validate question
  ├── Embed question
  ├── Retrieve relevant chunks (k=4)
  ├── Build prompt with context
  ├── Query LLM
  └── Return answer + sources

POST /conversation
  ├── Similar to /chat
  ├── Includes conversation history
  ├── Maintains context across messages
  └── Returns response with conversation_id

GET /documents
  └── List all uploaded documents

GET /stats
  └── System statistics and configuration

POST /clear-memory
  └── Clear conversation history
```

## Embedding & Retrieval Process

```
Document Chunk: "Machine learning is a subset of AI"
         │
         ▼ Embedding Model
[0.123, 0.456, 0.789, ..., 0.321]  (1536 dimensions)
         │
         ▼ Store in Vector DB
┌──────────────────────────────────┐
│  Vector Database (FAISS/Chroma)  │
│  [Index of all document vectors] │
└──────────────────────────────────┘
         │
         │ User Query: "What is ML?"
         │              ▼ Embed
         │     [0.119, 0.442, 0.801, ...]
         │              │
         │              ▼ Similarity Search
         │     ┌─────────────────────┐
         │     │  Cosine Similarity  │
         │     │  Score: 0.95        │
         │     └─────────────────────┘
         │              │
         ▼              ▼
Retrieved: "Machine learning is a subset of AI"
```

## Technology Stack Layers

```
┌─────────────────────────────────────────┐
│         Application Layer                │
│    FastAPI + Custom Business Logic      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         RAG Framework Layer              │
│    LangChain (Chains, Retrievers)       │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         AI/ML Layer                      │
│  OpenAI API + Sentence Transformers     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Data Layer                       │
│    FAISS/Chroma Vector Database         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Storage Layer                    │
│    File System (PDFs, Vectors)          │
└─────────────────────────────────────────┘
```

## Scaling Considerations

```
Single Server (Current)
  ├── All components on one machine
  └── Good for: Development, small deployments

Horizontal Scaling
  ├── Multiple API servers (load balanced)
  ├── Shared vector database
  └── Good for: Medium traffic

Distributed Architecture
  ├── Separate services:
  │   ├── API Gateway
  │   ├── Processing Service
  │   ├── Vector DB Cluster
  │   └── Storage Service
  └── Good for: High traffic, large scale
```

---

This architecture is designed to be:
- **Modular**: Each component is independent
- **Scalable**: Can be deployed in various configurations
- **Extensible**: Easy to add new features
- **Maintainable**: Clear separation of concerns
