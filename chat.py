"""
Chat Module
Handles LLM queries and response generation using RAG.
"""

from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from config import settings


class ChatBot:
    """
    Manages chat interactions with LLM using RAG.
    """
    
    def __init__(
        self,
        vector_db,
        model_name: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize chatbot.
        
        Args:
            vector_db: VectorDatabase instance
            model_name: LLM model name
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            openai_api_key: OpenAI API key
        """
        self.vector_db = vector_db
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=openai_api_key or settings.OPENAI_API_KEY
        )
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        
        # Create custom prompt
        self.qa_prompt_template = """You are an intelligent assistant helping users understand documents. 
Use the following pieces of context to answer the question at the end. 
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
Provide detailed, accurate answers citing specific parts of the context when relevant.

Context:
{context}

Question: {question}

Detailed Answer:"""
    
    def ask(
        self,
        question: str,
        return_sources: bool = True,
        k: int = 4
    ) -> Dict[str, Any]:
        """
        Ask a question and get an answer with sources.
        
        Args:
            question: User's question
            return_sources: Whether to return source documents
            k: Number of source documents to retrieve
            
        Returns:
            Dictionary with answer and optionally sources
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        try:
            # Retrieve relevant documents
            docs = self.vector_db.similarity_search(question, k=k)
            
            if not docs:
                return {
                    "question": question,
                    "answer": "I don't have any documents to answer this question. Please upload a PDF first."
                }
            
            # Build context from documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create prompt
            prompt = self.qa_prompt_template.format(context=context, question=question)
            
            # Query LLM
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
            result = {
                "question": question,
                "answer": response.content
            }
            
            if return_sources:
                sources = []
                for doc in docs:
                    sources.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    })
                result["sources"] = sources
            
            return result
            
        except Exception as e:
            raise Exception(f"Error processing question: {str(e)}")
    
    def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Have a conversational chat with context from previous messages.
        
        Args:
            message: User's message
            conversation_id: Optional conversation ID for tracking
            
        Returns:
            Dictionary with response
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")
        
        try:
            # Retrieve relevant documents
            docs = self.vector_db.similarity_search(message, k=4)
            
            # Build context
            context = "\n\n".join([doc.page_content for doc in docs]) if docs else "No relevant documents found."
            
            # Build conversation history
            messages = []
            messages.append(SystemMessage(content="You are a helpful assistant that answers questions based on document context. Use the conversation history to provide contextual responses."))
            
            # Add conversation history
            for msg in self.conversation_history[-6:]:  # Last 6 messages
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
            
            # Add current message with context
            current_prompt = f"Context:\n{context}\n\nQuestion: {message}"
            messages.append(HumanMessage(content=current_prompt))
            
            # Query LLM
            response = self.llm.invoke(messages)
            
            # Store in history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": response.content})
            
            result = {
                "message": message,
                "response": response.content,
                "conversation_id": conversation_id
            }
            
            if docs:
                sources = []
                for doc in docs:
                    sources.append({
                        "content": doc.page_content[:200] + "...",
                        "metadata": doc.metadata
                    })
                result["sources"] = sources
            
            return result
            
        except Exception as e:
            raise Exception(f"Error in conversation: {str(e)}")
    
    def direct_query(self, prompt: str) -> str:
        """
        Query the LLM directly without RAG context.
        
        Args:
            prompt: Direct prompt to LLM
            
        Returns:
            LLM response as string
        """
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            raise Exception(f"Error in direct query: {str(e)}")
    
    def get_relevant_documents(
        self,
        query: str,
        k: int = 4,
        with_scores: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get relevant documents without generating an answer.
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            with_scores: Whether to include relevance scores
            
        Returns:
            List of relevant documents
        """
        try:
            if with_scores:
                results = self.vector_db.similarity_search_with_score(query, k=k)
                documents = []
                for doc, score in results:
                    documents.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": float(score)
                    })
            else:
                results = self.vector_db.similarity_search(query, k=k)
                documents = []
                for doc in results:
                    documents.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    })
            
            return documents
            
        except Exception as e:
            raise Exception(f"Error retrieving documents: {str(e)}")
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history.
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history
    
    def update_model_settings(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Update model settings.
        
        Args:
            temperature: New temperature value
            max_tokens: New max tokens value
        """
        if temperature is not None:
            self.temperature = temperature
        if max_tokens is not None:
            self.max_tokens = max_tokens
        
        # Reinitialize LLM with new settings
        self.llm = ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            openai_api_key=settings.OPENAI_API_KEY
        )


# Example usage
if __name__ == "__main__":
    from embeddings import EmbeddingGenerator
    from vector_db import VectorDatabase
    from langchain.docstore.document import Document
    
    try:
        # Initialize components
        embedding_gen = EmbeddingGenerator(provider="sentence-transformers")
        embeddings = embedding_gen.get_langchain_embeddings()
        
        vector_db = VectorDatabase(
            embeddings=embeddings,
            db_type="faiss"
        )
        
        # Create sample documents
        documents = [
            Document(
                page_content="Python is a high-level programming language known for its simplicity and readability.",
                metadata={"source": "python_doc", "page": 1}
            ),
            Document(
                page_content="Machine learning is a subset of AI that enables systems to learn from data.",
                metadata={"source": "ml_doc", "page": 1}
            )
        ]
        
        vector_db.create_from_documents(documents)
        
        # Initialize chatbot
        chatbot = ChatBot(vector_db, model_name="gpt-3.5-turbo")
        
        # Ask a question
        question = "What is Python?"
        response = chatbot.ask(question)
        
        print(f"Q: {question}")
        print(f"A: {response['answer']}")
        
        if 'sources' in response:
            print(f"\nSources:")
            for i, source in enumerate(response['sources'], 1):
                print(f"{i}. {source['content'][:100]}...")
        
    except Exception as e:
        print(f"Error: {str(e)}")
