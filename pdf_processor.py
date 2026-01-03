"""
PDF Processor Module
Handles PDF text extraction, cleaning, and chunking.
"""

import os
import re
from typing import List, Dict, Any
import PyPDF2
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class PDFProcessor:
    """
    Processes PDF documents for RAG applications.
    Extracts, cleans, and chunks PDF text.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        use_pdfplumber: bool = True
    ):
        """
        Initialize PDF processor.
        
        Args:
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
            use_pdfplumber: Use pdfplumber (True) or PyPDF2 (False)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_pdfplumber = use_pdfplumber
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """
        Extract text from PDF using PyPDF2.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n[Page {page_num + 1}]\n{page_text}"
        except Exception as e:
            raise Exception(f"Error extracting text with PyPDF2: {str(e)}")
        
        return text
    
    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """
        Extract text from PDF using pdfplumber (better for complex PDFs).
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n[Page {page_num + 1}]\n{page_text}"
        except Exception as e:
            raise Exception(f"Error extracting text with pdfplumber: {str(e)}")
        
        return text
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and special characters.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\?\!\:\;\-\(\)\[\]\"\'\/\n]', '', text)
        
        # Normalize line breaks
        text = re.sub(r'\n+', '\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def process_pdf(self, pdf_path: str, clean: bool = True) -> str:
        """
        Extract and optionally clean text from PDF.
        
        Args:
            pdf_path: Path to the PDF file
            clean: Whether to clean the extracted text
            
        Returns:
            Processed text
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Extract text
        if self.use_pdfplumber:
            text = self.extract_text_pdfplumber(pdf_path)
        else:
            text = self.extract_text_pypdf2(pdf_path)
        
        # Clean text if requested
        if clean:
            text = self.clean_text(text)
        
        return text
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Document]:
        """
        Split text into chunks for embedding.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of Document objects with chunked text
        """
        if not text:
            return []
        
        # Create documents with metadata
        base_metadata = metadata or {}
        chunks = self.text_splitter.split_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            doc_metadata = {
                **base_metadata,
                "chunk_id": i,
                "total_chunks": len(chunks)
            }
            documents.append(Document(page_content=chunk, metadata=doc_metadata))
        
        return documents
    
    def process_and_chunk(
        self,
        pdf_path: str,
        metadata: Dict[str, Any] = None,
        clean: bool = True
    ) -> List[Document]:
        """
        Complete pipeline: extract, clean, and chunk PDF.
        
        Args:
            pdf_path: Path to the PDF file
            metadata: Optional metadata to attach to chunks
            clean: Whether to clean the extracted text
            
        Returns:
            List of Document objects ready for embedding
        """
        # Extract and clean text
        text = self.process_pdf(pdf_path, clean=clean)
        
        # Add file metadata
        file_metadata = {
            "source": pdf_path,
            "filename": os.path.basename(pdf_path),
            **(metadata or {})
        }
        
        # Chunk text
        documents = self.chunk_text(text, metadata=file_metadata)
        
        return documents
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get metadata information about a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF metadata
        """
        info = {
            "filename": os.path.basename(pdf_path),
            "file_size": os.path.getsize(pdf_path),
            "pages": 0,
            "title": "",
            "author": "",
            "creation_date": ""
        }
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                info["pages"] = len(pdf_reader.pages)
                
                if pdf_reader.metadata:
                    info["title"] = pdf_reader.metadata.get("/Title", "")
                    info["author"] = pdf_reader.metadata.get("/Author", "")
                    info["creation_date"] = pdf_reader.metadata.get("/CreationDate", "")
        except Exception as e:
            print(f"Warning: Could not extract PDF metadata: {str(e)}")
        
        return info


# Example usage
if __name__ == "__main__":
    # Initialize processor
    processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
    
    # Process a PDF
    pdf_path = "sample.pdf"
    
    try:
        # Get PDF info
        info = processor.get_pdf_info(pdf_path)
        print(f"PDF Info: {info}")
        
        # Process and chunk
        documents = processor.process_and_chunk(pdf_path)
        print(f"Created {len(documents)} chunks")
        
        # Print first chunk
        if documents:
            print(f"\nFirst chunk preview:")
            print(documents[0].page_content[:200])
            print(f"\nMetadata: {documents[0].metadata}")
    except Exception as e:
        print(f"Error: {str(e)}")
