from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase import Client

from app.security.supabase_auth import get_current_user, get_user_supabase
from app.services.student_profile_service import get_student_profile
from app.services.synthetic_peer_service import generate_synthetic_peers
from app.services.synthetic_peer_service import continue_synthetic_peer_discussion
from app.services.synthetic_peer_service import detect_peer_misconception
from app.services.synthetic_peer_service import analyze_peer_confidence
from app.services.synthetic_peer_service import analyze_peer_agreement
from app.services.synthetic_peer_service import run_peer_debate
from app.services.synthetic_peer_service import summarize_peer_classroom


router = APIRouter(
    prefix="/api/v1/synthetic-peer",
    tags=["Synthetic Peer Classroom"],
)


class SyntheticPeerRequest(BaseModel):
    topic: str
    student_prompt: str = ""
    study_context: str


class SyntheticPeerResponse(BaseModel):
    status: str
    topic: str
    student_prompt: str
    peer_roles: list[str] = []
    classroom_discussion: str = ""
    reason: str | None = None


@router.post("", response_model=SyntheticPeerResponse)
def create_synthetic_peer_classroom(
    request: SyntheticPeerRequest,
    current_user: dict[str, str] = Depends(get_current_user),
    db: Client = Depends(get_user_supabase),
):
    profile = get_student_profile(db, current_user["id"])
    prior_memory = (
        profile.learning_memory
        if profile is not None and isinstance(profile.learning_memory, dict)
        else {}
    )

    result = generate_synthetic_peers(
        topic=request.topic,
        student_prompt=request.student_prompt,
        study_context=request.study_context,
        prior_learning_memory=prior_memory,
    )

    return SyntheticPeerResponse(
        status=result["status"],
        topic=result.get("topic", request.topic),
        student_prompt=result.get(
            "student_prompt",
            request.student_prompt,
        ),
        peer_roles=result.get("peer_roles", []),
        classroom_discussion=result.get(
            "classroom_discussion",
            "",
        ),
        reason=result.get("reason"),
    )
class SyntheticPeerFollowupRequest(BaseModel):
    topic: str
    student_response: str
    study_context: str
    initial_discussion: str = ""


class SyntheticPeerFollowupResponse(BaseModel):
    status: str
    topic: str
    student_response: str
    peer_roles: list[str] = []
    followup_discussion: str = ""
    reason: str | None = None


@router.post("/followup", response_model=SyntheticPeerFollowupResponse)
def continue_synthetic_peer_classroom(
    request: SyntheticPeerFollowupRequest,
):
    result = continue_synthetic_peer_discussion(
        topic=request.topic,
        student_response=request.student_response,
        study_context=request.study_context,
        initial_discussion=request.initial_discussion,
    )

    return SyntheticPeerFollowupResponse(
        status=result["status"],
        topic=result.get("topic", request.topic),
        student_response=result.get(
            "student_response",
            request.student_response,
        ),
        peer_roles=result.get("peer_roles", []),
        followup_discussion=result.get(
            "followup_discussion",
            "",
        ),
        reason=result.get("reason"),
    )
class SyntheticPeerMisconceptionRequest(BaseModel):
    topic: str
    student_response: str
    study_context: str


class SyntheticPeerMisconceptionResponse(BaseModel):
    status: str
    topic: str
    student_response: str
    misconception_analysis: str = ""
    reason: str | None = None


@router.post(
    "/misconception",
    response_model=SyntheticPeerMisconceptionResponse,
)
def analyze_synthetic_peer_misconception(
    request: SyntheticPeerMisconceptionRequest,
):
    result = detect_peer_misconception(
        topic=request.topic,
        student_response=request.student_response,
        study_context=request.study_context,
    )

    return SyntheticPeerMisconceptionResponse(
        status=result["status"],
        topic=result.get("topic", request.topic),
        student_response=result.get(
            "student_response",
            request.student_response,
        ),
        misconception_analysis=result.get(
            "misconception_analysis",
            "",
        ),
        reason=result.get("reason"),
    )
class SyntheticPeerConfidenceRequest(BaseModel):
    topic: str
    student_response: str
    confidence_score: int
    misconception_analysis: str


