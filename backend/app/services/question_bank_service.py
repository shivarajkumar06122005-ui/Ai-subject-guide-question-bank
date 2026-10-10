from pathlib import Path

from app.services.document_service import process_pdf
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.generation_service import generate_grounded_content
from app.services.embedding_service import create_embedding
from app.services.retrieval_service import cosine_similarity


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"


def generate_question_bank(
    topic: str,
    question_count: int = 5,
    difficulty: str = "mixed",
    question_type: str = "mixed",
    study_text: str = "",
) -> str:
    if not topic.strip():
        return ""

    if question_count < 1:
        question_count = 1

    if question_count > 20:
        question_count = 20

    # Student-provided study text takes priority.
    if study_text.strip():
        context = study_text.strip()

    else:
        pdf_files = sorted(UPLOAD_DIR.glob("*.pdf"))

        if not pdf_files:
            return (
                "I could not generate a question bank because "
                "no study material has been provided."
            )

        pdf_path = max(
            pdf_files,
            key=lambda path: path.stat().st_mtime
        )

        document = process_pdf(str(pdf_path))

        if not document.chunks:
            return (
                "I could not generate a question bank because "
                "the uploaded study material contains no readable text."
            )

        relevant_chunks = retrieve_relevant_chunks(
            topic,
            document.chunks,
            top_k=5
        )

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
            return (
                "I could not find enough information about this topic "
                "in the provided study material."
            )

        context = "\n\n".join(
            chunk.text
            for chunk in relevant_chunks
        )

    instruction = f"""
You are the Question Bank Agent for Subject Guide AI.

Generate a grounded question bank from the provided study material.

Topic:
{topic}

Number of Questions:
{question_count}

Difficulty:
{difficulty}

Question Type:
{question_type}

Study Material:
{context}

Create exactly {question_count} questions.

For each question provide:

1. Question number
2. Question
3. Question type
4. Difficulty
5. Answer
6. Short explanation

QUESTION TYPES:
- MCQ
- Short Answer
- True/False
- Fill in the Blank

If the requested question type is "mixed", use a suitable mixture
of the supported types.

If the requested difficulty is "mixed", use a suitable mixture of
easy, medium, and difficult questions where the study material
supports the required difficulty.ble 

STRICT GROUNDING RULES:
- Use ONLY information supported by the study material.
- Do not use general knowledge.
- Do not invent facts, examples, formulas, definitions, or values.
- Do not create questions about information absent from the material.
- Answers must be directly supported by the study material.
- Explanations must also be grounded in the study material.
- If the material does not contain enough information to generate
  the requested number of valid questions, clearly state that
  there is not enough information instead of inventing questions.
- Do not claim that an assessment has been conducted.
- This agent creates a question bank only.
- Return only the question bank.
"""

    return generate_grounded_content(
        instruction=instruction,
        context=context
    )