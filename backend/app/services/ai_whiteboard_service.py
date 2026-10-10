from app.services.generation_service import generate_general_answer


def generate_whiteboard_content(
    topic: str,
    student_level: str = "",
    lesson_context: str = "",
) -> str:
    if not topic.strip():
        return ""

    level = student_level.strip() or "Student level not specified."
    context = lesson_context.strip() or "No lesson context provided."

    prompt = f"""
You are the AI Whiteboard Agent for Subject Guide AI.

Your job is to create a structured digital whiteboard plan that a teacher
or frontend whiteboard component can use to explain a topic.

Topic:
{topic}

Student Level:
{level}

Lesson Context:
{context}

Create the whiteboard content using this exact structure:

1. Board Title
- Give the whiteboard a clear title.

2. Learning Objective
- State what the student should understand after the explanation.

3. Main Concept
- Explain the central concept briefly.

4. Whiteboard Sections
Create logical sections from left to right or top to bottom.
For each section provide:
- Section title
- Key points
- Important terms
- Example or explanation

5. Step-by-Step Flow
- Show the logical sequence of the concept using arrows where useful.

6. Important Formula or Rule
- Include formulas, rules, or definitions only when relevant to the topic.

7. Worked Example
- Give one simple example and explain it step by step.

8. Final Summary
- Provide the key points that should remain on the whiteboard.

9. Board Layout
- Describe where each section should be positioned.

Important rules:
- Adapt the explanation to the student's level.
- Use the lesson context when it is relevant.
- Do not claim that an actual whiteboard image has been generated.
- Keep the content suitable for later frontend rendering.
- Keep the structure clear and logically ordered.
- Return only the whiteboard content.
- Use Markdown headings and bullets.
- Use normal ASCII hyphens (-).
"""

    return generate_general_answer(prompt)