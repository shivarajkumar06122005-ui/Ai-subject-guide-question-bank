from math import sqrt

from backend.app.models.chunk_model import DocumentChunk
from backend.app.services.embedding_service import create_embedding


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float]
) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError("Vectors must have the same dimensions")

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def retrieve_relevant_chunks(
    query: str,
    chunks: list[DocumentChunk],
    top_k: int = 3
) -> list[DocumentChunk]:
    """
    Retrieve the most relevant document chunks using
    cosine similarity between query and document embeddings.
    """

    if not query.strip() or not chunks:
        return []

    query_embedding = create_embedding(query)

    scored_chunks = []

    for chunk in chunks:
        chunk_embedding = create_embedding(chunk.text)

        score = cosine_similarity(
            query_embedding,
            chunk_embedding
        )

        scored_chunks.append((score, chunk))

    scored_chunks.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        chunk
        for _, chunk in scored_chunks[:top_k]
    ]
