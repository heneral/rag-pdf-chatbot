#!/bin/bash

# RAG PDF Chatbot - Start Server Script

echo "Starting RAG PDF Chatbot..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Using default settings."
fi

# Start the server
echo "Starting server at http://localhost:8000"
echo "API documentation available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
