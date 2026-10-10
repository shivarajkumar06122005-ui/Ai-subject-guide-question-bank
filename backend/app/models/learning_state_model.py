from pydantic import BaseModel


class LearningStateUpdate(BaseModel):
    current_level: int | None = None
    current_topic: str | None = None
    completed_topics: list[str] | None = None
    weak_topics: list[str] | None = None
    strong_topics: list[str] | None = None
    xp: int | None = None
    streak_days: int | None = None
    learning_state: str | None = None
    learning_memory: dict | None = None

