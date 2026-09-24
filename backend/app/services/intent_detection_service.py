INTENTS = [
    "grounded_qa",
    "definition",
    "explain",
    "summarize",
    "compare",
    "exam_answer",
    "quiz",
    "question_generation",
]


def detect_intent(question: str) -> str:
    if not question.strip():
        return "grounded_qa"

    text = question.lower().strip()

    if any(word in text for word in ["mcq", "quiz", "multiple choice"]):
        return "quiz"

    if any(word in text for word in ["5 mark", "5-mark", "10 mark", "exam answer"]):
        return "exam_answer"

    if any(word in text for word in ["compare", "difference between", "differentiate"]):
        return "compare"

    if any(word in text for word in ["summarize", "summary", "short notes"]):
        return "summarize"

    if any(word in text for word in ["what is", "define", "definition"]):
        return "definition"

    if any(word in text for word in ["generate questions", "create questions", "question bank"]):
        return "question_generation"

    if any(word in text for word in ["explain", "how does", "how do"]):
        return "explain"

    return "grounded_qa"
