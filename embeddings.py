"""
Embeddings Module
Handles text embedding generation using OpenAI or other providers.
"""

from typing import List, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None
import numpy as np
from config import settings


class EmbeddingGenerator:
    """
    Generates embeddings for text using various embedding models.
    Supports OpenAI embeddings and local Sentence Transformers.
    """
    
    def __init__(
        self,
        provider: str = "openai",
        model_name: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize embedding generator.
        
        Args:
            provider: Embedding provider ('openai' or 'sentence-transformers')
            model_name: Name of the embedding model
            openai_api_key: OpenAI API key (if using OpenAI)
        """
        self.provider = provider.lower()
        self.model_name = model_name
        self.embeddings: Optional[Embeddings] = None
        self.local_model = None
        
        if self.provider == "openai":
            self._init_openai(openai_api_key or settings.OPENAI_API_KEY, model_name)
        elif self.provider == "sentence-transformers":
            self._init_sentence_transformers(model_name)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _init_openai(self, api_key: str, model_name: Optional[str] = None):
        """
        Initialize OpenAI embeddings.
        
        Args:
            api_key: OpenAI API key
            model_name: Model name (defaults to text-embedding-3-small)
        """
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.model_name = model_name or "text-embedding-3-small"
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=api_key,
            model=self.model_name
        )
        print(f"Initialized OpenAI embeddings with model: {self.model_name}")
    
    def _init_sentence_transformers(self, model_name: Optional[str] = None):
        """
        Initialize Sentence Transformers embeddings (local, free).
        
        Args:
            model_name: Model name (defaults to all-MiniLM-L6-v2)
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise Exception("sentence-transformers is not installed. Install with: pip install sentence-transformers")
        
        self.model_name = model_name or "all-MiniLM-L6-v2"
        try:
            self.local_model = SentenceTransformer(self.model_name)
            print(f"Initialized Sentence Transformer model: {self.model_name}")
        except Exception as e:
            raise Exception(f"Error loading Sentence Transformer model: {str(e)}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            if self.provider == "openai":
                return self.embeddings.embed_query(text)
            elif self.provider == "sentence-transformers":
                embedding = self.local_model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("No valid texts to embed")
        
        try:
            if self.provider == "openai":
                return self.embeddings.embed_documents(valid_texts)
            elif self.provider == "sentence-transformers":
                embeddings = self.local_model.encode(
                    valid_texts,
                    convert_to_numpy=True,
                    show_progress_bar=len(valid_texts) > 10
                )
                return embeddings.tolist()
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    def get_langchain_embeddings(self) -> Embeddings:
        """
        Get LangChain-compatible embeddings object.
        
        Returns:
            LangChain Embeddings object
        """
        if self.provider == "openai":
            return self.embeddings
        elif self.provider == "sentence-transformers":
            # Create a wrapper for Sentence Transformers
            return SentenceTransformerEmbeddings(self.local_model)
        else:
            raise ValueError(f"Cannot get LangChain embeddings for provider: {self.provider}")
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Embedding dimension
        """
        if self.provider == "openai":
            # OpenAI embedding dimensions
            if "text-embedding-3-small" in self.model_name:
                return 1536
            elif "text-embedding-3-large" in self.model_name:
                return 3072
            elif "text-embedding-ada-002" in self.model_name:
                return 1536
            else:
                # Default, should query the model
                return 1536
        elif self.provider == "sentence-transformers":
            return self.local_model.get_sentence_embedding_dimension()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0 to 1)
        """
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        
        return float(dot_product / (norm_v1 * norm_v2))


class SentenceTransformerEmbeddings(Embeddings):
    """
    LangChain-compatible wrapper for Sentence Transformers.
    """
    
    def __init__(self, model: SentenceTransformer):
        self.model = model
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()


# Example usage
if __name__ == "__main__":
    # Using OpenAI embeddings
    try:
        embedding_gen = EmbeddingGenerator(provider="openai")
        
        # Embed single text
        text = "This is a sample document about artificial intelligence."
        embedding = embedding_gen.embed_text(text)
        print(f"Generated embedding with dimension: {len(embedding)}")
        
        # Embed multiple texts
        texts = [
            "Machine learning is a subset of AI.",
            "Natural language processing enables computers to understand text.",
            "Deep learning uses neural networks."
        ]
        embeddings = embedding_gen.embed_documents(texts)
        print(f"Generated {len(embeddings)} embeddings")
        
        # Calculate similarity
        similarity = embedding_gen.cosine_similarity(embeddings[0], embeddings[1])
        print(f"Similarity between first two texts: {similarity:.4f}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nTrying with Sentence Transformers (local, free)...")
        
        # Fallback to local model
        try:
            embedding_gen = EmbeddingGenerator(provider="sentence-transformers")
            embedding = embedding_gen.embed_text(text)
            print(f"Generated embedding with dimension: {len(embedding)}")
        except Exception as e2:
            print(f"Error with Sentence Transformers: {str(e2)}")
