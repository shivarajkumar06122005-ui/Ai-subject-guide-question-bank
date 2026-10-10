from app.services.independent_answer_service import evaluate_independent_answer


def generate_socratic_hint(
    original_problem: str,
    student_response: str,
) -> dict:
    """
    F2.8: Adaptive Socratic Engine.

    Evaluates the independent response using F2.7 and generates
    a targeted Socratic prompt without revealing the final answer.
    """

    evaluation = evaluate_independent_answer(
        original_problem=original_problem,
        student_response=student_response,
    )

    if evaluation["passed"]:
        return {
            "status": "passed",
            "hint_type": "unlock",
            "hint": (
                "Good reconstruction. Explain in your own words why "
                "your answer follows from the original problem."
            ),
            "reveals_answer": False,
            "evaluation": evaluation,
        }

    evidence = evaluation.get("evidence", {})
    evidence_type = evidence.get("type", "")
    reason = evaluation.get("reason", "")

    if reason == "empty_response":
        hint = (
            "Start from the original problem. What operation would "
            "you apply first, and why?"
        )
        hint_type = "active_recall_start"

    elif reason == "solution_set_does_not_match_original":
        original_solutions = evidence.get("original_solutions", [])
        student_solutions = evidence.get("student_solutions", [])

        hint = (
            "Your answer leads to a different solution than the "
            "original problem. Go back to the original equation and "
            "check each operation you performed. Which operation "
            "changed the value incorrectly?"
        )

        # Deliberately do not expose either solution set.
        # F2 must make the student reconstruct the answer.
        hint_type = "solution_mismatch"

    elif reason == "independent_reasoning_not_verified":
        failed_steps = evaluation.get("failed_steps", [])

        if failed_steps:
            first_failure = failed_steps[0]
            previous_step = first_failure.get("previous_step")
            expected_right = first_failure.get("expected_right")
            left_change = first_failure.get("left_change")
            right_change = first_failure.get("right_change")

            if (
                previous_step
                and left_change is not None
                and right_change is not None
            ):
                hint = (
                    "Look at the step where your reasoning changed. "
                    f"Compare it with the previous step ({previous_step}). "
                    f"The left side changed by {left_change}, while your "
                    f"right side changed by {right_change}. "
                    "What operation should be applied consistently "
                    "to both sides?"
                )
                hint_type = "transition_reconstruction"

            elif expected_right is not None:
                hint = (
                    "Your transformation changed the solution set. "
                    "Look at the previous step and ask: if the same "
                    "operation is applied to both sides, what must "
                    "remain equivalent?"
                )
                hint_type = "operation_reconstruction"

            else:
                hint = (
                    "Identify the first step where your reasoning "
                    "stops being justified. What rule or operation "
                    "did you use at that step?"
                )
                hint_type = "first_failure_reconstruction"
        else:
            hint = (
                "Reconstruct your reasoning one step at a time. "
                "For each step, ask whether the operation preserves "
                "the original problem."
            )
            hint_type = "reasoning_reconstruction"

    else:
        hint = (
            "Try the problem again without using the previous answer. "
            "Write the first step and explain why that step is valid."
        )
        hint_type = "guided_reconstruction"

    return {
        "status": "needs_reconstruction",
        "hint_type": hint_type,
        "hint": hint,
        "reveals_answer": False,
        "evaluation": evaluation,
    }
