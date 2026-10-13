import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class MCODERAGEngine:
    @staticmethod
    def process_syllabus_and_generate_pathway(department: str, syllabus_text: str):
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            f"You are MCODE, an expert AI study engine. Analyze the following syllabus for department: {department}. "
            "Break down the raw content into exactly 5 logical units/levels. "
            "For each unit, provide a title, a short summary, recommended reading topics, and a gateway quiz requirement.\n\n"
            f"Syllabus Content:\n{syllabus_text}"
        )
        response = model.generate_content(prompt)
        return response.text

    @staticmethod
    def generate_dynamic_quiz(unit_topic: str):
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            f"Generate 5 multiple-choice quiz questions based on the course topic: {unit_topic}. "
            "Provide options and designate the correct answer clearly."
        )
        response = model.generate_content(prompt)
        return response.text
