from dataclasses import dataclass, field


CONSECUTIVE_HINT_THRESHOLD = 3


@dataclass
class HintDependencyState:
    student_id: str
    topic: str
    consecutive_hint_attempts: int = 0
    independent_successes: int = 0
    total_attempts: int = 0
    hint_dependency_alert: bool = False
    history: list[dict] = field(default_factory=list)


_tracker: dict[tuple[str, str], HintDependencyState] = {}


def track_hint_dependency(
    student_id: str,
    topic: str,
    used_hint: bool,
    independent_check_passed: bool,
) -> dict:
    key = (student_id, topic)

    state = _tracker.setdefault(
        key,
        HintDependencyState(
            student_id=student_id,
            topic=topic,
        ),
    )

    state.total_attempts += 1

    if independent_check_passed:
        state.independent_successes += 1
        state.consecutive_hint_attempts = 0
    elif used_hint:
        state.consecutive_hint_attempts += 1
    else:
        state.consecutive_hint_attempts = 0

    state.hint_dependency_alert = (
        state.consecutive_hint_attempts >= CONSECUTIVE_HINT_THRESHOLD
    )

    event = {
        "attempt": state.total_attempts,
        "used_hint": used_hint,
        "independent_check_passed": independent_check_passed,
        "consecutive_hint_attempts": state.consecutive_hint_attempts,
        "hint_dependency_alert": state.hint_dependency_alert,
    }

    state.history.append(event)

    return {
        "student_id": state.student_id,
        "topic": state.topic,
        "consecutive_hint_attempts": state.consecutive_hint_attempts,
        "independent_successes": state.independent_successes,
        "total_attempts": state.total_attempts,
        "hint_dependency_alert": state.hint_dependency_alert,
        "history": state.history,
    }


def get_hint_dependency_state(
    student_id: str,
    topic: str,
) -> dict:
    state = _tracker.get((student_id, topic))

    if state is None:
        return {
            "student_id": student_id,
            "topic": topic,
            "consecutive_hint_attempts": 0,
            "independent_successes": 0,
            "total_attempts": 0,
            "hint_dependency_alert": False,
            "history": [],
        }

    return {
        "student_id": state.student_id,
        "topic": state.topic,
        "consecutive_hint_attempts": state.consecutive_hint_attempts,
        "independent_successes": state.independent_successes,
        "total_attempts": state.total_attempts,
        "hint_dependency_alert": state.hint_dependency_alert,
        "history": state.history,
    }


def reset_hint_dependency_state(
    student_id: str,
    topic: str,
) -> None:
    _tracker.pop((student_id, topic), None)
