from app.services.generation_service import (
    generate_answer,
    generate_general_answer,
)


def generate_teacher_response(
    question: str,
    lesson_context: str = "",
    student_level: str = "",
) -> str:
    if not question.strip():
        return ""

    level = (
        student_level.strip()
        or "Student level not specified."
    )

    # ---------------------------------------------------------
    # GROUNDED MODE
    # ---------------------------------------------------------
    # When study/lesson context is available, use the grounded
    # generation path so the teacher cannot invent unsupported facts.
    if lesson_context.strip():
        grounded_question = f"""
You are teaching a student at the following level:

Student Level:
{level}

Teaching Requirements:
- Explain the student's question clearly.
- Break difficult concepts into smaller steps.
- Use only information supported by the provided study material.
- Do not add outside facts or unsupported examples.
- Adapt the explanation to the student's level.
- End with a short Check Your Understanding question.
- If the material does not contain enough information, say:
"I could not find this information in the provided study material."

Student Question:
{question}
"""

        return generate_answer(
            question=grounded_question,
            context=lesson_context,
        )

    # ---------------------------------------------------------
    # GENERAL MODE
    # ---------------------------------------------------------
    # Preserve the existing behavior when no study material is
    # available.
    prompt = f"""
You are the AI Teacher Agent for Subject Guide AI.

Your job is to teach the student clearly and adapt the explanation
to the student's level.

Student Level:
{level}

Student Question:
{question}

Teaching requirements:

1. Understand the student's question.
2. Explain the concept clearly and accurately.
3. Adapt the explanation to the student's stated level.
4. Break difficult concepts into smaller steps.
5. Use a simple example when it helps understanding.
6. End with a short "Check Your Understanding" question.

Return only the teacher response.

Use Markdown headings and bullets where useful.
Use normal ASCII hyphens (-).
"""

    return generate_general_answer(prompt)
