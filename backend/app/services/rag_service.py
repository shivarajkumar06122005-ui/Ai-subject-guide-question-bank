from backend.app.models.chunk_model import DocumentChunk
from backend.app.models.rag_model import RAGResponse, SourceCitation
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


def answer_question_with_citations(
    question: str,
    chunks: list[DocumentChunk],
    top_k: int = 3
) -> RAGResponse:
    if not question.strip():
        return RAGResponse(
            answer="",
            citations=[]
        )

    relevant_chunks = retrieve_relevant_chunks(
        question,
        chunks,
        top_k=top_k
    )

    if not relevant_chunks:
        return RAGResponse(
            answer="I could not find this information in the provided study material.",
            citations=[]
        )

    context = "\n\n".join(
        chunk.text
        for chunk in relevant_chunks
    )

    answer = generate_answer(
        question,
        context
    )

    citations = [
        SourceCitation(
            source=chunk.source,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index
        )
        for chunk in relevant_chunks
    ]

    return RAGResponse(
        answer=answer,
        citations=citations
    )
