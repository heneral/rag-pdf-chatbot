# 🚀 Getting Started Checklist

Use this checklist to get your RAG PDF Chatbot up and running!

## ✅ Pre-Installation Checklist

- [ ] Python 3.10 or higher installed
  ```bash
  python3 --version
  ```

- [ ] pip is up to date
  ```bash
  pip install --upgrade pip
  ```

- [ ] Git is installed (optional, for cloning)
  ```bash
  git --version
  ```

- [ ] At least 2GB free disk space

- [ ] Internet connection (for installing packages)

## ✅ Installation Checklist

- [ ] Navigate to project directory
  ```bash
  cd /path/to/rag-pdf-chatbot
  ```

- [ ] Run setup script OR manual setup
  ```bash
  # Option 1: Automated
  ./setup.sh
  
  # Option 2: Manual
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

- [ ] Verify installation
  ```bash
  pip list | grep fastapi
  pip list | grep langchain
  ```

## ✅ Configuration Checklist

- [ ] Create `.env` file from template
  ```bash
  cp .env.example .env
  ```

- [ ] Get OpenAI API key
  - [ ] Visit https://platform.openai.com/
  - [ ] Sign up or log in
  - [ ] Go to API Keys section
  - [ ] Create new secret key
  - [ ] Copy the key

- [ ] Add API key to `.env`
  ```bash
  # Edit .env file
  OPENAI_API_KEY=sk-your-actual-key-here
  ```

- [ ] (Optional) Configure other settings in `.env`
  - [ ] Change LLM model (default: gpt-4-turbo-preview)
  - [ ] Adjust chunk size (default: 1000)
  - [ ] Change vector DB type (default: faiss)
  - [ ] Switch to local embeddings (sentence-transformers)

## ✅ First Run Checklist

- [ ] Start the server
  ```bash
  ./start.sh
  # OR
  source venv/bin/activate
  uvicorn main:app --reload
  ```

- [ ] Verify server is running
  - [ ] Open browser to http://localhost:8000
  - [ ] Should see API information

- [ ] Check API documentation
  - [ ] Open http://localhost:8000/docs
  - [ ] Should see Swagger UI

- [ ] Test health endpoint
  ```bash
  curl http://localhost:8000/health
  ```
  - [ ] Should return `{"status": "healthy"}`

## ✅ First Upload Checklist

- [ ] Prepare a test PDF
  - [ ] Find any PDF document
  - [ ] Place it in accessible location
  - [ ] Note the file path

- [ ] Upload via API
  ```bash
  curl -X POST http://localhost:8000/upload \
    -F "file=@/path/to/your/document.pdf"
  ```
  - [ ] Should return success message with document ID

- [ ] Or use example script
  ```python
  python example_usage.py
  # Edit the script to add your PDF path
  ```

- [ ] Verify upload
  ```bash
  curl http://localhost:8000/documents
  ```
  - [ ] Should list your uploaded document

## ✅ First Query Checklist

- [ ] Ask a simple question
  ```bash
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"question": "What is this document about?"}'
  ```

- [ ] Verify response contains:
  - [ ] Answer text
  - [ ] Source documents
  - [ ] No errors

- [ ] Try another question
  ```bash
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"question": "Summarize the main points"}'
  ```

## ✅ Testing Checklist

- [ ] Run test suite
  ```bash
  pytest test_api.py -v
  ```

- [ ] Run example usage script
  ```bash
  python example_usage.py
  ```

- [ ] Test via Swagger UI
  - [ ] Go to http://localhost:8000/docs
  - [ ] Try /upload endpoint
  - [ ] Try /chat endpoint

- [ ] Test conversation mode
  ```bash
  curl -X POST http://localhost:8000/conversation \
    -H "Content-Type: application/json" \
    -d '{"message": "Tell me about the introduction"}'
  ```

## ✅ Docker Setup Checklist (Optional)

- [ ] Docker installed
  ```bash
  docker --version
  ```

- [ ] Docker Compose installed
  ```bash
  docker-compose --version
  ```

- [ ] Create `.env` with API key

- [ ] Build image
  ```bash
  docker build -t rag-pdf-chatbot .
  ```

- [ ] Run with Docker Compose
  ```bash
  docker-compose up -d
  ```

- [ ] Check logs
  ```bash
  docker-compose logs -f
  ```

- [ ] Test container
  ```bash
  curl http://localhost:8000/health
  ```

## ✅ Troubleshooting Checklist

### Server won't start

- [ ] Check Python version (need 3.10+)
- [ ] Verify virtual environment is activated
- [ ] Check port 8000 is available
  ```bash
  lsof -i :8000
  ```
- [ ] Review error messages in terminal
- [ ] Check all dependencies installed
  ```bash
  pip install -r requirements.txt
  ```

### Upload fails

- [ ] Verify file is a valid PDF
- [ ] Check file size (default max: 10MB)
- [ ] Ensure sufficient disk space
- [ ] Check `uploads/` directory exists
- [ ] Review server logs for errors

### Chat returns "no documents" error

- [ ] Confirm PDF was uploaded successfully
- [ ] Check `vector_store/` directory exists
- [ ] Verify documents are listed
  ```bash
  curl http://localhost:8000/documents
  ```
- [ ] Restart server and try again

### OpenAI API errors

- [ ] Verify API key is correct in `.env`
- [ ] Check API key has not expired
- [ ] Confirm account has credits
- [ ] Test with different model (gpt-3.5-turbo)
- [ ] Or switch to local embeddings:
  ```bash
  # In .env
  EMBEDDING_PROVIDER=sentence-transformers
  ```

### Out of memory

- [ ] Reduce chunk size in `.env`
  ```bash
  CHUNK_SIZE=500
  ```
- [ ] Process smaller PDFs
- [ ] Use FAISS instead of Chroma
- [ ] Reduce `RETRIEVAL_K` value

## ✅ Production Deployment Checklist

- [ ] Security
  - [ ] Set `DEBUG=False` in `.env`
  - [ ] Use environment variables for secrets
  - [ ] Enable HTTPS
  - [ ] Add authentication
  - [ ] Implement rate limiting
  - [ ] Set up CORS properly

- [ ] Performance
  - [ ] Use production ASGI server (Gunicorn + Uvicorn)
  - [ ] Enable caching
  - [ ] Set up monitoring
  - [ ] Configure logging
  - [ ] Use persistent vector database

- [ ] Infrastructure
  - [ ] Set up reverse proxy (Nginx)
  - [ ] Configure firewall
  - [ ] Set up backups
  - [ ] Monitor disk space
  - [ ] Set up health checks

## 🎉 Success Criteria

You've successfully set up the RAG PDF Chatbot when:

- ✅ Server starts without errors
- ✅ Health endpoint returns healthy
- ✅ Can upload PDFs successfully
- ✅ Can ask questions and get relevant answers
- ✅ Answers include source references
- ✅ All tests pass
- ✅ API documentation is accessible

## 📚 Next Steps

Once everything is working:

1. **Read the documentation**
   - [ ] Review [README.md](README.md)
   - [ ] Check [QUICKSTART.md](QUICKSTART.md)
   - [ ] Study [ARCHITECTURE.md](ARCHITECTURE.md)

2. **Experiment with settings**
   - [ ] Try different LLM models
   - [ ] Adjust chunk size and overlap
   - [ ] Test different retrieval values (k)
   - [ ] Compare embedding providers

3. **Explore the code**
   - [ ] Read module docstrings
   - [ ] Understand the RAG pipeline
   - [ ] Review API endpoints
   - [ ] Study configuration options

4. **Build something cool!**
   - [ ] Add your own PDFs
   - [ ] Create a frontend
   - [ ] Integrate with other systems
   - [ ] Share your work!

## 💡 Tips

- Start with small PDFs for testing
- Use `gpt-3.5-turbo` to save costs during development
- Check logs frequently for debugging
- Read error messages carefully
- Ask specific questions for better answers
- Monitor OpenAI API usage

## 🆘 Need Help?

- Check [QUICKSTART.md](QUICKSTART.md) for detailed instructions
- Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for overview
- Look at [example_usage.py](example_usage.py) for code examples
- Check API docs at http://localhost:8000/docs
- Review error logs in terminal

---

**Good luck with your RAG PDF Chatbot!** 🚀

If you've checked all the boxes above, you're ready to build amazing things with AI!
