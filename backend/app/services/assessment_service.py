from app.services.generation_service import generate_grounded_content


def generate_assessment(
    topic: str,
    question_bank: str,
    student_answers: str = "",
    study_text: str = "",
) -> str:
    if not topic.strip() or not question_bank.strip():
        return ""

    context = study_text.strip() or question_bank.strip()

    instruction = f"""
You are the Assessment Agent for Subject Guide AI.

Your job is to evaluate a student's answers against the provided
question bank and generate a grounded assessment report.

Topic:
{topic}

Question Bank:
{question_bank}

Student Answers:
{student_answers if student_answers.strip() else "Student answers were not provided."}

Study Material / Grounding Context:
{context}

If student answers are provided, evaluate each answer.

For each question provide:

1. Question number
2. Correct answer
3. Student answer
4. Result: Correct / Incorrect / Not Answered
5. Short explanation

Then provide:

6. Assessment Summary
- Total questions
- Correct answers
- Incorrect answers
- Not answered
- Score where it can be determined

7. Topic Understanding
- Identify concepts the student demonstrated correctly.

8. Weak Topics
- Identify concepts associated with incorrect or missing answers.

9. Improvement Guidance
- Give study guidance based only on the identified weak topics
  and the supplied study material.

10. Next Learning Step
- Suggest what the student should review next based on the
  assessment results.

STRICT GROUNDING RULES:
- Use ONLY the supplied question bank and study material.
- Do not use general knowledge to determine answers.
- Do not invent facts, answers, concepts, or explanations.
- Do not assume an unanswered question is correct.
- Do not infer knowledge that is not demonstrated by the student's answers.
- If student answers are not provided, do not pretend an assessment
  has been completed. Instead explain that answers are required.
- Score only questions for which correctness can be determined.
- Do not claim that the student understands a topic unless supported
  by their submitted answers.
- Weak topics must be based on actual incorrect or unanswered questions.
- Return only the assessment report.
"""

    return generate_grounded_content(
        instruction=instruction,
        context=context
    )