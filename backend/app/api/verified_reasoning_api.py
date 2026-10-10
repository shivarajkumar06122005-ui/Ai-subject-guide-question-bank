from fastapi import APIRouter
from pydantic import BaseModel

from app.services.verified_reasoning_service import verify_reasoning


router = APIRouter(
    prefix="/api/v1/verified-reasoning",
    tags=["Verified AI Reasoning"],
)


class VerifiedReasoningRequest(BaseModel):
    reasoning: str


class VerificationEvidence(BaseModel):
    type: str
    level: str
    summary: str

class VerifiedReasoningResponse(BaseModel):
    domain: str
    status: str
    confidence: float
    evidence: VerificationEvidence
    verified_steps: list[dict]
    failed_steps: list[dict]
    hint: str


@router.post("", response_model=VerifiedReasoningResponse)
def verify_student_reasoning(
    request: VerifiedReasoningRequest,
):
    return verify_reasoning(request.reasoning)


