from backend.app.models.document_result import DocumentResult
from backend.app.services.document_service import process_pdf


def load_document(file_path: str) -> DocumentResult:
    return process_pdf(file_path)
