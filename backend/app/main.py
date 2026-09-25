from pathlib import Path
import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.app.models.question_model import QuestionRequest, QuestionResponse
from backend.app.services.document_loader_service import load_document
from backend.app.services.rag_service import answer_question_with_citations
from backend.app.services.document_service import list_uploaded_documents

load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "Subject Guide AI"),
    description="AI-powered Subject Guide and Question Bank Assistant",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_document_chunks = []
document_store = {}


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
    all_document_chunks = [chunk for chunks in document_store.values() for chunk in chunks]

    if not all_document_chunks:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF before asking a question."
        )

    result = answer_question_with_citations(
        request.question,
        all_document_chunks,
        top_k=request.top_k
    )

    return QuestionResponse(
        question=request.question,
        answer=result.answer,
        citations=result.citations
    )


@app.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    global active_document_chunks

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    upload_dir = Path(__file__).resolve().parents[2] / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename

    content = await file.read()

    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="PDF must be smaller than 20 MB."
        )

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    document = load_document(str(file_path))
    document_store[file.filename] = document.chunks
    active_document_chunks = document.chunks

    return {
        "message": "PDF uploaded and processed successfully",
        "filename": file.filename,
        "path": str(file_path),
        "size": len(content),
        "total_chunks": document.total_chunks
    }


@app.get("/api/v1/documents")
def get_documents():
    upload_dir = Path(__file__).resolve().parents[2] / "uploads"
    return {
        "documents": list_uploaded_documents(str(upload_dir))
    }


@app.delete("/api/v1/documents/{filename}")
def delete_document(filename: str):
    upload_dir = Path(__file__).resolve().parents[2] / "uploads"
    file_path = upload_dir / filename

    if not file_path.exists() or file_path.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    file_path.unlink()
    document_store.pop(filename, None)

    return {
        "message": "Document deleted successfully",
        "filename": filename
    }











