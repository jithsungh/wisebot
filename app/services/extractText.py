def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    import PyPDF2  # lazy import

    text = []
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    from docx import Document  # lazy import

    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text(file_path: str) -> str:
    """Extract text from a file (PDF or DOCX)."""
    import os  # lazy import

    # convert all \ to /
    file_path = file_path.replace("\\", "/")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")


if __name__ == "__main__":
    # Example usage
    test_file = "./files/TRI.pdf"  # change to your file path
    print(extract_text(test_file))