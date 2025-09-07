from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Suppose you already cleaned text from PDF/Word
def split_text_to_chunks(cleaned_text: str) -> list[Document]:
    # Wrap into a LangChain Document
    docs = [Document(page_content=cleaned_text, metadata={"source": "knowledge_base"})]

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n", ".", "?", "!"]  # smart splitting
    )
    chunks = splitter.split_documents(docs)
    # print(f"Total chunks: {len(chunks)}")
    # print(chunks[0].page_content)

    return chunks


# Example usage
if __name__ == "__main__":
    cleaned_text = """
    langchain helps build applications with llms. 
    retrieval augmented generation improves accuracy by fetching context. 
    groq runs llama models very fast for enterprise use cases.
    """
    print(split_text_to_chunks(cleaned_text))

