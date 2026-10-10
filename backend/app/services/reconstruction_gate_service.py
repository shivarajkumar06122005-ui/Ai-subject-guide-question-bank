from dataclasses import dataclass


@dataclass
class ReconstructionGateState:
    student_id: str
    topic: str
    status: str = "UNLOCKED"
    reason: str = ""
    reconstruction_attempts: int = 0


_gate_states: dict[tuple[str, str], ReconstructionGateState] = {}


def get_gate_state(student_id: str, topic: str) -> dict:
    state = _gate_states.get((student_id, topic))

    if state is None:
        return {
            "student_id": student_id,
            "topic": topic,
            "status": "UNLOCKED",
            "reason": "",
            "reconstruction_attempts": 0,
        }

    return {
        "student_id": state.student_id,
        "topic": state.topic,
        "status": state.status,
        "reason": state.reason,
        "reconstruction_attempts": state.reconstruction_attempts,
    }


def lock_reconstruction_gate(
    student_id: str,
    topic: str,
    reason: str,
) -> dict:
    key = (student_id, topic)

    state = _gate_states.setdefault(
        key,
        ReconstructionGateState(
            student_id=student_id,
            topic=topic,
        ),
    )

    state.status = "LOCKED"
    state.reason = reason

    return get_gate_state(student_id, topic)


def record_reconstruction_attempt(
    student_id: str,
    topic: str,
    passed: bool,
) -> dict:
    key = (student_id, topic)

    state = _gate_states.setdefault(
        key,
        ReconstructionGateState(
            student_id=student_id,
            topic=topic,
        ),
    )

    state.reconstruction_attempts += 1

    if passed:
        state.status = "UNLOCKED"
        state.reason = "successful_independent_reconstruction"
    else:
        state.status = "LOCKED"
        state.reason = "reconstruction_check_failed"

    return get_gate_state(student_id, topic)


def reset_reconstruction_gate(
    student_id: str,
    topic: str,
) -> dict:
    _gate_states.pop((student_id, topic), None)

    return get_gate_state(student_id, topic)
