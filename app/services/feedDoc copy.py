from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
import uuid
from splitText import semantic_split_text


def setup_knowledge_base(text: str, collection_name: str = "manuals"):
    """
    Clean, split, embed, and load documents into ChromaDB
    """
    print("🔄 Processing documents...")

    # Clean + semantic split
    chunks = semantic_split_text(text)
    print(f"📄 Created {len(chunks)} semantic text chunks")

    # Embeddings
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    texts = [chunk.page_content for chunk in chunks]
    embeddings = embedding_model.embed_documents(texts)
    print("✅ Generated embeddings")

    # Setup Chroma collection
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name=collection_name)

    # Batch insert (faster & scalable)
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

    # # Delete existing vectors
    # all_items = collection.get(include=[])
    # ids = all_items["ids"]
    # if ids:
    #     collection.delete(ids=ids)
    # print(f"🗑️  Cleared existing vectors. Current count: {collection.count()}")

    # Add new embeddings

def main():
    """Main function to feed documents to the knowledge base"""
    try:
        # Lazy imports for CLI and environment
        import argparse
        import os
        from dotenv import load_dotenv
        import extractText

        load_dotenv()

        parser = argparse.ArgumentParser(
            description="Extract text from a PDF or DOCX document and feed it into the knowledge base."
        )
        parser.add_argument(
            "-s", "--source", required=True, help="Path to the document file (PDF or DOCX)"
        )
        parser.add_argument(
            "-c", "--collection", default="manuals", help="ChromaDB collection name (default: manuals)"
        )
        args = parser.parse_args()

        print("📚 Document Feeding System")
        print("=" * 50)

        if not os.path.exists(args.source):
            print(f"❌ File not found: {args.source}")
            return

        print(f"📥 Reading from: {args.source}")
        text = extractText.extract_text(args.source)

        if not text.strip():
            print("❌ No text extracted. Exiting...")
            return

        print(f"\n📄 Received {len(text)} characters of text")

        # Setup knowledge base
        doc_count = setup_knowledge_base(text, args.collection)

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