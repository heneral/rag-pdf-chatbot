"""
Vector Database Module
Handles vector storage and retrieval using FAISS or Chroma.
"""

import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from config import settings


class VectorDatabase:
    """
    Manages vector database operations for document retrieval.
    Supports FAISS (in-memory/file-based) and Chroma (persistent).
    """
    
    def __init__(
        self,
        embeddings: Embeddings,
        db_type: str = "faiss",
        persist_directory: str = "./vector_store"
    ):
        """
        Initialize vector database.
        
        Args:
            embeddings: Embedding function/model
            db_type: Type of vector DB ('faiss' or 'chroma')
            persist_directory: Directory to persist the vector store
        """
        self.embeddings = embeddings
        self.db_type = db_type.lower()
        self.persist_directory = persist_directory
        self.vector_store = None
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
    
    def create_from_documents(
        self,
        documents: List[Document],
        collection_name: str = "default"
    ) -> None:
        """
        Create a new vector store from documents.
        
        Args:
            documents: List of Document objects to index
            collection_name: Name for the collection/index
        """
        if not documents:
            raise ValueError("No documents provided")
        
        try:
            if self.db_type == "faiss":
                self.vector_store = FAISS.from_documents(
                    documents=documents,
                    embedding=self.embeddings
                )
                print(f"Created FAISS index with {len(documents)} documents")
                
            elif self.db_type == "chroma":
                persist_path = os.path.join(self.persist_directory, collection_name)
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=persist_path,
                    collection_name=collection_name
                )
                self.vector_store.persist()
                print(f"Created Chroma collection '{collection_name}' with {len(documents)} documents")
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
                
        except Exception as e:
            raise Exception(f"Error creating vector store: {str(e)}")
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to an existing vector store.
        
        Args:
            documents: List of Document objects to add
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Create one first.")
        
        if not documents:
            return
        
        try:
            self.vector_store.add_documents(documents)
            
            if self.db_type == "chroma":
                self.vector_store.persist()
            
            print(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            raise Exception(f"Error adding documents: {str(e)}")
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Search for similar documents.
        
        Args:
            query: Query text
            k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of most similar documents
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        try:
            if filter_dict:
                results = self.vector_store.similarity_search(
                    query=query,
                    k=k,
                    filter=filter_dict
                )
            else:
                results = self.vector_store.similarity_search(query=query, k=k)
            
            return results
            
        except Exception as e:
            raise Exception(f"Error during similarity search: {str(e)}")
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents with relevance scores.
        
        Args:
            query: Query text
            k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of tuples (Document, score)
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        try:
            if filter_dict:
                results = self.vector_store.similarity_search_with_score(
                    query=query,
                    k=k,
                    filter=filter_dict
                )
            else:
                results = self.vector_store.similarity_search_with_score(
                    query=query,
                    k=k
                )
            
            return results
            
        except Exception as e:
            raise Exception(f"Error during similarity search with score: {str(e)}")
    
    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5
    ) -> List[Document]:
        """
        Search using Maximum Marginal Relevance (MMR).
        MMR balances relevance and diversity in results.
        
        Args:
            query: Query text
            k: Number of results to return
            fetch_k: Number of candidates to consider
            lambda_mult: Diversity factor (0=max diversity, 1=max relevance)
            
        Returns:
            List of diverse relevant documents
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        try:
            results = self.vector_store.max_marginal_relevance_search(
                query=query,
                k=k,
                fetch_k=fetch_k,
                lambda_mult=lambda_mult
            )
            return results
            
        except Exception as e:
            raise Exception(f"Error during MMR search: {str(e)}")
    
    def save_local(self, path: Optional[str] = None) -> None:
        """
        Save vector store to disk (FAISS only).
        
        Args:
            path: Path to save the index (defaults to persist_directory)
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        if self.db_type != "faiss":
            print("Save operation only needed for FAISS. Chroma auto-persists.")
            return
        
        save_path = path or os.path.join(self.persist_directory, "faiss_index")
        
        try:
            self.vector_store.save_local(save_path)
            print(f"Saved FAISS index to {save_path}")
        except Exception as e:
            raise Exception(f"Error saving vector store: {str(e)}")
    
    def load_local(
        self,
        path: Optional[str] = None,
        collection_name: str = "default"
    ) -> None:
        """
        Load vector store from disk.
        
        Args:
            path: Path to load from
            collection_name: Collection name (for Chroma)
        """
        try:
            if self.db_type == "faiss":
                load_path = path or os.path.join(self.persist_directory, "faiss_index")
                
                if not os.path.exists(load_path):
                    raise FileNotFoundError(f"FAISS index not found at {load_path}")
                
                self.vector_store = FAISS.load_local(
                    load_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"Loaded FAISS index from {load_path}")
                
            elif self.db_type == "chroma":
                persist_path = path or os.path.join(self.persist_directory, collection_name)
                
                if not os.path.exists(persist_path):
                    raise FileNotFoundError(f"Chroma collection not found at {persist_path}")
                
                self.vector_store = Chroma(
                    persist_directory=persist_path,
                    embedding_function=self.embeddings,
                    collection_name=collection_name
                )
                print(f"Loaded Chroma collection '{collection_name}' from {persist_path}")
                
        except Exception as e:
            raise Exception(f"Error loading vector store: {str(e)}")
    
    def delete_collection(self, collection_name: str = "default") -> None:
        """
        Delete a collection (Chroma only).
        
        Args:
            collection_name: Name of collection to delete
        """
        if self.db_type != "chroma":
            print("Delete collection only supported for Chroma")
            return
        
        try:
            if self.vector_store:
                self.vector_store.delete_collection()
                self.vector_store = None
                print(f"Deleted Chroma collection '{collection_name}'")
        except Exception as e:
            raise Exception(f"Error deleting collection: {str(e)}")
    
    def get_retriever(self, search_type: str = "similarity", k: int = 4):
        """
        Get a LangChain retriever interface.
        
        Args:
            search_type: Type of search ('similarity' or 'mmr')
            k: Number of documents to retrieve
            
        Returns:
            LangChain Retriever object
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        return self.vector_store.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k}
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with store statistics
        """
        stats = {
            "db_type": self.db_type,
            "persist_directory": self.persist_directory,
            "initialized": self.vector_store is not None
        }
        
        if self.vector_store and self.db_type == "faiss":
            try:
                stats["num_documents"] = self.vector_store.index.ntotal
            except:
                stats["num_documents"] = "unknown"
        
        return stats


