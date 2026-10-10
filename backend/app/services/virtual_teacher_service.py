from pathlib import Path
import re

from app.services.ai_teacher_service import generate_teacher_response
from app.services.assessment_service import generate_assessment
from app.services.adaptive_learning_service import generate_adaptive_learning_step
from app.services.document_service import process_pdf
from app.services.generation_service import generate_general_answer
from app.services.retrieval_service import (
    retrieve_relevant_chunks,
    cosine_similarity,
)
from app.services.embedding_service import create_embedding


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"


def _get_learning_context(
    topic: str,
    study_text: str = "",
) -> str:
    if study_text.strip():
        return study_text.strip()

    pdf_files = sorted(UPLOAD_DIR.glob("*.pdf"))

    if not pdf_files:
        return ""

    pdf_path = max(
        pdf_files,
        key=lambda path: path.stat().st_mtime
    )

    document = process_pdf(str(pdf_path))

    if not document.chunks:
        return ""

    relevant_chunks = retrieve_relevant_chunks(
        topic,
        document.chunks,
        top_k=5,
    )

    if not relevant_chunks:
        return ""

    topic_embedding = create_embedding(topic)

    relevant_chunks = [
        chunk
        for chunk in relevant_chunks
        if cosine_similarity(
            topic_embedding,
            create_embedding(chunk.text)
        ) >= 0.55
    ]

    if not relevant_chunks:
        return ""

    return "\n\n".join(
        chunk.text
        for chunk in relevant_chunks
    )


def _extract_check_question(text: str) -> str:
    if not text:
        return ""

    match = re.search(
        r"(?is)Check Your Understanding\s*:?\s*(.*?)(?:\n\s*##|\Z)",
        text,
    )

    if not match:
        return ""

    section = match.group(1).strip()

    for line in section.splitlines():
        cleaned = line.strip().lstrip("-*").strip()

        if "?" in cleaned:
            return cleaned

    return ""


def _extract_next_action(adaptive_report: str) -> str:
    if not adaptive_report:
        return ""

    match = re.search(
        r"(?is)6\.\s*Next Learning Step\s*(.*?)(?:\n\s*7\.|\Z)",
        adaptive_report,
    )

    if not match:
        return adaptive_report.strip()

    section = match.group(1).strip()

    lines = [
        line.strip().lstrip("-*").strip()
        for line in section.splitlines()
        if line.strip()
    ]

    return " ".join(lines)


def _generate_general_assessment(
    topic: str,
    question: str,
    student_answer: str,
) -> str:

    prompt = f"""
You are evaluating a student's answer as part of an AI Virtual Teacher.

Topic:
{topic}

Check Your Understanding Question:
{question}

Student Answer:
{student_answer}

Use established general knowledge to determine whether the student's
answer is correct.

Return this exact structure:

1. Question
2. Correct Answer
3. Student Answer
4. Result: Correct / Incorrect / Incomplete
5. Short Explanation

6. Assessment Summary
- Result
- Brief understanding summary

7. Weak Topics
- Identify the concept that needs review only when the answer is
  incorrect or incomplete.

8. Improvement Guidance
- Give one practical learning suggestion.

9. Next Learning Step
- Give one clear immediate action.

STRICT RULES:
- Do not invent facts.
- Do not claim the answer came from uploaded study material.
- Judge the answer using established general knowledge.
- Keep the assessment concise.
- Return only the assessment report.
"""

    return generate_general_answer(prompt)


def _generate_general_feedback(
    topic: str,
    student_level: str,
    question: str,
    student_answer: str,
    assessment_report: str,
    adaptive_report: str,
) -> str:

    prompt = f"""
You are the Virtual Teacher giving feedback after a student answered
a Check Your Understanding question.

Topic:
{topic}

Student Level:
{student_level}

Question:
{question}

Student Answer:
{student_answer}

Assessment Report:
{assessment_report}

Adaptive Learning Report:
{adaptive_report}

Give conversational teacher feedback.

Rules:
- Use established general knowledge.
- Clearly say whether the answer was correct, incorrect, or incomplete.
- Explain the concept briefly.
- Follow the adaptive learning recommendation.
- Tell the student what to do next.
- Stay appropriate for the student's level.
- Do not claim that the explanation came from uploaded study material.
- Return only the teacher feedback.
"""

    return generate_general_answer(prompt)


