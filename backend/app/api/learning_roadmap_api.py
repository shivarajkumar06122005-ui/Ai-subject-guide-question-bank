from fastapi import APIRouter
from pydantic import BaseModel

from app.services.learning_roadmap_service import generate_learning_roadmap


router = APIRouter(
    prefix="/api/v1/roadmap",
    tags=["Learning Roadmap"],
)


class RoadmapRequest(BaseModel):
    goal: str
    current_knowledge: str = ""


class RoadmapResponse(BaseModel):
    goal: str
    current_knowledge: str
    roadmap: str


@router.post("", response_model=RoadmapResponse)
def create_learning_roadmap(request: RoadmapRequest):
    roadmap = generate_learning_roadmap(
        goal=request.goal,
        current_knowledge=request.current_knowledge,
    )

    return RoadmapResponse(
        goal=request.goal,
        current_knowledge=request.current_knowledge,
        roadmap=roadmap,
    )