# Example usage
if __name__ == "__main__":
    from embeddings import EmbeddingGenerator
    
    # Initialize embeddings
    try:
        embedding_gen = EmbeddingGenerator(provider="sentence-transformers")
        embeddings = embedding_gen.get_langchain_embeddings()
        
        # Create vector database
        vector_db = VectorDatabase(
            embeddings=embeddings,
            db_type="faiss",
            persist_directory="./test_vector_store"
        )
        
        # Create sample documents
        documents = [
            Document(
                page_content="Machine learning is a subset of artificial intelligence.",
                metadata={"source": "doc1", "page": 1}
            ),
            Document(
                page_content="Natural language processing enables computers to understand human language.",
                metadata={"source": "doc1", "page": 2}
            ),
            Document(
                page_content="Deep learning uses neural networks with multiple layers.",
                metadata={"source": "doc2", "page": 1}
            )
        ]
        
        # Create index
        vector_db.create_from_documents(documents)
        
        # Search
        query = "What is machine learning?"
        results = vector_db.similarity_search(query, k=2)
        
        print(f"\nQuery: {query}")
        print(f"\nTop results:")
        for i, doc in enumerate(results, 1):
            print(f"\n{i}. {doc.page_content}")
            print(f"   Metadata: {doc.metadata}")
        
        # Save index
        vector_db.save_local()
        
        # Get stats
        print(f"\nVector DB Stats: {vector_db.get_stats()}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
