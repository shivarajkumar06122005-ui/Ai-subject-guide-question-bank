from app.models.metacognitive_model import MetacognitiveEvent


CALIBRATION_THRESHOLD = 0.20
HINT_DEPENDENCY_THRESHOLD = 3


def calculate_calibration(event: MetacognitiveEvent) -> dict:
    calibration_gap = (
        event.jol - event.independent_performance
    )

    if calibration_gap > CALIBRATION_THRESHOLD:
        status = "overconfident"
    elif calibration_gap < -CALIBRATION_THRESHOLD:
        status = "underconfident"
    else:
        status = "well_calibrated"

    return {
        "student_id": event.student_id,
        "topic": event.topic,
        "jol": event.jol,
        "independent_performance": event.independent_performance,
        "calibration_gap": round(calibration_gap, 4),
        "status": status,
        "hint_count": event.hint_count,
        "answer_time_seconds": event.answer_time_seconds,
        "unassisted": event.unassisted,
    }


def detect_miscalibration(event: MetacognitiveEvent) -> dict:
    calibration = calculate_calibration(event)

    calibration_gap = abs(calibration["calibration_gap"])

    calibration_alert = calibration_gap > CALIBRATION_THRESHOLD

    hint_dependency = (
        event.hint_count >= HINT_DEPENDENCY_THRESHOLD
    )

    miscalibration_alert = (
        calibration_alert or hint_dependency
    )

    reasons = []

    if calibration_alert:
        reasons.append("calibration_gap")

    if hint_dependency:
        reasons.append("high_hint_usage")

    return {
        **calibration,
        "calibration_alert": calibration_alert,
        "hint_dependency": hint_dependency,
        "miscalibration_alert": miscalibration_alert,
        "alert_reasons": reasons,
    }