def generate_virtual_teacher_session(
    topic: str,
    student_level: str = "",
    learning_goal: str = "",
    lesson_context: str = "",
    study_text: str = "",
    student_answer: str = "",
    check_question: str = "",
) -> dict:

    if not topic.strip():
        return {
            "teacher_script": "",
            "check_question": "",
            "assessment_report": "",
            "adaptive_learning_report": "",
            "next_action": "",
        }

    context = _get_learning_context(
        topic=topic,
        study_text=study_text,
    )

    # True means the uploaded material is relevant to the topic.
    grounded_mode = bool(context.strip())

    level = (
        student_level.strip()
        or "Student level not specified."
    )

    goal = (
        learning_goal.strip()
        or "Understand the topic clearly."
    )

    # ---------------------------------------------------------
    # FIRST TURN: TEACH THE LESSON
    # ---------------------------------------------------------
    if not student_answer.strip():

        if grounded_mode:

            combined_context = (
                f"Learning Goal:\n{goal}\n\n"
                f"Additional Lesson Context:\n"
                f"{lesson_context.strip() or 'None'}\n\n"
                f"Study Material:\n"
                f"{context}"
            )

            teacher_response = generate_teacher_response(
                question=(
                    "Teach this topic as my Virtual Teacher. "
                    "Start with a natural introduction, explain the "
                    "concept step by step, adapt the explanation to "
                    "the student's level, use the supplied lesson "
                    "context, and finish with exactly one short "
                    "Check Your Understanding question."
                    f"\n\nTopic:\n{topic}"
                ),
                lesson_context=combined_context,
                student_level=level,
            )

        else:

            teacher_response = generate_teacher_response(
                question=(
                    "Teach this topic as my Virtual Teacher using "
                    "established general knowledge. "
                    "Start with a natural introduction, explain "
                    "the concept step by step, adapt the explanation "
                    "to the student's level, and finish with exactly "
                    "one short Check Your Understanding question."
                    f"\n\nTopic:\n{topic}\n"
                    f"\nLearning Goal:\n{goal}"
                    f"\n\nAdditional Context:\n"
                    f"{lesson_context.strip() or 'None'}"
                ),
                lesson_context="",
                student_level=level,
            )

        extracted_question = (
            check_question.strip()
            or _extract_check_question(teacher_response)
        )

        teacher_script = f"""
# VIRTUAL TEACHER SESSION

## Topic
{topic}

## Student Level
{level}

## Learning Goal
{goal}

## Teaching Mode
{"Grounded Study Material" if grounded_mode else "General Knowledge"}

## Teacher Lesson
{teacher_response}

## Virtual Teacher Delivery Notes
- Tone: Friendly, calm, student-focused
- Speaking pace: Moderate
- Use short pauses after important concepts
- Emphasize key terms
- Ask the student to answer the Check Your Understanding question
- Wait for the student's response before continuing the lesson
""".strip()

        return {
            "teacher_script": teacher_script,
            "check_question": extracted_question,
            "assessment_report": "",
            "adaptive_learning_report": "",
            "next_action": "WAIT_FOR_STUDENT_ANSWER",
        }

    # ---------------------------------------------------------
    # SECOND TURN: ASSESS STUDENT ANSWER
    # ---------------------------------------------------------
    question_for_assessment = check_question.strip()

    if not question_for_assessment:
        return {
            "teacher_script": (
                "I received your answer, but I need the "
                "Check Your Understanding question to evaluate it."
            ),
            "check_question": "",
            "assessment_report": "",
            "adaptive_learning_report": "",
            "next_action": "QUESTION_REQUIRED",
        }

    if grounded_mode:

        assessment_report = generate_assessment(
            topic=topic,
            question_bank=question_for_assessment,
            student_answers=student_answer,
            study_text=context,
        )

    else:

        assessment_report = _generate_general_assessment(
            topic=topic,
            question=question_for_assessment,
            student_answer=student_answer,
        )

    adaptive_learning_report = ""

    if assessment_report.strip():
        adaptive_learning_report = generate_adaptive_learning_step(
            topic=topic,
            assessment_report=assessment_report,
            current_knowledge=level,
        )

    next_action = _extract_next_action(
        adaptive_learning_report
    )

    # ---------------------------------------------------------
    # TEACHER FEEDBACK
    # ---------------------------------------------------------
    if grounded_mode:

        feedback_context = f"""
Learning Goal:
{goal}

Study Material:
{context}

Assessment Report:
{assessment_report}

Adaptive Learning Report:
{adaptive_learning_report}

Student Answer:
{student_answer}

Check Question:
{question_for_assessment}
"""

        teacher_feedback = generate_teacher_response(
            question="""
The student has just answered a Check Your Understanding question.

Give teacher feedback on the student's answer.

Rules:
- Use only the supplied study material and assessment information.
- Explain whether the answer is correct, incorrect, incomplete,
  or not answerable.
- If incorrect or incomplete, explain the missing concept clearly.
- Follow the adaptive learning recommendation.
- Tell the student exactly what to do next.
- Keep it conversational.
- Do not invent facts.

Return only the teacher feedback.
""",
            lesson_context=feedback_context,
            student_level=level,
        )

    else:

        teacher_feedback = _generate_general_feedback(
            topic=topic,
            student_level=level,
            question=question_for_assessment,
            student_answer=student_answer,
            assessment_report=assessment_report,
            adaptive_report=adaptive_learning_report,
        )

    return {
        "teacher_script": teacher_feedback,
        "check_question": question_for_assessment,
        "assessment_report": assessment_report,
        "adaptive_learning_report": adaptive_learning_report,
        "next_action": next_action,
    }