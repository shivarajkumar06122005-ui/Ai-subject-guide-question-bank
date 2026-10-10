from fastapi import APIRouter
from pydantic import BaseModel

from app.services.visual_content_service import generate_visual_content


router = APIRouter(
    prefix="/api/v1/visual-content",
    tags=["Visual Content Agent"],
)


class VisualContentRequest(BaseModel):
    topic: str
    visual_learning_spec: str = ""
    student_level: str = ""


class VisualContentResponse(BaseModel):
    topic: str
    visual_learning_spec: str
    student_level: str
    visual_content: str


@router.post("", response_model=VisualContentResponse)
def create_visual_content(request: VisualContentRequest):
    visual_content = generate_visual_content(
        topic=request.topic,
        visual_learning_spec=request.visual_learning_spec,
        student_level=request.student_level,
    )

    return VisualContentResponse(
        topic=request.topic,
        visual_learning_spec=request.visual_learning_spec,
        student_level=request.student_level,
        visual_content=visual_content,
    )