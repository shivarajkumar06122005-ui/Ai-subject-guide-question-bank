from pydantic import BaseModel
from typing import List, Optional

class StudentProfile(BaseModel):
    full_name: str
    email: str
    academic_level: str
    department: str

class QuizSubmission(BaseModel):
    user_id: str
    unit_id: str
    answers: List[str]

class TokenReward(BaseModel):
    user_id: str
    tokens_earned: int
