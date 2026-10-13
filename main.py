from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from models import StudentProfile, QuizSubmission
from rag_engine import MCODERAGEngine
from database import init_db, save_user_profile, get_user_profile, update_user_progress
import shutil
import os
import PyPDF2

app = FastAPI(title="MCODE Backend Study Engine", version="1.0.0")

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/api/student/profile")
def create_profile(profile: StudentProfile):
    save_user_profile(profile.email, profile.full_name, profile.academic_level, profile.department)
    return {
        "status": "success",
        "message": f"Welcome to MCODE, {profile.full_name}! Profile saved to database.",
        "profile": profile
    }

@app.get("/api/student/{email}")
def get_profile(email: str):
    user = get_user_profile(email)
    if not user:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    return {"status": "success", "profile": user}

@app.post("/api/pathway/generate")
async def generate_pathway(
    department: str = Form(...),
    syllabus_file: UploadFile = File(...)
):
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{syllabus_file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(syllabus_file.file, buffer)
        
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
    # Mock grading: evaluating if submission is valid
    score_percentage = 60.0 
    passed = score_percentage >= 40.0
    tokens_earned = 50 if passed else 0
    
    # If passed, update tokens and streak in database using user_id as email
    if passed:
        update_user_progress(submission.user_id, tokens_earned)
    
    return {
        "user_id": submission.user_id,
        "unit_id": submission.unit_id,
        "score_percentage": score_percentage,
        "passed": passed,
        "tokens_earned": tokens_earned,
        "message": "Gateway unlocked successfully! Tokens and streak updated." if passed else "Score too low. Try again."
    }
