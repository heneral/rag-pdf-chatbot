"""
Example Usage Script
Demonstrates how to use the RAG PDF Chatbot API.
"""

import requests
import json
import time


BASE_URL = "http://localhost:8000"


def check_health():
    """Check if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Server is running")
            return True
        else:
            print("✗ Server returned error")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running. Start it with: uvicorn main:app --reload")
        return False


def upload_pdf(file_path):
    """Upload a PDF file."""
    print(f"\nUploading {file_path}...")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Upload successful: {result['message']}")
            return True
        else:
            print(f"✗ Upload failed: {response.json()}")
            return False
    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def ask_question(question, k=4, return_sources=True):
    """Ask a question about the uploaded documents."""
    print(f"\nQuestion: {question}")
    
    payload = {
        "question": question,
        "k": k,
        "return_sources": return_sources
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nAnswer: {result['answer']}")
            
            if return_sources and 'sources' in result:
                print(f"\nSources ({len(result['sources'])} documents):")
                for i, source in enumerate(result['sources'], 1):
                    print(f"\n  {i}. {source['content'][:150]}...")
                    if 'metadata' in source:
                        print(f"     Metadata: {source['metadata']}")
            
            return result
        else:
            print(f"✗ Error: {response.json()}")
            return None
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None


def list_documents():
    """List all uploaded documents."""
    print("\nListing uploaded documents...")
    
    try:
        response = requests.get(f"{BASE_URL}/documents")
        
        if response.status_code == 200:
            result = response.json()
            if result['total'] == 0:
                print("No documents uploaded yet.")
            else:
                print(f"\nTotal documents: {result['total']}")
                for doc in result['documents']:
                    print(f"\n  - {doc['filename']}")
                    print(f"    ID: {doc['id']}")
                    print(f"    Pages: {doc['pages']}")
                    print(f"    Uploaded: {doc['upload_date']}")
            return result
        else:
            print(f"✗ Error: {response.json()}")
            return None
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None


def get_stats():
    """Get system statistics."""
    print("\nGetting system stats...")
    
    try:
        response = requests.get(f"{BASE_URL}/stats")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nApp: {result['app_name']} v{result['version']}")
            print(f"Documents uploaded: {result['documents_uploaded']}")
            print(f"\nSettings:")
            for key, value in result['settings'].items():
                print(f"  {key}: {value}")
            return result
        else:
            print(f"✗ Error: {response.json()}")
            return None
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None


def main():
    """Main example workflow."""
    print("=" * 60)
    print("RAG PDF Chatbot - Example Usage")
    print("=" * 60)
    
    # Check if server is running
    if not check_health():
        return
    
    # Get stats
    get_stats()
    
    # List existing documents
    list_documents()
    
    # Example: Upload a PDF (replace with your PDF path)
    # pdf_path = "sample.pdf"
    # upload_pdf(pdf_path)
    
    # Example: Ask questions
    # Uncomment these after uploading a document
    
    # ask_question("What is the main topic of the document?")
    # ask_question("Can you summarize chapter 2?")
    # ask_question("What are the key findings?", k=6)
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    print("\nTo upload your own PDF:")
    print("  upload_pdf('path/to/your/document.pdf')")
    print("\nTo ask questions:")
    print("  ask_question('Your question here')")
    print("")


if __name__ == "__main__":
    main()
