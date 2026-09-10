from dataclasses import dataclass


@dataclass
class DocumentChunk:
    text: str
    source: str
    chunk_index: int
    page_number: int | None = None