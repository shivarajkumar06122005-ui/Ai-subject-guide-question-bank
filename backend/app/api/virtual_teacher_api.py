from fastapi import APIRouter
from pydantic import BaseModel

from app.services.virtual_teacher_service import (
    generate_virtual_teacher_session
)


router = APIRouter(
    prefix="/api/v1/virtual-teacher",
    tags=["Virtual Teacher Agent"],
)


class VirtualTeacherRequest(BaseModel):
    topic: str
    student_level: str = ""
    learning_goal: str = ""
    lesson_context: str = ""
    study_text: str = ""
    student_answer: str = ""
    check_question: str = ""


class VirtualTeacherResponse(BaseModel):
    topic: str
    student_level: str
    learning_goal: str
    lesson_context: str
    study_text: str
    student_answer: str
    check_question: str
    teacher_script: str
    assessment_report: str
    adaptive_learning_report: str
    next_action: str


@router.post("", response_model=VirtualTeacherResponse)
def create_virtual_teacher_session(
    request: VirtualTeacherRequest
):
    result = generate_virtual_teacher_session(
        topic=request.topic,
        student_level=request.student_level,
        learning_goal=request.learning_goal,
        lesson_context=request.lesson_context,
        study_text=request.study_text,
        student_answer=request.student_answer,
        check_question=request.check_question,
    )

    return VirtualTeacherResponse(
        topic=request.topic,
        student_level=request.student_level,
        learning_goal=request.learning_goal,
        lesson_context=request.lesson_context,
        study_text=request.study_text,
        student_answer=request.student_answer,
        check_question=result["check_question"],
        teacher_script=result["teacher_script"],
        assessment_report=result["assessment_report"],
        adaptive_learning_report=result["adaptive_learning_report"],
        next_action=result["next_action"],
    )
