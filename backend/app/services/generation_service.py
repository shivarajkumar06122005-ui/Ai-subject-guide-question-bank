from ollama import chat


GENERATION_MODEL = "qwen3:0.6b"


def generate_answer(
    question: str,
    context: str
) -> str:
    if not question.strip():
        return ""

    prompt = f"""
You are an AI Subject Guide.

Answer the student's question using only the provided context.

If the answer cannot be found in the context, say:
"I could not find this information in the provided study material."

Do not invent information.

Context:
{context}

Student Question:
{question}

Answer:
"""

    response = chat(
        model=GENERATION_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()