from app.services.generation_service import generate_general_answer


def generate_prerequisites(
    goal: str,
    current_knowledge: str = "",
) -> str:
    if not goal.strip():
        return ""

    knowledge = (
        current_knowledge.strip()
        or "The student's current knowledge is not specified."
    )

    prompt = f"""
You are the Prerequisite Agent for Subject Guide AI.

Your job is to analyze what a student needs to know BEFORE learning their target goal.

Student Goal:
{goal}

Current Student Knowledge:
{knowledge}

Analyze the prerequisites using this exact structure:

1. Target Goal
- State the student's target clearly.

2. Required Prerequisites
- List the concepts, skills, or topics required before the target.
- Arrange them from foundational to advanced.

3. Why Each Prerequisite Is Needed
- Explain briefly why each prerequisite is required for the target.

4. Already Known
- Identify prerequisites that the student already knows based ONLY on the provided current knowledge.
- Do not assume knowledge that was not provided.

5. Knowledge Gaps
- Identify prerequisites that appear to be missing from the provided knowledge.
- Do not invent missing information.

6. Recommended Starting Point
- Identify the prerequisite/topic the student should start with based on the available information.

7. Prerequisite Sequence
- Show the dependency order clearly.
- Use this format:
  Foundation → Prerequisite → Intermediate → Target

Important rules:
- Do not assume the student knows something unless it is provided.
- Do not treat advanced topics as prerequisites for foundational topics.
- Keep prerequisite relationships logically ordered.
- Be practical and student-friendly.
- Return only the prerequisite analysis.
- Use Markdown headings and bullets.
- Use normal ASCII hyphens (-).
"""

    return generate_general_answer(prompt)