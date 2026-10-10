from app.services.independent_answer_service import evaluate_independent_answer
from app.services.reconstruction_gate_service import (
    get_gate_state,
    lock_reconstruction_gate,
    record_reconstruction_attempt,
)


def start_reconstruction_gate(
    student_id: str,
    topic: str,
    reason: str = "metacognitive_reconstruction_required",
) -> dict:
    """
    F2.9: Start a reconstruction gate.

    The gate becomes LOCKED when the system determines that the
    student must independently reconstruct the concept before
    continuing.
    """
    return lock_reconstruction_gate(
        student_id=student_id,
        topic=topic,
        reason=reason,
    )


def evaluate_reconstruction_gate(
    student_id: str,
    topic: str,
    original_problem: str,
    student_response: str,
) -> dict:
    """
    F2.9: Evaluate an independent reconstruction and update
    the gate lifecycle.

    PASS  -> UNLOCKED
    FAIL  -> remains LOCKED
    """

    evaluation = evaluate_independent_answer(
        original_problem=original_problem,
        student_response=student_response,
    )

    gate_state = record_reconstruction_attempt(
        student_id=student_id,
        topic=topic,
        passed=evaluation["passed"],
    )

    return {
        "student_id": student_id,
        "topic": topic,
        "gate_status": gate_state["status"],
        "gate_reason": gate_state["reason"],
        "reconstruction_attempts": gate_state["reconstruction_attempts"],
        "evaluation": evaluation,
        "can_continue": gate_state["status"] == "UNLOCKED",
    }


def get_reconstruction_gate(
    student_id: str,
    topic: str,
) -> dict:
    """
    F2.9: Return the current lifecycle state of the gate.
    """
    state = get_gate_state(
        student_id=student_id,
        topic=topic,
    )

    return {
        **state,
        "can_continue": state["status"] == "UNLOCKED",
    }
