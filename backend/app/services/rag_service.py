from backend.app.models.chunk_model import DocumentChunk
from backend.app.services.generation_service import generate_answer
from backend.app.services.retrieval_service import retrieve_relevant_chunks


def answer_question(
    question: str,
    chunks: list[DocumentChunk],
    top_k: int = 3
) -> str:
    if not question.strip():
        return ""

    relevant_chunks = retrieve_relevant_chunks(
        question,
        chunks,
        top_k=top_k
    )

    if not relevant_chunks:
        return "I could not find this information in the provided study material."

    context = "\n\n".join(
        chunk.text
        for chunk in relevant_chunks
    )

    return generate_answer(
        question,
        context
    )