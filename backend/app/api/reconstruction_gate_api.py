from fastapi import APIRouter
from pydantic import BaseModel

from app.services.reconstruction_lifecycle_service import (
    start_reconstruction_gate,
    evaluate_reconstruction_gate,
    get_reconstruction_gate,
)
from app.services.socratic_engine_service import generate_socratic_hint


router = APIRouter(
    prefix="/api/v1/reconstruction-gate",
    tags=["Metacognitive Reconstruction Gate"],
)


class ReconstructionGateStartRequest(BaseModel):
    student_id: str
    topic: str
    reason: str = "metacognitive_reconstruction_required"


class ReconstructionGateEvaluateRequest(BaseModel):
    student_id: str
    topic: str
    original_problem: str
    student_response: str


@router.post("/start")
def start_gate(request: ReconstructionGateStartRequest):
    return start_reconstruction_gate(
        student_id=request.student_id,
        topic=request.topic,
        reason=request.reason,
    )


@router.post("/evaluate")
def evaluate_gate(request: ReconstructionGateEvaluateRequest):
    lifecycle = evaluate_reconstruction_gate(
        student_id=request.student_id,
        topic=request.topic,
        original_problem=request.original_problem,
        student_response=request.student_response,
    )

    socratic = generate_socratic_hint(
        original_problem=request.original_problem,
        student_response=request.student_response,
    )

    return {
        **lifecycle,
        "socratic": socratic,
    }


@router.get("/{student_id}/{topic}")
def get_gate(student_id: str, topic: str):
    return get_reconstruction_gate(
        student_id=student_id,
        topic=topic,
    )