class SyntheticPeerConfidenceResponse(BaseModel):
    status: str
    topic: str
    student_response: str
    confidence_score: int
    understanding_status: str = ""
    calibration: str = ""
    interpretation: str = ""
    reason: str | None = None


@router.post(
    "/confidence",
    response_model=SyntheticPeerConfidenceResponse,
)
def analyze_synthetic_peer_confidence(
    request: SyntheticPeerConfidenceRequest,
):
    result = analyze_peer_confidence(
        topic=request.topic,
        student_response=request.student_response,
        confidence_score=request.confidence_score,
        misconception_analysis=request.misconception_analysis,
    )

    return SyntheticPeerConfidenceResponse(
        status=result["status"],
        topic=result.get("topic", request.topic),
        student_response=result.get(
            "student_response",
            request.student_response,
        ),
        confidence_score=result.get(
            "confidence_score",
            request.confidence_score,
        ),
        understanding_status=result.get(
            "understanding_status",
            "",
        ),
        calibration=result.get(
            "calibration",
            "",
        ),
        interpretation=result.get(
            "interpretation",
            "",
        ),
        reason=result.get("reason"),
    )

class SyntheticPeerAgreementRequest(BaseModel):
    topic: str
    peer_discussion: str
    study_context: str


class SyntheticPeerAgreementResponse(BaseModel):
    status: str
    topic: str
    peer_agreement: str = ""
    reason: str | None = None


@router.post(
    "/agreement",
    response_model=SyntheticPeerAgreementResponse,
)
def analyze_synthetic_peer_agreement(
    request: SyntheticPeerAgreementRequest,
):
    result = analyze_peer_agreement(
        topic=request.topic,
        peer_discussion=request.peer_discussion,
        study_context=request.study_context,
    )

    return SyntheticPeerAgreementResponse(
        status=result["status"],
        topic=result.get("topic", request.topic),
        peer_agreement=result.get(
            "peer_agreement",
            "",
        ),
        reason=result.get("reason"),
    )


class SyntheticPeerDebateRequest(BaseModel):
    topic: str
    revised_claim: str
    study_context: str
    peer_discussion: str = ""


class SyntheticPeerDebateResponse(BaseModel):
    status: str
    topic: str
    revised_claim: str = ""
    debate_result: str = ""
    reason: str | None = None


@router.post(
    "/debate",
    response_model=SyntheticPeerDebateResponse,
)
def analyze_synthetic_peer_debate(
    request: SyntheticPeerDebateRequest,
):
    result = run_peer_debate(
        topic=request.topic,
        revised_claim=request.revised_claim,
        study_context=request.study_context,
        peer_discussion=request.peer_discussion,
    )

    return SyntheticPeerDebateResponse(
        status=result["status"],
        topic=result.get("topic", request.topic),
        revised_claim=result.get(
            "revised_claim",
            request.revised_claim,
        ),
        debate_result=result.get(
            "debate_result",
            "",
        ),
        reason=result.get("reason"),
    )


class SyntheticPeerSummaryRequest(BaseModel):
    topic: str
    study_context: str
    initial_student_response: str
    misconception_analysis: str = ""
    confidence_analysis: str = ""
    agreement_analysis: str = ""
    revised_claim: str = ""
    debate_result: str = ""


class SyntheticPeerSummaryResponse(BaseModel):
    status: str
    topic: str
    learning_summary: str = ""
    reason: str | None = None


@router.post(
    "/summary",
    response_model=SyntheticPeerSummaryResponse,
)
def summarize_synthetic_peer_classroom(
    request: SyntheticPeerSummaryRequest,
):
    result = summarize_peer_classroom(
        topic=request.topic,
        study_context=request.study_context,
        initial_student_response=request.initial_student_response,
        misconception_analysis=request.misconception_analysis,
        confidence_analysis=request.confidence_analysis,
        agreement_analysis=request.agreement_analysis,
        revised_claim=request.revised_claim,
        debate_result=request.debate_result,
    )

    return SyntheticPeerSummaryResponse(
        status=result["status"],
        topic=result.get("topic", request.topic),
        learning_summary=result.get(
            "learning_summary",
            "",
        ),
        reason=result.get("reason"),
    )

