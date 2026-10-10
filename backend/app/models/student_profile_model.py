from pydantic import BaseModel, Field
from typing import List


class StudentProfile(BaseModel):
    student_id: str
    name: str = ""
    current_level: int = 1
    current_topic: str = ""
    completed_topics: List[str] = Field(default_factory=list)
    weak_topics: List[str] = Field(default_factory=list)
    strong_topics: List[str] = Field(default_factory=list)
    xp: int = 0
    streak_days: int = 0
    learning_state: str = "NOT_STARTED"
    learning_memory: dict = Field(default_factory=dict)


