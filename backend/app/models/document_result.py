from dataclasses import dataclass

from backend.app.models.chunk_model import DocumentChunk


@dataclass
class DocumentResult:
    source: str
    total_chunks: int
    chunks: list[DocumentChunk]