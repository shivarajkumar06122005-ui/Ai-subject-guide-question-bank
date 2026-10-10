from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_teacher_service import generate_teacher_response


router = APIRouter(
    prefix="/api/v1/teacher",
    tags=["AI Teacher Agent"],
)


class TeacherRequest(BaseModel):
    question: str
    lesson_context: str = ""
    student_level: str = ""


class TeacherResponse(BaseModel):
    question: str
    lesson_context: str
    student_level: str
    answer: str


@router.post("", response_model=TeacherResponse)
def create_teacher_response(request: TeacherRequest):
    answer = generate_teacher_response(
        question=request.question,
        lesson_context=request.lesson_context,
        student_level=request.student_level,
    )

    return TeacherResponse(
        question=request.question,
        lesson_context=request.lesson_context,
        student_level=request.student_level,
        answer=answer,
    )