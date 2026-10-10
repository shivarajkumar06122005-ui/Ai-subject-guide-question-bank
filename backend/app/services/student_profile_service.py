from supabase import Client

from app.models.student_profile_model import StudentProfile


def create_student_profile(
    db: Client,
    student_id: str,
    name: str = "",
) -> StudentProfile:
    profile = StudentProfile(
        student_id=student_id,
        name=name,
    )

    db.table("student_profiles").insert(profile.model_dump()).execute()
    return profile


def get_student_profile(
    db: Client,
    student_id: str,
) -> StudentProfile | None:
    response = (
        db.table("student_profiles")
        .select("*")
        .eq("student_id", student_id)
        .execute()
    )

    if not response.data:
        return None

    data = response.data[0]

    return StudentProfile(
        student_id=data["student_id"],
        name=data.get("name", ""),
        current_level=data.get("current_level", 1),
        current_topic=data.get("current_topic", ""),
        completed_topics=data.get("completed_topics", []),
        weak_topics=data.get("weak_topics", []),
        strong_topics=data.get("strong_topics", []),
        xp=data.get("xp", 0),
        streak_days=data.get("streak_days", 0),
        learning_state=data.get("learning_state", "NOT_STARTED"),
        learning_memory=data.get("learning_memory", {}),
    )


def update_student_profile(
    db: Client,
    student_id: str,
    **updates,
) -> StudentProfile | None:
    profile = get_student_profile(db, student_id)

    if profile is None:
        return None

    updated_data = profile.model_dump()
    updated_data.update(updates)
    updated_profile = StudentProfile(**updated_data)

    (
        db.table("student_profiles")
        .update(updated_profile.model_dump())
        .eq("student_id", student_id)
        .execute()
    )

    return updated_profile
