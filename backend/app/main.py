from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.app.models.question_model import QuestionRequest, QuestionResponse
from backend.app.services.document_loader_service import load_document
from backend.app.services.rag_service import answer_question_with_citations
from backend.app.services.generation_service import generate_general_answer
from backend.app.api.router_api import router as router_api
from backend.app.services.intent_detection_service import route_intent
from backend.app.api.learning_roadmap_api import router as learning_roadmap_router
from backend.app.api.prerequisite_api import router as prerequisite_router
from backend.app.api.ai_teacher_api import router as ai_teacher_router
from backend.app.api.visual_learning_api import router as visual_learning_router
from backend.app.api.visual_content_api import router as visual_content_router
from backend.app.api.ai_whiteboard_api import router as ai_whiteboard_router
from backend.app.api.teaching_video_api import router as teaching_video_router
from backend.app.api.document_api import router as document_router
from backend.app.api.virtual_teacher_api import router as virtual_teacher_router
from backend.app.api.voice_teacher_api import router as voice_teacher_router
from backend.app.api.question_bank_api import router as question_bank_router
from backend.app.api.assessment_api import router as assessment_router
from backend.app.api.adaptive_learning_api import router as adaptive_learning_router
from backend.app.api.study_guide_api import router as study_guide_router
from backend.app.api.verified_reasoning_api import router as verified_reasoning_router
from backend.app.api.metacognitive_api import router as metacognitive_router
from backend.app.api.reconstruction_gate_api import router as reconstruction_gate_router
from backend.app.api.synthetic_peer_api import router as synthetic_peer_router
from backend.app.api.student_profile_api import router as student_profile_router

load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "Subject Guide AI"),
    description="AI-powered Subject Guide and Question Bank Assistant",
    version="0.1.0"
)

app.include_router(router_api)
app.include_router(learning_roadmap_router)
app.include_router(prerequisite_router)
app.include_router(ai_teacher_router)
app.include_router(visual_learning_router)
app.include_router(visual_content_router)
app.include_router(ai_whiteboard_router)
app.include_router(teaching_video_router)
app.include_router(document_router)
app.include_router(virtual_teacher_router)
app.include_router(voice_teacher_router)
app.include_router(question_bank_router)
app.include_router(assessment_router)
app.include_router(adaptive_learning_router)
app.include_router(study_guide_router)
app.include_router(verified_reasoning_router)
app.include_router(metacognitive_router)
app.include_router(reconstruction_gate_router)
app.include_router(synthetic_peer_router)
app.include_router(student_profile_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Subject Guide AI backend is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/api/v1/question", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    # Route the question before running retrieval.
    route_intent(request.question)

    upload_dir = Path(__file__).resolve().parents[1] / "uploads"

    pdf_files = sorted(upload_dir.glob("*.pdf"))

    if not pdf_files:
        return QuestionResponse(
            question=request.question,
            answer=generate_general_answer(request.question),
            citations=[]
        )

    all_chunks = []

    for pdf_path in pdf_files:
        document = load_document(str(pdf_path))
        all_chunks.extend(document.chunks)

    result = answer_question_with_citations(
        request.question,
        all_chunks,
        top_k=request.top_k
    )

    if result.answer.strip() == "I could not find this information in the provided study material.":
        return QuestionResponse(
            question=request.question,
            answer=generate_general_answer(request.question),
            citations=[]
        )

    return QuestionResponse(
        question=request.question,
        answer=result.answer,
        citations=result.citations
    )









