from app.services.generation_service import generate_general_answer


def generate_adaptive_learning_step(
    topic: str,
    assessment_report: str,
    current_knowledge: str = "",
) -> str:
    if not topic.strip() or not assessment_report.strip():
        return ""

    knowledge = (
        current_knowledge.strip()
        or "The student's current knowledge is not specified."
    )

    prompt = f"""
You are the Adaptive Learning Agent for Subject Guide AI.

Determine the student's next learning step using the assessment
results and the student's current knowledge.

Topic:
{topic}

Current Student Knowledge:
{knowledge}

Assessment Report:
{assessment_report}

Follow this exact structure:

1. Assessment Status
- Summarize the demonstrated performance from the assessment report.
- Do not invent scores or knowledge that are not present.

2. Strong Areas
- List concepts that the student demonstrated correctly.

3. Weak Areas
- List concepts associated with incorrect or unanswered questions.

4. Weak Topic Routing
For every weak area:
- Identify the concept that needs review.
- Identify the relevant prerequisite or foundational concept when
  supported by the assessment information.
- Recommend targeted practice.

5. Adaptive Decision
- If the student demonstrated strong understanding, recommend
  progressing to the next learning stage.
- If the student demonstrated weak understanding, recommend reviewing
  the relevant concept and practicing it again.
- Do not invent a prerequisite that is not supported by the
  assessment or current knowledge.

6. Next Learning Step
- Give one clear immediate action.

7. Next Assessment
- Recommend what should be assessed after the student completes
  the next learning step.

STRICT RULES:
- Use only information contained in the assessment report and
  current student knowledge.
- Do not use general knowledge to invent student performance.
- Do not assume a concept is weak unless the assessment indicates it.
- Do not claim mastery unless supported by the assessment.
- Do not invent prerequisites.
- Keep the next action practical and specific.
- Return only the adaptive learning report.
- Use Markdown headings and bullets.
- Use normal ASCII hyphens (-).
"""

    return generate_general_answer(prompt)