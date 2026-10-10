from fastapi import APIRouter
from pydantic import BaseModel

from app.services.adaptive_learning_service import generate_adaptive_learning_step


router = APIRouter(
    prefix="/api/v1/adaptive-learning",
    tags=["Adaptive Learning Agent"],
)


class AdaptiveLearningRequest(BaseModel):
    topic: str
    assessment_report: str
    current_knowledge: str = ""


class AdaptiveLearningResponse(BaseModel):
    topic: str
    assessment_report: str
    current_knowledge: str
    adaptive_learning_report: str


@router.post("", response_model=AdaptiveLearningResponse)
def create_adaptive_learning_step(
    request: AdaptiveLearningRequest
):
    adaptive_learning_report = generate_adaptive_learning_step(
        topic=request.topic,
        assessment_report=request.assessment_report,
        current_knowledge=request.current_knowledge,
    )

    return AdaptiveLearningResponse(
        topic=request.topic,
        assessment_report=request.assessment_report,
        current_knowledge=request.current_knowledge,
        adaptive_learning_report=adaptive_learning_report,
    )
