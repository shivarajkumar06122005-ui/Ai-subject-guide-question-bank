from pydantic import BaseModel, Field


class ActiveRecallRequest(BaseModel):
    student_id: str
    topic: str
    prompt: str
    student_response: str = ""
    expected_concept: str = ""
    gate_status: str = "LOCKED"


class ActiveRecallResponse(BaseModel):
    student_id: str
    topic: str
    prompt: str
    student_response: str
    independent_response_submitted: bool
    gate_status: str
    message: str
