from ollama import chat

from backend.app.services.prompt_engine_service import build_system_prompt
from backend.app.services.intent_detection_service import detect_intent


GENERATION_MODEL = "qwen3:0.6b"


def generate_answer(
    question: str,
    context: str
) -> str:
    if not question.strip():
        return ""

    intent = detect_intent(question)
    system_prompt = build_system_prompt(intent=intent)

    user_prompt = f"""
GROUNDING REQUIREMENT:
For grounded_qa, the answer must contain ONLY information explicitly present in the Retrieved Study Material.

STRICT RULES:
- Do not add any information from your own knowledge.
- Do not create or modify examples.
- Do not introduce facts, examples, or concepts that are absent from the Retrieved Study Material. You may combine and clearly explain information that is present in the material.
- Do not infer missing information.
- Do not expand abbreviations or concepts.
- Use only facts and concepts supported by the Retrieved Study Material, but organize and explain those facts in your own words when needed to match the requested examination format.
- If the Retrieved Study Material does not directly answer the question, respond exactly:
"I could not find this information in the provided study material."

Retrieved Study Material:
{context}

Student Question:
{question}

Answer:
"""

    response = chat(
    model=GENERATION_MODEL,
    options={"temperature": 0},
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response["message"]["content"].strip()



