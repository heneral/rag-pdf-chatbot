# Quick Start Guide

## 🚀 Getting Started

### 1. Initial Setup

```bash
# Run the setup script
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit the `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

To get an API key:
1. Visit https://platform.openai.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new secret key

### 3. Start the Server

```bash
# Using the start script
./start.sh

# Or manually
source venv/bin/activate
uvicorn main:app --reload
```

The server will start at: http://localhost:8000

API Documentation (Swagger UI): http://localhost:8000/docs

## 📝 Using the API

### Option 1: Using cURL

#### Upload a PDF
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@your_document.pdf"
```

#### Ask a Question
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic of the document?",
    "k": 4,
    "return_sources": true
  }'
```

#### List Documents
```bash
curl http://localhost:8000/documents
```

### Option 2: Using Python Script

```python
# Use the provided example
python example_usage.py

# Or use the helper functions:
from example_usage import upload_pdf, ask_question

upload_pdf("your_document.pdf")
ask_question("What is this document about?")
```

### Option 3: Using the Swagger UI

1. Open http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

## 🐳 Using Docker

### Build and Run

```bash
# Build the image
docker build -t rag-pdf-chatbot .

# Run the container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/vector_store:/app/vector_store \
  rag-pdf-chatbot
```

### Using Docker Compose

```bash
# Create .env file with your API key
echo "OPENAI_API_KEY=your_key_here" > .env

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## 🎯 Common Use Cases

### 1. Single Document Q&A

```python
from example_usage import upload_pdf, ask_question

# Upload your PDF
upload_pdf("research_paper.pdf")

# Ask specific questions
ask_question("What are the main findings?")
ask_question("What methodology was used?")
ask_question("What are the conclusions?")
```

### 2. Multiple Document Analysis

```python
# Upload multiple PDFs
upload_pdf("document1.pdf")
upload_pdf("document2.pdf")
upload_pdf("document3.pdf")

# Ask questions across all documents
ask_question("Compare the approaches discussed in these documents")
```

### 3. Conversation Mode

```bash
curl -X POST http://localhost:8000/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about the introduction",
    "conversation_id": "user123"
  }'

# Follow-up question (maintains context)
curl -X POST http://localhost:8000/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you elaborate on that?",
    "conversation_id": "user123"
  }'
```

## ⚙️ Configuration

### Environment Variables

Edit `.env` to customize:

```bash
# Use free local embeddings (no API key needed)
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Use cheaper OpenAI model
LLM_MODEL=gpt-3.5-turbo

# Adjust chunk size for better context
CHUNK_SIZE=1500
CHUNK_OVERLAP=300

# Retrieve more context
RETRIEVAL_K=6
```

### Using Local Models (Free)

To avoid OpenAI API costs for embeddings:

```bash
# In .env
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

Note: You still need OpenAI API for the LLM (GPT) unless you integrate a local model.

## 🧪 Testing

```bash
# Run tests
pytest test_api.py -v

# Check health
curl http://localhost:8000/health

# Get stats
curl http://localhost:8000/stats
```

## 📊 Monitoring

### Check System Stats
```bash
curl http://localhost:8000/stats
```

### View Uploaded Documents
```bash
curl http://localhost:8000/documents
```

### Check Conversation History
```bash
curl http://localhost:8000/conversation-history
```

### Clear Conversation Memory
```bash
curl -X POST http://localhost:8000/clear-memory
```

## 🔧 Troubleshooting

### Server won't start
- Check if port 8000 is available: `lsof -i :8000`
- Verify Python version: `python3 --version` (need 3.10+)
- Check if virtual environment is activated

### Upload fails
- Check file size (default max: 10MB)
- Verify file is a valid PDF
- Check disk space

### Chat returns error about no documents
- Upload at least one PDF first
- Check if vector store was created successfully
- Verify `vector_store/` directory exists

### API key errors
- Verify `.env` file exists and has correct format
- Check OpenAI API key is valid
- Ensure key has proper permissions

### Out of memory
- Reduce `CHUNK_SIZE` in `.env`
- Use FAISS instead of Chroma
- Process smaller PDFs

## 🚀 Production Deployment

### Security Checklist
- [ ] Set `DEBUG=False` in production
- [ ] Use proper secrets management
- [ ] Enable HTTPS
- [ ] Add rate limiting
- [ ] Set up authentication
- [ ] Use environment-specific configs

### Performance Tips
- Use FAISS for better performance
- Implement caching for common queries
- Use async operations where possible
- Set appropriate `CHUNK_SIZE` and `RETRIEVAL_K`

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [FAISS Wiki](https://github.com/facebookresearch/faiss/wiki)

## 💡 Tips & Best Practices

1. **Start Simple**: Upload one PDF, ask basic questions, then expand
2. **Experiment with K**: Try different values for `k` (number of chunks retrieved)
3. **Use Descriptive Questions**: More specific questions get better answers
4. **Check Sources**: Review source documents to understand where answers come from
5. **Adjust Temperature**: Lower temperature (0.3) for factual, higher (0.8) for creative
6. **Monitor Costs**: Track OpenAI API usage if using paid models

## 🆘 Getting Help

- Check logs: `docker-compose logs` or terminal output
- Review API docs: http://localhost:8000/docs
- Test with example script: `python example_usage.py`
- Check GitHub issues or create a new one

---

Happy chatting with your PDFs! 🎉
