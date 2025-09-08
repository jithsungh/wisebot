#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.chatbot import AdaptiveKnowledgeChatbot

print("Testing chatbot initialization...")
try:
    bot = AdaptiveKnowledgeChatbot('manuals')
    print("✅ Chatbot created successfully")
    info = bot.get_vectorstore_info()
    print(f"✅ Vectorstore info: {info}")
    
    # Test a simple query
    result = bot.ask_question("Hello", "test_user")
    print(f"✅ Test query result: {result['success']}")
    print("✅ All components working")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
