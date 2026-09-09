from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.app.models.chunk_model import DocumentChunk


def get_file_extension(file_path: str) -> str:
    return Path(file_path).suffix.lower()


def is_pdf(file_path: str) -> bool:
    return get_file_extension(file_path) == ".pdf"


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


def split_text_into_chunks(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    return splitter.split_text(text)

def process_pdf(file_path: str) -> list[DocumentChunk]:
    text = extract_text_from_pdf(file_path)

    if not text:
        return []

    source = Path(file_path).name

    return create_document_chunks(text, source)

def create_document_chunks(text: str, source: str) -> list[DocumentChunk]:
    chunks = split_text_into_chunks(text)

    return [
        DocumentChunk(
            text=chunk,
            source=source,
            chunk_index=index
        )
        for index, chunk in enumerate(chunks)
    ]