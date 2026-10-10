from pydantic import BaseModel

from app.models.citation_model import SourceCitation


class RAGResponse(BaseModel):
    answer: str
    citations: list[SourceCitation]

