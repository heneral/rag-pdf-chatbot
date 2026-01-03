# RAG PDF Chatbot

A chatbot that can answer questions from uploaded PDFs using Retrieval-Augmented Generation (RAG). The bot reads PDF content, embeds it into a vector database, retrieves relevant chunks, and generates accurate answers with an LLM.

## 📋 Table of Contents

- [Overview](#overview)
- [Motivation](#motivation)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Installation Guide](#installation-guide)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Future Improvements](#future-improvements)
- [Security & Best Practices](#security--best-practices)
- [References & Resources](#references--resources)

## 🎯 Overview

Most traditional chatbots:
- Answer based on pre-defined scripts
- Cannot reference large documents
- Miss context in long PDFs

This project demonstrates how to build an intelligent assistant that understands documents and provides contextual, accurate responses.

## 💡 Motivation

This project addresses the limitations of traditional chatbots by:
- Enabling semantic search over documents
- Providing AI-powered Q&A with context
- Supporting structured responses (JSON optional)
- Offering a scalable backend API

## ✨ Key Features

- **Upload one or multiple PDFs**: Process single or batch PDF documents
- **Semantic search over documents**: Find relevant information using vector similarity
- **AI-powered Q&A with context**: Generate accurate answers based on document content
- **Structured responses**: Optional JSON response format
- **Scalable backend API**: Built with FastAPI for high performance

## 🛠️ Tech Stack

- **Programming Language**: Python 3.10+
- **Backend**: FastAPI
- **AI / LLM**: OpenAI GPT-4, Claude, or other LLM APIs
- **RAG Framework**: LangChain
- **Vector Database**: FAISS / Chroma / Pinecone / Qdrant
- **PDF Processing**: PyPDF2 / pdfplumber
- **Environment Management**: Virtualenv / Poetry
- **Deployment**: Docker, AWS / GCP / Azure (optional)

## 🏗️ System Architecture

```
+----------------+        +-----------------+       +----------------+
|                |        |                 |       |                |
| PDF Documents  |  --->  |   Embedding     |  ---> |  Vector DB     |
|                |        |   Generation    |       |  (FAISS, etc.)|
+----------------+        +-----------------+       +----------------+
                                                      |
                                                      v
                                               +----------------+
                                               |   LLM Model    |
                                               |  (GPT-4 API)   |
                                               +----------------+
                                                      |
                                                      v
                                               +----------------+
                                               |  FastAPI API   |
                                               | /chat endpoint |
                                               +----------------+
                                                      |
                                                      v
                                               +----------------+
                                               | Frontend / CLI |
                                               +----------------+
```

### Workflow

1. User uploads PDFs → Backend extracts text
2. Text is split into chunks (chunking) → embedded into vector DB
3. User sends a question → Backend retrieves most relevant chunks
4. LLM generates answer based on retrieved context
5. Backend returns answer to user

## 📦 Installation Guide

### Prerequisites

- Python 3.10+
- Virtualenv or Poetry
- OpenAI API key or equivalent

### Steps

```bash
# Clone repo
git clone https://github.com/yourusername/rag-pdf-chatbot.git
cd rag-pdf-chatbot

# Create environment
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Set API keys (copy .env.example to .env and fill in your keys)
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📖 Usage Guide

### API Endpoints

#### 1. Upload PDF

```bash
POST /upload
Form-data: file=<pdf_file>
```

**Response:**
```json
{
  "status": "success",
  "message": "PDF uploaded and indexed.",
  "document_id": "abc123"
}
```

#### 2. Ask Question

```bash
POST /chat
```

**Request Body:**
```json
{
  "question": "What is the main topic of the document?"
}
```

**Response:**
```json
{
  "answer": "The document discusses the impact of climate change on coastal cities...",
  "sources": ["page 1", "page 3"]
}
```

#### 3. List Documents

```bash
GET /documents
```

**Response:**
```json
{
  "documents": [
    {"id": "abc123", "filename": "report.pdf", "upload_date": "2026-01-04"}
  ]
}
```

### CLI Example

```bash
# Upload PDF
curl -X POST http://localhost:8000/upload -F "file=@document.pdf"

# Ask question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the summary of chapter 2?"}'
```

## 📁 Project Structure

```
rag-pdf-chatbot/
│
├── main.py              # FastAPI backend
├── pdf_processor.py     # PDF text extraction
├── embeddings.py        # Text embedding functions
├── vector_db.py         # Vector database handling
├── chat.py              # LLM query & response
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
├── Dockerfile           # Docker configuration
├── README.md            # This file
├── uploads/             # Temporary PDF storage
└── vector_store/        # Vector database storage
```

## 🔍 How It Works (Step-by-Step)

### 1. PDF Processing
- Extract text from PDF
- Clean text (remove extra spaces, headers, footers)

### 2. Chunking
- Break long text into smaller segments (e.g., 500-1000 tokens per chunk)
- Maintain context overlap between chunks

### 3. Embedding
- Convert text chunks into vector embeddings
- Use OpenAI embeddings or similar

### 4. Vector Storage
- Store embeddings in FAISS / Pinecone / Chroma
- Enable fast similarity search

### 5. Question Handling
- Receive user query
- Retrieve top-k most relevant chunks

### 6. Answer Generation
- Pass retrieved chunks + query to LLM
- Generate context-aware answer

### 7. Return Response
- Send answer back via API / frontend

## 🚀 Future Improvements

- [ ] Multi-document support (merge embeddings)
- [ ] Summarization & highlights
- [ ] Multi-language support
- [ ] User authentication & multi-tenant support
- [ ] Caching common queries to reduce API cost
- [ ] Advanced RAG techniques (reranking, LLM-based retrieval)
- [ ] Web interface (React/Vue frontend)
- [ ] Conversation history and context
- [ ] Support for more document formats (Word, Excel, etc.)

## 🔒 Security & Best Practices

- ✅ Limit file size for uploads
- ✅ Sanitize PDF content
- ✅ API key protection via environment variables
- ✅ Guardrails for LLM responses (filter sensitive info)
- ✅ Logging & monitoring usage
- ✅ Rate limiting on API endpoints
- ✅ Input validation

## 📚 References & Resources

- [LangChain Docs](https://python.langchain.com/)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [FAISS](https://github.com/facebookresearch/faiss)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PyPDF2](https://pypdf2.readthedocs.io/)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using FastAPI, LangChain, and OpenAI**
