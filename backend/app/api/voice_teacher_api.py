from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.voice_teacher_service import (
    generate_voice_teacher_script,
    generate_teacher_audio,
)


router = APIRouter(
    prefix="/api/v1/voice-teacher",
    tags=["Voice Teacher Agent"],
)


AUDIO_DIR = Path(__file__).resolve().parents[2] / "generated_audio"


class VoiceTeacherRequest(BaseModel):
    topic: str
    student_level: str = ""
    learning_goal: str = ""
    lesson_context: str = ""
    study_text: str = ""


class VoiceTeacherResponse(BaseModel):
    topic: str
    student_level: str
    learning_goal: str
    lesson_context: str
    study_text: str
    voice_script: str
    audio_file: str


@router.post("", response_model=VoiceTeacherResponse)
def create_voice_teacher_script(
    request: VoiceTeacherRequest
):
    voice_script = generate_voice_teacher_script(
        topic=request.topic,
        student_level=request.student_level,
        learning_goal=request.learning_goal,
        lesson_context=request.lesson_context,
        study_text=request.study_text,
    )

    audio_file = ""

    if voice_script.strip():
        audio_filename = "voice_teacher.wav"

        generate_teacher_audio(
            transcript=voice_script,
            filename=audio_filename,
        )

        audio_file = (
            f"/api/v1/voice-teacher/audio/{audio_filename}"
        )

    return VoiceTeacherResponse(
        topic=request.topic,
        student_level=request.student_level,
        learning_goal=request.learning_goal,
        lesson_context=request.lesson_context,
        study_text=request.study_text,
        voice_script=voice_script,
        audio_file=audio_file,
    )


@router.get("/audio/{filename}")
def get_voice_teacher_audio(filename: str):
    audio_path = AUDIO_DIR / filename

    if not audio_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Audio file not found."
        )

    return FileResponse(
        path=str(audio_path),
        media_type="audio/wav",
        filename=filename,
    )