from fastapi import APIRouter
from pydantic import BaseModel

from app.services.study_guide_service import generate_study_guide


router = APIRouter(
    prefix="/api/v1/study-guide",
    tags=["Study Guide Agent"],
)


class StudyGuideRequest(BaseModel):
    topic: str
    context: str


class StudyGuideResponse(BaseModel):
    topic: str
    context: str
    study_guide: str


@router.post("", response_model=StudyGuideResponse)
def create_study_guide(
    request: StudyGuideRequest,
):
    study_guide = generate_study_guide(
        topic=request.topic,
        context=request.context,
    )

    return StudyGuideResponse(
        topic=request.topic,
        context=request.context,
        study_guide=study_guide,
    )