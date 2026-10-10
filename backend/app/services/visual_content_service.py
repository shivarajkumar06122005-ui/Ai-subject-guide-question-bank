from app.services.generation_service import generate_general_answer


def generate_visual_content(
    topic: str,
    visual_learning_spec: str = "",
    student_level: str = "",
) -> str:
    if not topic.strip():
        return ""

    specification = (
        visual_learning_spec.strip()
        or "No visual learning specification provided."
    )
    level = student_level.strip() or "Student level not specified."

    prompt = f"""
You are the Visual Content Agent for Subject Guide AI.

Your job is to transform a visual learning specification into structured
visual content that can later be rendered by a frontend or visualization
system.

Topic:
{topic}

Student Level:
{level}

Visual Learning Specification:
{specification}

Create the visual content using this structure:

1. Visual Type
- Identify the most suitable visual format:
  diagram, flowchart, tree, timeline, comparison table, graph,
  concept map, or another appropriate format.

2. Visual Title
- Provide a short descriptive title.

3. Visual Elements
- List the objects, nodes, labels, or components that should appear.

4. Relationships
- Describe how the visual elements connect to each other.
- Clearly identify direction, hierarchy, sequence, or comparison where relevant.

5. Layout
- Describe how the elements should be arranged.

6. Example
- Provide the example content that should appear in the visual.

7. Rendering Specification
- Provide a concise structured specification that a frontend
  visualization component could use to render the visual.

Important rules:
- Use the supplied visual learning specification as the primary basis.
- Do not claim that an actual image has been generated.
- Do not invent unsupported relationships.
- Keep the structure accurate and suitable for the student's level.
- Return only the visual content specification.
- Use Markdown headings and bullets.
- Use normal ASCII hyphens (-).
"""

    return generate_general_answer(prompt)