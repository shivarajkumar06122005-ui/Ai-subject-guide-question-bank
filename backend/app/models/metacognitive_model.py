from pydantic import BaseModel, Field


class MetacognitiveEvent(BaseModel):
    student_id: str
    topic: str

    # Judgment of Learning: student's self-reported confidence.
    jol: float = Field(ge=0.0, le=1.0)

    # Independent performance without AI assistance.
    independent_performance: float = Field(ge=0.0, le=1.0)

    # Optional behavioral signals.
    hint_count: int = Field(default=0, ge=0)
    answer_time_seconds: float = Field(default=0.0, ge=0.0)

    # Whether this event was completed without AI assistance.
    unassisted: bool = True
