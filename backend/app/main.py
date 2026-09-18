from pathlib import Path
import os

from fastapi import FastAPI
from dotenv import load_dotenv

from backend.app.models.question_model import QuestionRequest, QuestionResponse
from backend.app.services.document_loader_service import load_document
from backend.app.services.rag_service import answer_question_with_citations

load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "Subject Guide AI"),
    description="AI-powered Subject Guide and Question Bank Assistant",
    version="0.1.0"
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
    pdf_path = Path(__file__).resolve().parents[2] / "backend" / "tests" / "simple.pdf"

    document = load_document(str(pdf_path))

    result = answer_question_with_citations(
        request.question,
        document.chunks,
        top_k=request.top_k
    )

    return QuestionResponse(
        question=request.question,
        answer=result.answer,
        citations=result.citations
    )
