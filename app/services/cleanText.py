import re
import unicodedata

def clean_text(text: str, lowercase: bool = True) -> str:
    """
    Clean raw text for chatbot knowledge ingestion.
    
    Steps:
    1. Normalize unicode (fix smart quotes, dashes, etc.)
    2. Remove URLs, emails, HTML tags
    3. Replace bullet points and dashes with normalized format
    4. Keep alphanumeric + basic punctuation (.,;:!?()-)
    5. Collapse extra spaces/newlines
    6. Optional: lowercase text (good for embeddings)
    """
    
    # Normalize unicode (convert fancy quotes/dashes to plain)
    text = unicodedata.normalize("NFKD", text)
    
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    
    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Replace bullets/dashes with a standard format
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\-–—]', ' - ', text)
    
    # Keep only words, numbers, punctuation
    text = re.sub(r'[^a-zA-Z0-9.,;:!?()\-\s]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Lowercase (optional)
    if lowercase:
        text = text.lower()
    
    return text


# Example usage
if __name__ == "__main__":
    sample = """
    📌 LangChain helps build applications with LLMs.
    Contact: support@example.com
    Visit https://www.langchain.com/docs for more info.
    - Feature 1: Retrieval Augmented Generation
    - Feature 2: Chains & Agents
    """

    print(clean_text(sample))
