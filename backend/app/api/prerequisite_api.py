from fastapi import APIRouter
from pydantic import BaseModel

from app.services.prerequisite_service import generate_prerequisites


router = APIRouter(
    prefix="/api/v1/prerequisite",
    tags=["Prerequisite Agent"],
)


class PrerequisiteRequest(BaseModel):
    goal: str
    current_knowledge: str = ""


class PrerequisiteResponse(BaseModel):
    goal: str
    current_knowledge: str
    prerequisites: str


@router.post("", response_model=PrerequisiteResponse)
def create_prerequisite_analysis(request: PrerequisiteRequest):
    prerequisites = generate_prerequisites(
        goal=request.goal,
        current_knowledge=request.current_knowledge,
    )

    return PrerequisiteResponse(
        goal=request.goal,
        current_knowledge=request.current_knowledge,
        prerequisites=prerequisites,
    )
