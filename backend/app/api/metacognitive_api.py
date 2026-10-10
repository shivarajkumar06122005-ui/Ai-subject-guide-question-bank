from fastapi import APIRouter
from pydantic import BaseModel

from app.models.active_recall_model import (
    ActiveRecallRequest,
    ActiveRecallResponse,
)
from app.models.metacognitive_model import MetacognitiveEvent
from app.services.metacognitive_service import detect_miscalibration
from app.services.hint_dependency_service import (
    get_hint_dependency_state,
    track_hint_dependency,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Metacognitive Learning Control"],
)


@router.post(
    "/active-recall",
    response_model=ActiveRecallResponse,
)
def submit_active_recall(
    request: ActiveRecallRequest,
):
    submitted = bool(request.student_response.strip())

    message = (
        "Independent reconstruction submitted."
        if submitted
        else "Independent reconstruction is required before continuing."
    )

    return ActiveRecallResponse(
        student_id=request.student_id,
        topic=request.topic,
        prompt=request.prompt,
        student_response=request.student_response,
        independent_response_submitted=submitted,
        gate_status=request.gate_status,
        message=message,
    )


@router.post("/metacognitive/evaluate")
def evaluate_metacognitive_event(
    event: MetacognitiveEvent,
):
    return detect_miscalibration(event)


class HintDependencyRequest(BaseModel):
    student_id: str
    topic: str
    used_hint: bool
    independent_check_passed: bool


@router.post("/metacognitive/hint-dependency")
def record_hint_dependency(
    request: HintDependencyRequest,
):
    return track_hint_dependency(
        student_id=request.student_id,
        topic=request.topic,
        used_hint=request.used_hint,
        independent_check_passed=request.independent_check_passed,
    )


@router.get("/metacognitive/hint-dependency/{student_id}/{topic}")
def read_hint_dependency(
    student_id: str,
    topic: str,
):
    return get_hint_dependency_state(
        student_id=student_id,
        topic=topic,
    )
