from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.voice_teacher_service import generate_teacher_audio
from app.services.teaching_video_service import (
    generate_teaching_video_plan,
    extract_teacher_narration,
    create_teaching_video,
)


router = APIRouter(
    prefix="/api/v1/teaching-video",
    tags=["Teaching Video Agent"],
)


class TeachingVideoRequest(BaseModel):
    topic: str
    student_level: str = ""
    lesson_context: str = ""
    learning_goal: str = ""
    study_text: str = ""


class TeachingVideoResponse(BaseModel):
    topic: str
    student_level: str
    lesson_context: str
    learning_goal: str
    study_text: str
    video_plan: str
    teacher_narration: str
    audio_file: str
    video_file: str


@router.post("", response_model=TeachingVideoResponse)
def create_teaching_video_plan(request: TeachingVideoRequest):

    # ---------------------------------------------------------
    # 1. Generate teaching-video plan
    # ---------------------------------------------------------
    video_plan = generate_teaching_video_plan(
        topic=request.topic,
        student_level=request.student_level,
        lesson_context=request.lesson_context,
        learning_goal=request.learning_goal,
        study_text=request.study_text,
    )

    # ---------------------------------------------------------
    # 2. Extract teacher narration
    # ---------------------------------------------------------
    teacher_narration = extract_teacher_narration(video_plan)

    audio_file = ""
    video_file = ""

    if not teacher_narration.strip():
        return TeachingVideoResponse(
            topic=request.topic,
            student_level=request.student_level,
            lesson_context=request.lesson_context,
            learning_goal=request.learning_goal,
            study_text=request.study_text,
            video_plan=video_plan,
            teacher_narration="",
            audio_file="",
            video_file="",
        )

    # ---------------------------------------------------------
    # 3. Create safe audio filename
    # ---------------------------------------------------------
    safe_topic = "".join(
        char if char.isalnum() else "_"
        for char in request.topic.lower()
    ).strip("_")

    audio_filename = f"teaching_video_voice_{safe_topic}.wav"

    # Expected audio location
    audio_path = (
        Path(__file__).resolve().parents[2]
        / "generated_audio"
        / audio_filename
    )

    # ---------------------------------------------------------
    # 4. Generate Gemini AI teacher voice
    # ---------------------------------------------------------
    try:
        generated_audio_path = generate_teacher_audio(
            teacher_narration,
            filename=audio_filename,
        )

        # Diagnostic output
        print("========================================")
        print("GENERATED AUDIO PATH:")
        print(generated_audio_path)
        print("========================================")

        if generated_audio_path:
            audio_path = Path(generated_audio_path)

    except Exception as exc:
        print(f"Teaching Video voice generation failed: {exc}")
        generated_audio_path = None

    # ---------------------------------------------------------
    # 5. Verify generated audio
    # ---------------------------------------------------------
    if audio_path.exists():

        audio_file = (
            f"/api/v1/voice-teacher/audio/{audio_path.name}"
        )

        # -----------------------------------------------------
        # 6. Create actual MP4 teaching video
        # -----------------------------------------------------
        try:
            video_path = create_teaching_video(
                narration_audio_path=str(audio_path),
                output_filename="teaching_video.mp4",
                topic=request.topic,
                video_plan=video_plan,
            )

            if video_path:

                video_path = Path(video_path)

                if video_path.exists():
                    video_file = (
                        "/api/v1/teaching-video/video/"
                        f"{video_path.name}"
                    )

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Teaching Video creation failed: {exc}",
            )

    else:
        raise HTTPException(
            status_code=500,
            detail=(
                "Teaching Video audio file was not created: "
                f"{audio_path}"
            ),
        )

    # ---------------------------------------------------------
    # 7. Return generated plan + audio + video
    # ---------------------------------------------------------
    return TeachingVideoResponse(
        topic=request.topic,
        student_level=request.student_level,
        lesson_context=request.lesson_context,
        learning_goal=request.learning_goal,
        study_text=request.study_text,
        video_plan=video_plan,
        teacher_narration=teacher_narration,
        audio_file=audio_file,
        video_file=video_file,
    )


# -------------------------------------------------------------
# Serve generated teaching videos
# -------------------------------------------------------------
@router.get("/video/{filename}")
def get_teaching_video(filename: str):

    backend_dir = Path(__file__).resolve().parents[2]

    # Normal generated videos
    video_path = (
        backend_dir
        / "generated_videos"
        / filename
    )

    # Existing Binary Search demo video
    if filename == "binary_search_2d_full.mp4":
        video_path = (
            backend_dir
            / "binary_search_2d_full.mp4"
        )

    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Teaching video not found.",
        )

    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
    )
