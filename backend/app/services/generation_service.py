import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.services.prompt_engine_service import build_system_prompt
from app.services.intent_detection_service import detect_intent


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

GENERATION_MODEL = "gemini-3.5-flash-lite"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)


def generate_answer(question: str, context: str) -> str:
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
- Do not introduce facts, examples, or concepts that are absent from the Retrieved Study Material.
- You may combine and clearly explain information that is present in the material.
- Do not infer missing information.
- Do not expand abbreviations or concepts.
- Use only facts and concepts supported by the Retrieved Study Material.
- Organize and explain those facts in your own words when needed to match the requested examination format.
- If the Retrieved Study Material does not directly answer the question, respond exactly:
"I could not find this information in the provided study material."

Retrieved Study Material:
{context}

Student Question:
{question}

Answer:
"""

    response = gemini_client.models.generate_content(
        model=GENERATION_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(
                thinking_level="low"
            ),
        ),
    )

    return response.text.strip()


def generate_general_answer(question: str) -> str:
    if not question.strip():
        return ""

    response = gemini_client.models.generate_content(
        model=GENERATION_MODEL,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=(
                "Answer the student's question clearly and accurately "
                "using your general knowledge. Do not claim that the "
                "answer came from uploaded study material."
            ),
            thinking_config=types.ThinkingConfig(
                thinking_level="low"
            ),
        ),
    )

    return response.text.strip()

def generate_grounded_content(
    instruction: str,
    context: str,
) -> str:
    if not instruction.strip() or not context.strip():
        return ""

    prompt = f"""
GROUNDING REQUIREMENT:
Generate the requested content using ONLY the Retrieved Study Material.

STRICT RULES:
- Do not use general knowledge.
- Do not invent facts, examples, formulas, or explanations.
- Do not infer missing information.
- Use only information explicitly supported by the Retrieved Study Material.
- If the material does not provide enough information, clearly say so.

Retrieved Study Material:
{context}

Task:
{instruction}

Return only the requested content.
"""

    response = gemini_client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a grounded educational content generator. "
                "Use only the supplied study material."
            ),
            thinking_config=types.ThinkingConfig(
                thinking_level="low"
            ),
        ),
    )

    return response.text.strip()