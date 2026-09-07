from pathlib import Path
from pypdf import PdfReader


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