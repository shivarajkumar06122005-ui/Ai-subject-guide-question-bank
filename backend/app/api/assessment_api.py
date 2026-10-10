from fastapi import APIRouter
from pydantic import BaseModel

from app.services.assessment_service import generate_assessment


router = APIRouter(
    prefix="/api/v1/assessment",
    tags=["Assessment Agent"],
)


class AssessmentRequest(BaseModel):
    topic: str
    question_bank: str
    student_answers: str = ""
    study_text: str = ""


class AssessmentResponse(BaseModel):
    topic: str
    question_bank: str
    student_answers: str
    study_text: str
    assessment_report: str


@router.post("", response_model=AssessmentResponse)
def create_assessment(
    request: AssessmentRequest
):
    assessment_report = generate_assessment(
        topic=request.topic,
        question_bank=request.question_bank,
        student_answers=request.student_answers,
        study_text=request.study_text,
    )

    return AssessmentResponse(
        topic=request.topic,
        question_bank=request.question_bank,
        student_answers=request.student_answers,
        study_text=request.study_text,
        assessment_report=assessment_report,
    )