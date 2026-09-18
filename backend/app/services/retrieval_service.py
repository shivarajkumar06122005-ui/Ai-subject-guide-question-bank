from backend.app.models.chunk_model import DocumentChunk


def retrieve_relevant_chunks(
    query: str,
    chunks: list[DocumentChunk],
    top_k: int = 3
) -> list[DocumentChunk]:
    """
    Retrieve the most relevant document chunks for a query.

    Placeholder implementation for the Week 3 RAG retrieval layer.
    Semantic similarity search will be connected later.
    """

    if not query.strip():
        return []

    return chunks[:top_k]