from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
import json
import uuid
import asyncio
from datetime import datetime
import sys
import os

# Add the services directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from chatbot import AdaptiveKnowledgeChatbot

router = APIRouter()

class ConnectionManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_info: Dict[str, Dict] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_info[user_id] = {
            "connected_at": datetime.now().isoformat(),
            "message_count": 0
        }
        
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_info:
            del self.user_info[user_id]
            
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))
            
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_text(json.dumps(message))
            
    def get_active_users(self) -> List[Dict]:
        return [
            {"user_id": user_id, **info} 
            for user_id, info in self.user_info.items()
        ]

# Global instances
manager = ConnectionManager()
chatbot = None

def get_chatbot():
    """Get or create chatbot instance"""
    global chatbot
    if chatbot is None:
        try:
            print("🔄 Initializing chatbot...")
            chatbot = AdaptiveKnowledgeChatbot(collection_name="manuals")
            print("✅ Chatbot initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize chatbot: {e}")
            # Don't raise HTTPException here, let it be handled in the WebSocket endpoint
            return None
    return chatbot

# Initialize chatbot at startup
try:
    chatbot = get_chatbot()
except:
    print("⚠️ Chatbot initialization deferred to first connection")

@router.websocket("/test")
async def websocket_test(websocket: WebSocket):
    """Simple WebSocket test endpoint"""
    await websocket.accept()
    await websocket.send_text("Hello! WebSocket connection successful!")
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("WebSocket test disconnected")

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time chat"""
    
    try:
        # Accept connection first
        await websocket.accept()
        print(f"🔌 WebSocket connection accepted for user: {user_id}")
        
        # Then try to get chatbot
        bot = get_chatbot()
        if bot is None:
            error_msg = {
                "type": "error",
                "message": "Chatbot service is currently unavailable. Please try again later.",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(error_msg))
            await websocket.close(code=1011, reason="Chatbot unavailable")
            return
            
        # Add to connection manager
        manager.active_connections[user_id] = websocket
        manager.user_info[user_id] = {
            "connected_at": datetime.now().isoformat(),
            "message_count": 0
        }
        
        # Send welcome message
        welcome_message = {
            "type": "system",
            "message": f"Welcome! You're connected as user {user_id}",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }
        await websocket.send_text(json.dumps(welcome_message))
        
        # Send knowledge base info
        try:
            kb_info = bot.get_vectorstore_info()
            info_message = {
                "type": "system", 
                "message": f"Knowledge base loaded with {kb_info['document_count']} documents",
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            await websocket.send_text(json.dumps(info_message))
        except Exception as e:
            print(f"⚠️ Could not get knowledge base info: {e}")
            await websocket.send_text(json.dumps({
                "type": "system",
                "message": "Knowledge base status unknown",
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }))
        
    except Exception as e:
        print(f"❌ Error during WebSocket setup: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Connection setup failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }))
        await websocket.close(code=1011, reason="Setup failed")
        return
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "").strip()
            message_type = message_data.get("type", "user")
            
            if not user_message:
                continue
                
            # Handle special commands
            if user_message.lower() == "/clear":
                bot.clear_user_memory(user_id)
                response_message = {
                    "type": "system",
                    "message": "Conversation memory cleared!",
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id
                }
                await manager.send_personal_message(response_message, user_id)
                continue
            
            if user_message.lower() == "/history":
                history = bot.get_user_conversation_history(user_id)
                history_message = {
                    "type": "system",
                    "message": f"You have {len(history)} conversations in history",
                    "data": history,
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id
                }
                await manager.send_personal_message(history_message, user_id)
                continue
            
            if user_message.lower() == "/users":
                active_users = manager.get_active_users()
                users_message = {
                    "type": "system",
                    "message": f"{len(active_users)} active users",
                    "data": active_users,
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id
                }
                await manager.send_personal_message(users_message, user_id)
                continue
            
            # Echo user message
            user_echo = {
                "type": "user",
                "message": user_message,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            await manager.send_personal_message(user_echo, user_id)
            
            # Get bot response
            typing_message = {
                "type": "typing",
                "message": "Assistant is typing...",
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            await manager.send_personal_message(typing_message, user_id)
            
            # Simulate thinking time
            await asyncio.sleep(0.5)
            
            # Get response from chatbot
            response = bot.ask_question(user_message, user_id)
            
            # Send bot response
            bot_response = {
                "type": "assistant",
                "message": response["answer"],
                "confidence": response["confidence"],
                "context_count": len(response["context"]),
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            await manager.send_personal_message(bot_response, user_id)
            
            # Update user message count
            if user_id in manager.user_info:
                manager.user_info[user_id]["message_count"] += 1
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"🔌 User {user_id} disconnected")
    except Exception as e:
        print(f"❌ WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)

@router.get("/chat/users")
async def get_active_users():
    """Get list of active users"""
    return {"active_users": manager.get_active_users()}

@router.get("/chat/status")
async def get_chat_status():
    """Get chatbot and system status"""
    try:
        bot = get_chatbot()
        kb_info = bot.get_vectorstore_info()
        return {
            "status": "online",
            "knowledge_base": kb_info,
            "active_users": len(manager.active_connections),
            "chatbot_users": len(bot.memory_manager.user_sessions)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "active_users": len(manager.active_connections),
            "chatbot_users": 0
        }

@router.post("/chat/clear/{user_id}")
async def clear_user_memory(user_id: str):
    """Clear memory for a specific user"""
    try:
        bot = get_chatbot()
        bot.clear_user_memory(user_id)
        return {"message": f"Memory cleared for user {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history/{user_id}")
async def get_user_history(user_id: str):
    """Get conversation history for a user"""
    try:
        bot = get_chatbot()
        history = bot.get_user_conversation_history(user_id)
        return {"user_id": user_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
