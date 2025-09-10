import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

class UserMemoryManager:
    """Manages separate conversation memory for each user"""
    
    def __init__(self, memory_window: int = 10):
        self.user_memories: Dict[str, ConversationBufferWindowMemory] = {}
        self.memory_window = memory_window
        self.user_sessions: Dict[str, Dict] = {}
    
    def get_user_memory(self, user_id: str) -> ConversationBufferWindowMemory:
        """Get or create memory for a specific user"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = ConversationBufferWindowMemory(
                k=self.memory_window,
                return_messages=True
            )
            self.user_sessions[user_id] = {
                "created_at": datetime.now(),
                "message_count": 0,
                "last_activity": datetime.now()
            }
        
        self.user_sessions[user_id]["last_activity"] = datetime.now()
        return self.user_memories[user_id]
    
    def add_message(self, user_id: str, human_message: str, ai_message: str):
        """Add a conversation turn to user's memory"""
        memory = self.get_user_memory(user_id)
        memory.chat_memory.add_user_message(human_message)
        memory.chat_memory.add_ai_message(ai_message)
        self.user_sessions[user_id]["message_count"] += 1
    
    def clear_user_memory(self, user_id: str):
        """Clear memory for a specific user"""
        if user_id in self.user_memories:
            self.user_memories[user_id].clear()
            self.user_sessions[user_id]["message_count"] = 0
    
    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """Get formatted conversation history for a user"""
        if user_id not in self.user_memories:
            return []
        
        memory = self.user_memories[user_id]
        messages = memory.chat_memory.messages
        
        history = []
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                history.append({
                    "user": messages[i].content,
                    "assistant": messages[i + 1].content,
                    "timestamp": datetime.now().isoformat()
                })
        
        return history

class AdaptiveKnowledgeChatbot:
    """Enhanced chatbot with user-specific memory and WebSocket support"""
    
    def __init__(self, collection_name: str = "manuals"):
        self.collection_name = collection_name
        self.memory_manager = UserMemoryManager()
        
        # Initialize components
        self._init_vectorstore()
        self._init_llm()
        
    def _init_vectorstore(self):
        """Initialize ChromaDB vectorstore"""
        try:
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print(f"✅ Connected to vectorstore: {self.collection.count()} documents")
        except Exception as e:
            print(f"❌ Failed to initialize vectorstore: {e}")
            raise
    
    def _init_llm(self):
        """Initialize Groq LLM"""
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            self.llm = ChatGroq(
                api_key=api_key,
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=1024
            )
            print("✅ Connected to Groq LLM")
        except Exception as e:
            print(f"❌ Failed to initialize LLM: {e}")
            raise
    
    def _retrieve_context(self, query: str, k: int = 5) -> List[str]:
        """Retrieve relevant context from vectorstore"""
        try:
            query_embedding = self.embedding_model.embed_query(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )
            
            if results["documents"] and results["documents"][0]:
                return results["documents"][0]
            return []
        except Exception as e:
            print(f"❌ Context retrieval error: {e}")
            return []
    
    def _calculate_confidence(self, query: str, context: List[str]) -> float:
        """Calculate confidence score based on context relevance"""
        if not context:
            return 0.0
        
        query_words = set(query.lower().split())
        context_text = " ".join(context).lower()
        context_words = set(context_text.split())
        
        # Simple overlap-based confidence
        overlap = len(query_words.intersection(context_words))
        confidence = min(overlap / len(query_words), 1.0) if query_words else 0.0
        
        return confidence
    
    def ask_question(self, query: str, user_id: str = "default") -> Dict[str, Any]:
        """Ask a question with user-specific memory"""
        try:
            # Retrieve relevant context
            context = self._retrieve_context(query)
            confidence = self._calculate_confidence(query, context)
            
            # Get user memory
            memory = self.memory_manager.get_user_memory(user_id)
            conversation_history = memory.chat_memory.messages[-6:] if memory.chat_memory.messages else []
            
            # Build context-aware prompt
            context_text = "\n".join(context[:3]) if context else "No relevant context found."
            
            # Format conversation history
            history_text = ""
            if conversation_history:
                history_text = "\n\nPrevious conversation:\n"
                for i in range(0, len(conversation_history), 2):
                    if i + 1 < len(conversation_history):
                        history_text += f"User: {conversation_history[i].content}\n"
                        history_text += f"Assistant: {conversation_history[i + 1].content}\n"
            
            prompt = f"""You are a helpful AI assistant with access to a knowledge base. Answer the user's question based on the provided context and conversation history.

                Context from knowledge base:
                {context_text}

                Previous conversation history:
                {history_text}

                User question: {query}

                Instructions:
                - Use the context and conversation history to provide accurate answers
                - If the information isn't in the context, say "I don't have enough information about that topic"
                - Be conversational and remember previous parts of our conversation
                - Keep responses concise but helpful
                - No need of any citations or references or preamble like "Based on the provided context, etc."
                Answer:"""
            
            # Get response from LLM
            response = self.llm.invoke([HumanMessage(content=prompt)])
            answer = response.content
            
            # Add to user memory
            self.memory_manager.add_message(user_id, query, answer)
            
            return {
                "success": True,
                "answer": answer,
                "context": context,
                "confidence": confidence,
                "user_id": user_id
            }
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            return {
                "success": False,
                "answer": error_msg,
                "context": [],
                "confidence": 0.0,
                "user_id": user_id
            }
    
    def clear_user_memory(self, user_id: str):
        """Clear memory for a specific user"""
        self.memory_manager.clear_user_memory(user_id)
        print(f"🧹 Cleared conversation memory for user: {user_id}")
    
    def get_user_conversation_history(self, user_id: str) -> List[Dict]:
        """Get conversation history for a user"""
        return self.memory_manager.get_conversation_history(user_id)
    
    def get_vectorstore_info(self) -> Dict[str, Any]:
        """Get information about the vectorstore"""
        try:
            count = self.collection.count()
            return {
                "document_count": count,
                "collection_name": self.collection_name
            }
        except Exception as e:
            print(f"❌ Error getting vectorstore info: {e}")
            return {"document_count": 0, "collection_name": self.collection_name}
    
    def get_active_users(self) -> List[Dict]:
        """Get list of active users and their session info"""
        users = []
        for user_id, session in self.memory_manager.user_sessions.items():
            users.append({
                "user_id": user_id,
                "created_at": session["created_at"].isoformat(),
                "last_activity": session["last_activity"].isoformat(),
                "message_count": session["message_count"]
            })
        return users
