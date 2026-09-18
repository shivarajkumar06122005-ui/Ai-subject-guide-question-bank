from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3


class QuestionResponse(BaseModel):
    question: str
    answer: str