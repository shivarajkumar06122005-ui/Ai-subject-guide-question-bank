import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

GENERATION_MODEL = "gemini-3.5-flash-lite"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)


REASONING_SCHEMA = {
    "type": "object",
    "properties": {
        "domain": {
            "type": "string",
            "enum": ["math", "calculus", "trigonometry", "inequality", "python", "logic", "unknown"],
        },
        "problem": {
            "type": "string",
        },
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step": {
                        "type": "integer",
                    },
                    "text": {
                        "type": "string",
                    },
                    "expression": {
                        "type": "string",
                    },
                },
                "required": ["step", "text", "expression"],
            },
        },
    },
    "required": ["domain", "problem", "steps"],
}


def parse_reasoning(reasoning: str) -> dict:
    """
    F1.5: Convert natural-language student reasoning into
    structured verification-ready steps.

    Gemini only parses the reasoning.
    It does NOT decide whether the reasoning is correct.
    """

    if not reasoning.strip():
        return {
            "domain": "unknown",
            "problem": "",
            "steps": [],
        }

    prompt = f"""
You are the reasoning parser for an educational verification system.

Your ONLY job is to convert the student's reasoning into structured,
machine-readable steps.

Do NOT decide whether the student's reasoning is correct.
Do NOT fix mistakes.
Do NOT invent missing steps.
Do NOT add mathematical knowledge that the student did not express.

Preserve the student's reasoning faithfully.

For every identifiable reasoning step:
- assign a sequential step number
- copy the meaning of the student's step into "text"
- extract the mathematical/code/logical expression into "expression"
- if no explicit expression exists, use the closest faithful representation
- never silently correct an incorrect expression

Identify the most appropriate domain.

Student reasoning:
{reasoning}
"""

    response = gemini_client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=REASONING_SCHEMA,
            system_instruction=(
                "You are a faithful reasoning parser. "
                "Parse only. Never judge correctness and never repair "
                "the student's reasoning."
            ),
            thinking_config=types.ThinkingConfig(
                thinking_level="low"
            ),
        ),
    )

    return json.loads(response.text)
