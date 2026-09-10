from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.app.models.chunk_model import DocumentChunk
from backend.app.models.document_result import DocumentResult


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


def extract_pages_from_pdf(file_path: str) -> list[str]:
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            pages.append(page_text.strip())
        else:
            pages.append("")

    return pages


def split_text_into_chunks(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    return splitter.split_text(text)


def create_document_chunks(
    text: str,
    source: str,
    page_number: int | None = None
) -> list[DocumentChunk]:
    chunks = split_text_into_chunks(text)

    return [
        DocumentChunk(
            text=chunk,
            source=source,
            chunk_index=index,
            page_number=page_number
        )
        for index, chunk in enumerate(chunks)
    ]


def process_pdf(file_path: str) -> DocumentResult:
    source = Path(file_path).name
    pages = extract_pages_from_pdf(file_path)

    document_chunks = []
    chunk_index = 0

    for page_number, page_text in enumerate(pages, start=1):
        if not page_text:
            continue

        page_chunks = split_text_into_chunks(page_text)

        for chunk in page_chunks:
            document_chunks.append(
                DocumentChunk(
                    text=chunk,
                    source=source,
                    chunk_index=chunk_index,
                    page_number=page_number
                )
            )

            chunk_index += 1

    return DocumentResult(
        source=source,
        total_chunks=len(document_chunks),
        chunks=document_chunks
    )