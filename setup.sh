#!/bin/bash

# RAG PDF Chatbot - Quick Start Script

echo "==================================="
echo "RAG PDF Chatbot - Quick Start"
echo "==================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  Warning: .env file not found"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "Please edit .env and add your OpenAI API key:"
    echo "  OPENAI_API_KEY=your_key_here"
    echo ""
    read -p "Press Enter to continue after setting your API key..."
fi

# Create necessary directories
mkdir -p uploads vector_store

echo ""
echo "==================================="
echo "Setup complete!"
echo "==================================="
echo ""
echo "To start the server, run:"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --reload"
echo ""
echo "Or simply run:"
echo "  ./start.sh"
echo ""
