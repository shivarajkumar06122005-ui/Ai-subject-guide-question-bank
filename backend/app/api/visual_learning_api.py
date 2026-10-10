from fastapi import APIRouter
from pydantic import BaseModel

from app.services.visual_learning_service import generate_visual_learning_response


router = APIRouter(
    prefix="/api/v1/visual-learning",
    tags=["Visual Learning Agent"],
)


class VisualLearningRequest(BaseModel):
    topic: str
    student_level: str = ""
    learning_goal: str = ""


class VisualLearningResponse(BaseModel):
    topic: str
    student_level: str
    learning_goal: str
    visual_learning: str


@router.post("", response_model=VisualLearningResponse)
def create_visual_learning_response(request: VisualLearningRequest):
    visual_learning = generate_visual_learning_response(
        topic=request.topic,
        student_level=request.student_level,
        learning_goal=request.learning_goal,
    )

    return VisualLearningResponse(
        topic=request.topic,
        student_level=request.student_level,
        learning_goal=request.learning_goal,
        visual_learning=visual_learning,
    )