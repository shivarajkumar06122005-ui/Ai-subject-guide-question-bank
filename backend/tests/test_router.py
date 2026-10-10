import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.services.intent_detection_service import route_intent


def check(text, intent):
    result = route_intent(text)
    assert result.intent == intent, (text, result.model_dump())
    assert result.route == intent
    assert 0 <= result.confidence <= 1


def test_study(): check("Explain recursion", "study")
def test_quiz(): check("Give me 10 MCQs on recursion", "quiz")
def test_exam_2():
    result = route_intent("Give me a 2 mark answer for SVM")
    assert result.intent == "exam" and result.parameters.marks == 2

def test_exam_5():
    result = route_intent("Give me a 5 mark answer for SVM")
    assert result.intent == "exam" and result.parameters.marks == 5

def test_exam_10():
    result = route_intent("Give me a 10 mark answer for SVM")
    assert result.intent == "exam" and result.parameters.marks == 10

def test_flashcard(): check("Create flashcards for normalization", "flashcard")
def test_planner(): check("Make my study plan for this week", "planner")
def test_pyq(): check("Analyze these PYQs", "pyq_analysis")
def test_interview(): check("Interview me on Python", "interview")
def test_reteach(): check("I don't understand normalization", "reteach")
def test_next_step(): check("What should I learn next?", "next_step")
def test_practice(): check("Test me on algorithms", "practice")
def test_general(): check("Can you help me?", "general")
