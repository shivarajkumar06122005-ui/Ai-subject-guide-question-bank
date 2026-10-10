from fastapi import APIRouter
from pydantic import BaseModel

from app.services.question_bank_service import generate_question_bank


router = APIRouter(
    prefix="/api/v1/question-bank",
    tags=["Question Bank Agent"],
)


class QuestionBankRequest(BaseModel):
    topic: str
    question_count: int = 5
    difficulty: str = "mixed"
    question_type: str = "mixed"
    study_text: str = ""


class QuestionBankResponse(BaseModel):
    topic: str
    question_count: int
    difficulty: str
    question_type: str
    study_text: str
    question_bank: str


@router.post("", response_model=QuestionBankResponse)
def create_question_bank(
    request: QuestionBankRequest
):
    question_bank = generate_question_bank(
        topic=request.topic,
        question_count=request.question_count,
        difficulty=request.difficulty,
        question_type=request.question_type,
        study_text=request.study_text,
    )

    return QuestionBankResponse(
        topic=request.topic,
        question_count=request.question_count,
        difficulty=request.difficulty,
        question_type=request.question_type,
        study_text=request.study_text,
        question_bank=question_bank,
    )