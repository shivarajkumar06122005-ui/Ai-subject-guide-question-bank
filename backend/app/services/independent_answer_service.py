from app.services.verified_reasoning_service import verify_reasoning


def _extract_solution_set(verification_result: dict) -> list:
    """
    Extract the final verified solution set from F1 evidence.
    """
    verified_steps = verification_result.get("verified_steps", [])

    if not verified_steps:
        return []

    # Prefer the last verified step because it represents
    # the student's final mathematical state.
    for step in reversed(verified_steps):
        solutions = step.get("solutions")
        if solutions is not None:
            return sorted(
                [str(solution) for solution in solutions]
            )

    return []


def evaluate_independent_answer(
    original_problem: str,
    student_response: str,
) -> dict:
    """
    F2.7: Evaluate an independent student answer against
    the original problem using F1 deterministic verification.

    The student's answer is not judged in isolation.
    It must produce the same solution set as the original problem.
    """

    original = original_problem.strip()
    response = student_response.strip()

    if not original:
        return {
            "status": "failed",
            "passed": False,
            "confidence": 0.0,
            "reason": "missing_original_problem",
            "evidence": {
                "type": "insufficient_context",
                "summary": "The original problem is required.",
            },
        }

    if not response:
        return {
            "status": "failed",
            "passed": False,
            "confidence": 1.0,
            "reason": "empty_response",
            "evidence": {
                "type": "no_independent_response",
                "summary": (
                    "No independent answer was submitted."
                ),
            },
        }

    original_result = verify_reasoning(original)
    student_result = verify_reasoning(response)

    if original_result.get("status") != "verified":
        return {
            "status": "failed",
            "passed": False,
            "confidence": original_result.get("confidence", 0.0),
            "reason": "original_problem_not_verifiable",
            "evidence": {
                "type": "original_problem_verification",
                "summary": (
                    "The original problem could not be deterministically "
                    "verified by the reasoning verifier."
                ),
                "original_evidence": original_result.get("evidence", {}),
            },
        }

    if student_result.get("status") != "verified":
        return {
            "status": "failed",
            "passed": False,
            "confidence": student_result.get("confidence", 0.0),
            "reason": "independent_reasoning_not_verified",
            "evidence": {
                "type": "independent_reasoning_verification",
                "summary": (
                    "The independent response contains reasoning "
                    "that could not be deterministically verified."
                ),
                "student_evidence": student_result.get("evidence", {}),
            },
            "verified_steps": student_result.get("verified_steps", []),
            "failed_steps": student_result.get("failed_steps", []),
        }

    original_solutions = _extract_solution_set(original_result)
    student_solutions = _extract_solution_set(student_result)

    if not original_solutions:
        return {
            "status": "failed",
            "passed": False,
            "confidence": 0.70,
            "reason": "original_solution_not_extracted",
            "evidence": {
                "type": "solution_extraction",
                "summary": (
                    "The original problem was verified, but its "
                    "solution set could not be extracted."
                ),
            },
        }

    if not student_solutions:
        return {
            "status": "failed",
            "passed": False,
            "reason": "student_solution_not_extracted",
            "confidence": 0.90,
            "evidence": {
                "type": "solution_extraction",
                "summary": (
                    "The independent response was verified, but "
                    "its final solution set could not be extracted."
                ),
            },
        }

    passed = original_solutions == student_solutions

    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "confidence": 1.0,
        "reason": (
            "solution_set_matches_original"
            if passed
            else "solution_set_does_not_match_original"
        ),
        "evidence": {
            "type": "independent_answer_comparison",
            "level": "high",
            "summary": (
                "The independent answer produces the same solution set "
                "as the original problem."
                if passed
                else "The independent answer produces a different "
                     "solution set from the original problem."
            ),
            "original_solutions": original_solutions,
            "student_solutions": student_solutions,
        },
        "verified_steps": student_result.get("verified_steps", []),
        "failed_steps": student_result.get("failed_steps", []),
    }
