from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.models.learning_state_model import LearningStateUpdate
from app.security.supabase_auth import get_current_user, get_user_supabase
from app.services.student_profile_service import (
    create_student_profile,
    get_student_profile,
    update_student_profile,
)

router = APIRouter(
    prefix="/api/v1/students",
    tags=["students"],
)


def verify_profile_owner(student_id: str, current_user: dict[str, str]) -> None:
    if student_id != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own student profile.",
        )


@router.post("/{student_id}/profile")
def create_profile(
    student_id: str,
    name: str = "",
    current_user: dict[str, str] = Depends(get_current_user),
    db: Client = Depends(get_user_supabase),
):
    verify_profile_owner(student_id, current_user)

    existing_profile = get_student_profile(db, student_id)
    if existing_profile is not None:
        return existing_profile

    return create_student_profile(db, student_id, name)


@router.get("/{student_id}/profile")
def get_profile(
    student_id: str,
    current_user: dict[str, str] = Depends(get_current_user),
    db: Client = Depends(get_user_supabase),
):
    verify_profile_owner(student_id, current_user)

    profile = get_student_profile(db, student_id)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found.",
        )

    return profile


@router.patch("/{student_id}/profile")
def update_profile(
    student_id: str,
    updates: LearningStateUpdate,
    current_user: dict[str, str] = Depends(get_current_user),
    db: Client = Depends(get_user_supabase),
):
    verify_profile_owner(student_id, current_user)

    profile = update_student_profile(
        db,
        student_id,
        **updates.model_dump(exclude_none=True),
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found.",
        )

    return profile
