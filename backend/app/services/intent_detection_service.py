"""Week 5 Feature #1: Router / Intent Agent.

The router is intentionally independent from the specialized agents. It only
classifies intent, extracts lightweight parameters, and selects a route.
"""

import json
import re
from typing import Any

from app.models.router_model import RouterParameters, RouterResult, ROUTER_INTENTS


ROUTE_BY_INTENT = {intent: intent for intent in ROUTER_INTENTS}


def _parameters_from_text(text: str, *, document_related=False, image_related=False, voice_related=False) -> RouterParameters:
    lowered = text.lower()
    marks = None
    match = re.search(r"\b(2|5|10|15|20)\s*[- ]?mark(?:s)?\b", lowered)
    if match:
        marks = int(match.group(1))

    count = None
    match = re.search(r"\b(\d+)\s+(?:mcqs?|questions?|qns?)\b", lowered)
    if match:
        count = int(match.group(1))

    difficulty = next((d for d in ("easy", "medium", "hard", "difficult") if d in lowered), None)

    language = None
    for name in ("english", "kannada", "hindi", "tamil", "telugu", "malayalam"):
        if name in lowered:
            language = name
            break

    topic = None
    topic_match = re.search(r"\b(?:on|about|for|of|in)\s+([a-z0-9][a-z0-9 &+/#.-]{1,80}?)(?:\?|$)", text, re.I)
    if topic_match:
        topic = topic_match.group(1).strip(" .")
        topic = re.sub(r"^(?:this|the)\s+", "", topic, flags=re.I)

    subject = None
    for name in ("python", "dbms", "database", "sql", "machine learning", "artificial intelligence", "ai", "data structures", "algorithms", "computer networks", "operating systems"):
        if name in lowered:
            subject = name
            break

    return RouterParameters(
        subject=subject,
        topic=topic,
        marks=marks,
        question_count=count,
        difficulty=difficulty,
        language=language,
        requested_mode=("exam" if marks else None),
        document_related=document_related or any(x in lowered for x in ("uploaded", "document", "notes", "textbook", "pdf", "pyq")),
        image_related=image_related or any(x in lowered for x in ("image", "photo", "picture", "screenshot")),
        voice_related=voice_related or any(x in lowered for x in ("voice", "speak", "audio")),
    )


def _keyword_route(text: str) -> tuple[str, float] | None:
    t = text.lower().strip()

    # High-signal intents first so overlapping words do not cause surprising routes.
    rules = [
        ("image_question", ("explain this image", "solve this image", "image question", "photo of", "screenshot of"), 0.99),
        ("voice", ("by voice", "using voice", "voice question", "speak to me", "talk to me"), 0.99),
        ("mock_test", ("mock test", "take a mock test"), 0.96),
        ("interview", ("mock interview", "interview me", "take an interview"), 0.99),
        ("pyq_analysis", ("analyze these pyq", "analyze pyq", "analyse these pyq", "repeated questions", "previous year questions"), 0.99),
        ("flashcard", ("flashcard", "flash cards", "flash cards for", "create cards"), 0.99),
        ("planner", ("study plan", "study planner", "plan my study", "what should i study this week", "plan for this week"), 0.99),
        ("next_step", ("what should i learn next", "what do i learn next", "learn next", "next topic"), 0.99),
        ("reteach", ("teach this again", "i don't understand", "i dont understand", "explain again", "reteach", "still don't understand"), 0.98),
        ("exam", ("mark answer", "marks answer", "exam answer", "exam mode", "write a 2 mark", "write a 5 mark", "write a 10 mark", "give a 2 mark", "give a 5 mark", "give a 10 mark"), 0.99),
        ("quiz", ("mcq", "mcqs", "multiple choice", "quiz me", "give me a quiz", "create a quiz"), 0.99),
        ("practice", ("practice questions", "practice on", "practice with", "test my knowledge", "test me on"), 0.94),
        ("challenge", ("challenge me", "give me a challenge", "hard challenge"), 0.97),
        ("revision", ("revise", "revision", "quick revision", "revision notes", "help me revise"), 0.96),
        ("teacher", ("teach me", "be my teacher", "personal tutor", "teach this topic"), 0.95),
        ("document_question", ("according to my notes", "from my notes", "from the textbook", "from the uploaded", "based on the pdf"), 0.93),
        ("study", ("explain", "what is", "define", "how does", "how do", "tell me about"), 0.90),
    ]

    for intent, phrases, confidence in rules:
        if any(phrase in t for phrase in phrases):
            return intent, confidence
    return None


def _ai_fallback(text: str, *, document_related=False, image_related=False, voice_related=False) -> RouterResult:
    schema_hint = {
        "intent": "one of: " + ", ".join(sorted(ROUTER_INTENTS)),
        "confidence": 0.0,
        "route": "same as intent",
        "parameters": {
            "subject": None,
            "topic": None,
            "marks": None,
            "difficulty": None,
            "question_count": None,
            "time_limit": None,
            "language": None,
            "requested_mode": None,
            "document_related": False,
            "image_related": False,
            "voice_related": False,
        },
    }
    prompt = f"""Classify this student request. Return ONLY valid JSON matching this shape:\n{json.dumps(schema_hint)}\n\nRules: choose one intent only; do not answer the student; if ambiguous use general with confidence below 0.60.\nStudent request: {text}"""
    try:
        from ollama import chat
        response = chat(
            model="qwen3:0.6b",
            options={"temperature": 0},
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response["message"]["content"].strip()
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I | re.S)
        data: dict[str, Any] = json.loads(raw)
        result = RouterResult.model_validate(data)
        if result.intent not in ROUTER_INTENTS or result.confidence < 0.60:
            return RouterResult(intent="general", confidence=min(result.confidence, 0.59), route="general", parameters=_parameters_from_text(text, document_related=document_related, image_related=image_related, voice_related=voice_related))
        result.route = result.intent
        return result
    except Exception:
        return RouterResult(intent="general", confidence=0.0, route="general", parameters=_parameters_from_text(text, document_related=document_related, image_related=image_related, voice_related=voice_related))


def route_intent(text: str, *, document_related=False, image_related=False, voice_related=False) -> RouterResult:
    """Classify a request using deterministic rules first and AI only when needed."""
    if not text.strip():
        return RouterResult(intent="general", confidence=0.0, route="general", parameters=RouterParameters())

    matched = _keyword_route(text)
    params = _parameters_from_text(text, document_related=document_related, image_related=image_related, voice_related=voice_related)

    if matched:
        intent, confidence = matched
        return RouterResult(intent=intent, confidence=confidence, route=ROUTE_BY_INTENT[intent], parameters=params)

    return _ai_fallback(text, document_related=document_related, image_related=image_related, voice_related=voice_related)


# Backward-compatible helper used by the existing generation service.
def detect_intent(question: str) -> str:
    result = route_intent(question)
    return result.intent
