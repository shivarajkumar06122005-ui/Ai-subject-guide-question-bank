from pydantic import BaseModel

from backend.app.models.citation_model import SourceCitation


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3


class QuestionResponse(BaseModel):
    question: str
    answer: str
    citations: list[SourceCitation] = []
