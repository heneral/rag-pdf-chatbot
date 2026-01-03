"""
FastAPI Main Application
RESTful API for RAG PDF Chatbot.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import uuid
import shutil
from datetime import datetime

from config import settings
from pdf_processor import PDFProcessor
from embeddings import EmbeddingGenerator
from vector_db import VectorDatabase
from chat import ChatBot


# Pydantic models for request/response
class ChatRequest(BaseModel):
    question: str
    k: Optional[int] = 4
    return_sources: Optional[bool] = True


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: Optional[List[Dict[str, Any]]] = None


class ConversationRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class DocumentInfo(BaseModel):
    id: str
    filename: str
    upload_date: str
    pages: int
    file_size: int


class StatusResponse(BaseModel):
    status: str
    message: str


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A RAG-based PDF chatbot API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Global instances (will be initialized on startup)
pdf_processor: Optional[PDFProcessor] = None
embedding_generator: Optional[EmbeddingGenerator] = None
vector_db: Optional[VectorDatabase] = None
chatbot: Optional[ChatBot] = None

# Document tracking
documents_db: Dict[str, DocumentInfo] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global pdf_processor, embedding_generator, vector_db, chatbot
    
    try:
        # Initialize PDF processor
        pdf_processor = PDFProcessor(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        # Initialize embedding generator
        embedding_generator = EmbeddingGenerator(
            provider=settings.EMBEDDING_PROVIDER,
            model_name=settings.EMBEDDING_MODEL
        )
        
        # Initialize vector database
        embeddings = embedding_generator.get_langchain_embeddings()
        vector_db = VectorDatabase(
            embeddings=embeddings,
            db_type=settings.VECTOR_DB_TYPE,
            persist_directory=settings.VECTOR_DB_PATH
        )
        
        # Try to load existing vector store
        try:
            vector_db.load_local()
            print("Loaded existing vector store")
        except:
            print("No existing vector store found, will create new one on first upload")
        
        # Initialize chatbot
        if vector_db.vector_store:
            chatbot = ChatBot(
                vector_db=vector_db,
                model_name=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS
            )
            print("Chatbot initialized successfully")
        
        print(f"{settings.APP_NAME} started successfully!")
        
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "endpoints": {
            "upload": "/upload",
            "chat": "/chat",
            "documents": "/documents",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "vector_db_initialized": vector_db.vector_store is not None if vector_db else False,
        "chatbot_initialized": chatbot is not None
    }


@app.post("/upload", response_model=StatusResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF file.
    
    Args:
        file: PDF file to upload
        
    Returns:
        Status response with document ID
    """
    global chatbot
    
    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
        )
    
    try:
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Save file temporarily
        file_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Process PDF
        documents = pdf_processor.process_and_chunk(
            pdf_path=file_path,
            metadata={"document_id": doc_id}
        )
        
        # Get PDF info
        pdf_info = pdf_processor.get_pdf_info(file_path)
        
        # Add to vector database
        if vector_db.vector_store is None:
            vector_db.create_from_documents(documents)
        else:
            vector_db.add_documents(documents)
        
        # Save vector store
        vector_db.save_local()
        
        # Initialize or reinitialize chatbot
        if chatbot is None:
            chatbot = ChatBot(
                vector_db=vector_db,
                model_name=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS
            )
        
        # Store document info
        documents_db[doc_id] = DocumentInfo(
            id=doc_id,
            filename=file.filename,
            upload_date=datetime.now().isoformat(),
            pages=pdf_info.get("pages", 0),
            file_size=pdf_info.get("file_size", 0)
        )
        
        # Clean up temporary file (optional, keep for reference)
        # os.remove(file_path)
        
        return StatusResponse(
            status="success",
            message=f"PDF uploaded and indexed successfully. Document ID: {doc_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Ask a question about uploaded documents.
    
    Args:
        request: Chat request with question
        
    Returns:
        Chat response with answer and sources
    """
    if chatbot is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents uploaded yet. Please upload a PDF first."
        )
    
    try:
        response = chatbot.ask(
            question=request.question,
            return_sources=request.return_sources,
            k=request.k
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )


@app.post("/conversation")
async def conversation_endpoint(request: ConversationRequest):
    """
    Have a conversational chat with context.
    
    Args:
        request: Conversation request
        
    Returns:
        Conversation response
    """
    if chatbot is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents uploaded yet. Please upload a PDF first."
        )
    
    try:
        response = chatbot.chat(
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in conversation: {str(e)}"
        )


@app.get("/documents")
async def list_documents():
    """
    List all uploaded documents.
    
    Returns:
        List of document information
    """
    return {
        "documents": list(documents_db.values()),
        "total": len(documents_db)
    }


@app.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """
    Get information about a specific document.
    
    Args:
        doc_id: Document ID
        
    Returns:
        Document information
    """
    if doc_id not in documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return documents_db[doc_id]


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """
    Delete a document (note: doesn't remove from vector store).
    
    Args:
        doc_id: Document ID
        
    Returns:
        Status response
    """
    if doc_id not in documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Remove from tracking
    del documents_db[doc_id]
    
    # Remove file if exists
    for filename in os.listdir(settings.UPLOAD_DIR):
        if filename.startswith(doc_id):
            os.remove(os.path.join(settings.UPLOAD_DIR, filename))
    
    return StatusResponse(
        status="success",
        message=f"Document {doc_id} deleted"
    )


@app.post("/clear-memory")
async def clear_memory():
    """
    Clear conversation memory.
    
    Returns:
        Status response
    """
    if chatbot:
        chatbot.clear_memory()
    
    return StatusResponse(
        status="success",
        message="Conversation memory cleared"
    )


@app.get("/conversation-history")
async def get_conversation_history():
    """
    Get conversation history.
    
    Returns:
        Conversation history
    """
    if chatbot is None:
        return {"history": []}
    
    return {
        "history": chatbot.get_conversation_history()
    }


@app.get("/stats")
async def get_stats():
    """
    Get system statistics.
    
    Returns:
        System statistics
    """
    stats = {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "documents_uploaded": len(documents_db),
        "vector_db_stats": vector_db.get_stats() if vector_db else {},
        "settings": {
            "embedding_provider": settings.EMBEDDING_PROVIDER,
            "vector_db_type": settings.VECTOR_DB_TYPE,
            "llm_model": settings.LLM_MODEL,
            "chunk_size": settings.CHUNK_SIZE,
            "retrieval_k": settings.RETRIEVAL_K
        }
    }
    
    return stats


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An internal error occurred",
            "detail": str(exc) if settings.DEBUG else None
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
