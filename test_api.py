"""
Test Suite for RAG PDF Chatbot
Run with: pytest test_api.py
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import os


client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "version" in response.json()


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


def test_stats_endpoint():
    """Test stats endpoint."""
    response = client.get("/stats")
    assert response.status_code == 200
    assert "app_name" in response.json()
    assert "version" in response.json()


def test_list_documents():
    """Test listing documents."""
    response = client.get("/documents")
    assert response.status_code == 200
    assert "documents" in response.json()
    assert "total" in response.json()


def test_chat_without_documents():
    """Test chat endpoint without uploading documents first."""
    response = client.post(
        "/chat",
        json={"question": "What is this document about?"}
    )
    # Should fail because no documents are uploaded
    assert response.status_code == 400


def test_conversation_history():
    """Test getting conversation history."""
    response = client.get("/conversation-history")
    assert response.status_code == 200
    assert "history" in response.json()


def test_clear_memory():
    """Test clearing conversation memory."""
    response = client.post("/clear-memory")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


# Note: File upload tests would require actual PDF files
# Add more comprehensive tests with sample PDFs as needed

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
