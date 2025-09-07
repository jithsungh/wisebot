from chatbot import AdaptiveKnowledgeChatbot

def main():
    """Main function to run the chatbot interface"""
    print("🤖 Initializing Adaptive Knowledge Chatbot...")
    
    try:
        # Initialize chatbot
        chatbot = AdaptiveKnowledgeChatbot(collection_name="manuals")
        
        # Display vectorstore info
        info = chatbot.get_vectorstore_info()
        if info:
            print(f"📚 Loaded {info['document_count']} documents from vectorstore")
            if info['document_count'] == 0:
                print("⚠️  No documents in knowledge base. Run feed.py first to add documents.")
                return
        
        print("\n💬 Chatbot ready! Type 'exit' or 'quit' to stop, 'clear' to clear memory.\n")
        
        # Chat loop
        while True:
            try:
                query = input("You: ").strip()
                
                if query.lower() in ["exit", "quit", "bye"]:
                    print("👋 Goodbye!")
                    break
                
                if query.lower() == "clear":
                    chatbot.clear_memory()
                    continue
                
                if not query:
                    print("Please enter a question.")
                    continue
                
                # Get response
                response = chatbot.ask_question(query)
                
                if response["success"]:
                    answer = response['answer']
                    print(f"Assistant: {answer}")
                    
                    # If answer is "I don't know" or low confidence, show context
                    if ("I don't know" in answer.lower() or 
                        "i don't know" in answer.lower() or 
                        response["confidence"] < 0.5):
                        
                        if response["context"]:
                            print(f"\n📄 Retrieved context:")
                            for i, context in enumerate(response["context"][:3], 1):
                                print(f"{i}. {context[:200]}{'...' if len(context) > 200 else ''}")
                        else:
                            print("📄 No relevant context found in knowledge base.")
                        
                        if response["confidence"] < 0.5:
                            print(f"⚠️  Low confidence ({response['confidence']:.1f})")
                else:
                    print(f"Assistant: {response['answer']}")
                    
                print()  # Empty line for readability
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        print("Make sure you have:")
        print("1. GROQ_API_KEY in your .env file")
        print("2. ChromaDB with documents (run feed.py first)")
        print("3. All required packages installed")

if __name__ == "__main__":
    main()