import os
import uuid
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
import cleanText
import splitText

load_dotenv()

def setup_knowledge_base(sample_text: str, collection_name: str = "manuals"):
    """
    Process and load documents into ChromaDB
    
    Args:
        sample_text (str): The text content to process
        collection_name (str): Name of the ChromaDB collection
    """
    print("🔄 Processing documents...")
    
    # Clean and split text
    cleaned_text = cleanText.clean_text(sample_text)
    chunks = splitText.split_text_to_chunks(cleaned_text)
    print(f"📄 Created {len(chunks)} text chunks")
    
    # Create embeddings
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    texts = [chunk.page_content for chunk in chunks]
    embeddings = embedding_model.embed_documents(texts)
    print("✅ Generated embeddings")
    
    # Setup Chroma collection
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name=collection_name)
    
    # Delete existing vectors
    all_items = collection.get(include=[])
    ids = all_items["ids"]
    if ids:
        collection.delete(ids=ids)
    print(f"🗑️  Cleared existing vectors. Current count: {collection.count()}")
    
    # Add new embeddings
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        collection.add(
            ids=[str(uuid.uuid4())],
            documents=[chunk.page_content],
            embeddings=[embedding]
        )
    
    print(f"✅ Added {collection.count()} vectors to ChromaDB")
    return collection.count()

def main():
    """Main function to feed documents to the knowledge base"""
    print("📚 Document Feeding System")
    print("=" * 50)
    
    try:
        # Get text input from user
        print("Enter your document text (press Ctrl+Z then Enter on Windows, or Ctrl+D on Unix to finish):")
        print("-" * 50)
        
        # Read multiline input
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        sample_text = '\n'.join(lines)
        
        if not sample_text.strip():
            print("❌ No text provided. Exiting...")
            return
        
        print(f"\n📄 Received {len(sample_text)} characters of text")
        
        # Setup knowledge base
        doc_count = setup_knowledge_base(sample_text, "manuals")
        
        if doc_count > 0:
            print(f"✅ Successfully added {doc_count} document chunks to knowledge base")
            print("🚀 You can now run chat.py to interact with the chatbot")
        else:
            print("❌ Failed to add documents to knowledge base")
            
    except KeyboardInterrupt:
        print("\n👋 Feeding cancelled by user")
    except Exception as e:
        print(f"❌ Error during document feeding: {e}")

if __name__ == "__main__":
    main()