import os
import uuid
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
import cleanText

from splitText import semantic_split_text

load_dotenv()

def setup_knowledge_base(sample_text: str, collection_name: str = "manuals"):
    """
    Process, embed, and load documents into ChromaDB.
    """
    print("🔄 Processing documents...")

    # Clean and semantic split
    cleaned_text = cleanText.clean_text(sample_text)
    chunks = semantic_split_text(cleaned_text)
    print(f"📄 Created {len(chunks)} semantic text chunks")

    # Create embeddings
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    texts = [chunk.page_content for chunk in chunks]
    embeddings = embedding_model.embed_documents(texts)
    print("✅ Generated embeddings")

    # Setup Chroma collection
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name=collection_name)

    # Batch insert (fast & scalable)
    ids = [str(uuid.uuid4()) for _ in chunks]
    documents = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(f"✅ Added {collection.count()} vectors to ChromaDB")
    return collection.count()


def main():
    """Main function to feed documents into the knowledge base"""
    print("📚 Document Feeding System")
    print("=" * 50)

    try:
        # Get text input from user
        print("Enter your document text (Ctrl+Z + Enter on Windows, or Ctrl+D on Unix to finish):")
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