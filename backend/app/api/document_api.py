from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.document_service import process_pdf


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    file_path = UPLOAD_DIR / Path(file.filename).name

    content = await file.read()
    file_path.write_bytes(content)

    try:
        result = process_pdf(str(file_path))
    except Exception as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail=f"Could not process PDF: {exc}"
        )

    return {
        "filename": result.source,
        "pages": len({
            chunk.page_number
            for chunk in result.chunks
            if chunk.page_number is not None
        }),
        "chunks": result.total_chunks,
        "status": "READY",
    }