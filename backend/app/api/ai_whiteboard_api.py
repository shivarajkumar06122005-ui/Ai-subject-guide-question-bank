from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_whiteboard_service import generate_whiteboard_content


router = APIRouter(
    prefix="/api/v1/whiteboard",
    tags=["AI Whiteboard Agent"],
)


class WhiteboardRequest(BaseModel):
    topic: str
    student_level: str = ""
    lesson_context: str = ""


class WhiteboardResponse(BaseModel):
    topic: str
    student_level: str
    lesson_context: str
    whiteboard: str


@router.post("", response_model=WhiteboardResponse)
def create_whiteboard_content(request: WhiteboardRequest):
    whiteboard = generate_whiteboard_content(
        topic=request.topic,
        student_level=request.student_level,
        lesson_context=request.lesson_context,
    )

    return WhiteboardResponse(
        topic=request.topic,
        student_level=request.student_level,
        lesson_context=request.lesson_context,
        whiteboard=whiteboard,
    )