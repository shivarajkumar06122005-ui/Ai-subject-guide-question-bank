from pathlib import Path

from app.services.generation_service import generate_grounded_content
from app.services.document_service import process_pdf
from app.services.retrieval_service import retrieve_relevant_chunks


def generate_study_guide(
    topic: str,
    context: str,
) -> str:
    if not topic.strip():
        return ""

    if not context.strip():
        upload_dir = Path(__file__).resolve().parents[2] / "uploads"
        pdf_files = sorted(upload_dir.glob("*.pdf"))

        if not pdf_files:
            return ""

        pdf_path = max(pdf_files, key=lambda path: path.stat().st_mtime)
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

        context = "\n\n".join(
            chunk.text
            for chunk in relevant_chunks
        )

    instruction = f"""
You are the Study Guide Agent for Subject Guide AI.

Create a structured study guide for the following topic:

Topic:
{topic}

The study guide must help a student understand and revise the topic.

Use this structure:

1. Topic
2. Overview
3. Key Concepts
4. Important Points
5. Examples
6. Quick Revision
7. Exam Focus

GROUNDING RULES:
- Use ONLY information supported by the provided study material.
- Do not use general knowledge.
- Do not invent definitions, examples, formulas, facts, or applications.
- Do not introduce concepts that are absent from the study material.
- Do not infer information that is not explicitly supported.
- Keep explanations clear and student-friendly.
- Examples must come only from the study material.
- If a section is not supported by the material, write:
  "Not available in the provided study material."
- Do not claim that the student has mastered the topic.
- Do not create an assessment.
- Return only the study guide.

Study Material:
{context}
"""

    return generate_grounded_content(
        instruction=instruction,
        context=context,
    )