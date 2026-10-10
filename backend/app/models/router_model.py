from typing import Any

from pydantic import BaseModel, Field


ROUTER_INTENTS = {
    "study",
    "practice",
    "quiz",
    "exam",
    "revision",
    "challenge",
    "mock_test",
    "interview",
    "planner",
    "flashcard",
    "pyq_analysis",
    "image_question",
    "voice",
    "teacher",
    "reteach",
    "next_step",
    "document_question",
    "general",
}


class RouterParameters(BaseModel):
    subject: str | None = None
    topic: str | None = None
    marks: int | None = Field(default=None, ge=1, le=100)
    difficulty: str | None = None
    question_count: int | None = Field(default=None, ge=1, le=1000)
    time_limit: str | None = None
    language: str | None = None
    requested_mode: str | None = None
    document_related: bool = False
    image_related: bool = False
    voice_related: bool = False


class RouterResult(BaseModel):
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    route: str
    parameters: RouterParameters = Field(default_factory=RouterParameters)


class RouterRequest(BaseModel):
    message: str = Field(min_length=1)
    image_related: bool = False
    voice_related: bool = False
    document_related: bool = False
