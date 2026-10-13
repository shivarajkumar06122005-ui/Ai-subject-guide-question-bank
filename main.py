from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from models import StudentProfile, QuizSubmission
from rag_engine import MCODERAGEngine
import shutil
import os
import PyPDF2

app = FastAPI(title="MCODE Backend Study Engine", version="1.0.0")

@app.post("/api/student/profile")
def create_profile(profile: StudentProfile):
    return {
        "status": "success",
        "message": f"Welcome to MCODE, {profile.full_name}!",
        "profile": profile
    }

@app.post("/api/pathway/generate")
async def generate_pathway(
    department: str = Form(...),
    syllabus_file: UploadFile = File(...)
):
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{syllabus_file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(syllabus_file.file, buffer)
        
    # Extract text correctly based on file type
    syllabus_text = ""
    if syllabus_file.filename.endswith('.pdf'):
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                syllabus_text += page.extract_text() or ""
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            syllabus_text = f.read()
            
    pathway_result = MCODERAGEngine.process_syllabus_and_generate_pathway(department, syllabus_text)
    
    return {
        "status": "success",
        "department": department,
        "pathway_structure": pathway_result
    }

@app.get("/api/quiz/generate/{unit_topic}")
def get_gateway_quiz(unit_topic: str):
    quiz = MCODERAGEngine.generate_dynamic_quiz(unit_topic)
    return {
        "status": "success",
        "unit_topic": unit_topic,
        "quiz_content": quiz
    }

@app.post("/api/quiz/submit")
def evaluate_quiz(submission: QuizSubmission):
    score_percentage = 60.0 
    passed = score_percentage >= 40.0
    tokens_earned = 50 if passed else 0
    
    return {
        "user_id": submission.user_id,
        "unit_id": submission.unit_id,
        "score_percentage": score_percentage,
        "passed": passed,
        "tokens_earned": tokens_earned,
        "message": "Gateway unlocked successfully!" if passed else "Score too low. Try again."
    }
