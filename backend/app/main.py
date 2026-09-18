from fastapi import FastAPI
from dotenv import load_dotenv
import os

from backend.app.models.chunk_model import DocumentChunk
from backend.app.models.question_model import QuestionRequest, QuestionResponse
from backend.app.services.rag_service import answer_question

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
    chunks = [
        DocumentChunk(
            text="Python is a high-level programming language used for software development and data analysis.",
            source="python_notes.pdf",
            chunk_index=0,
            page_number=1
        ),
        DocumentChunk(
            text="SQL is used to manage and query relational databases.",
            source="sql_notes.pdf",
            chunk_index=1,
            page_number=2
        ),
        DocumentChunk(
            text="Photosynthesis is the process by which plants produce food using sunlight.",
            source="biology_notes.pdf",
            chunk_index=2,
            page_number=3
        )
    ]

    answer = answer_question(
        request.question,
        chunks,
        top_k=request.top_k
    )

    return QuestionResponse(
        question=request.question,
        answer=answer
    )