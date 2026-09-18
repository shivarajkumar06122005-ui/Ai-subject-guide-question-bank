from pydantic import BaseModel


class SourceCitation(BaseModel):
    source: str
    page_number: int | None = None
    chunk_index: int
