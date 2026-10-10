from app.services.generation_service import generate_general_answer


def generate_learning_roadmap(
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
You are the Learning Roadmap Agent for Subject Guide AI.

Create a structured, adaptive learning roadmap for the student's goal.

Student Goal:
{goal}

Current Student Knowledge:
{knowledge}

The roadmap MUST follow this exact structure:

1. Goal
- Clearly define the target learning outcome.

2. Current Knowledge Analysis
- Analyze what the student already knows from the provided current knowledge.
- Identify what can be skipped or treated as already understood.
- Do not claim the student knows anything that was not provided.

3. Prerequisite Analysis
- Identify the concepts required before the target topics.
- Explain why each prerequisite is needed.

4. Dependency Graph
- Show the learning dependencies explicitly.
- Use a simple format such as:
  Topic A → Topic B → Topic C
- Make prerequisite relationships clear.

5. Learning Sequence
- Arrange topics from foundational to advanced.
- Follow the dependency relationships.
- Explain what should be learned at each stage.

6. Practice Plan
- Give practical exercises after each major learning stage.
- Include progressively harder practice.
- Include coding/problem-solving practice when appropriate.

7. Assessment
- Define how the student should test understanding.
- Include quizzes, exercises, projects, or other suitable assessments.
- Explain what performance indicates sufficient understanding.

8. Weak-Topic Detection
- Explain how weak areas can be identified from assessment performance.
- Give concrete examples of weak-topic signals.

9. Adaptive Next Step
- Explain what the student should do after strong or weak performance.
- If a topic is weak, route the student back to the relevant prerequisite or practice stage.
- If the topic is strong, move to the next dependency.

Final Next Action:
- End with one clear immediate action the student should take.

Important rules:
- Use the student's current knowledge when determining the starting point.
- Do not treat advanced topics as prerequisites for foundational topics.
- Keep dependencies logically ordered.
- Make the roadmap practical and student-friendly.
- Do not invent facts about the student.
- Use plain text and Markdown headings/bullets.
- Use normal ASCII hyphens (-), not special dash characters.
- Return only the roadmap.
"""

    return generate_general_answer(prompt)