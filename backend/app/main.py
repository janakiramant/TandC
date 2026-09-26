import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse

from app.config import settings
from app.pdf_parser import parse_pdf_bytes
from app.llm_service import analyze_document_with_llm, answer_chat_with_llm
from app.schemas import (
    UploadResponse, DocumentAnalysis, ChatRequest, ChatResponse
)
from app.storage import storage

app = FastAPI(
    title="Legal PDF Analyzer AI API",
    description="Backend API for Legal PDF Analyzer MVP",
    version="1.0.0"
)

# Allowed CORS origins: restrict in production via ALLOWED_ORIGINS env var
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization"],
)

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Legal PDF Analyzer AI",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Uploads and parses a legal PDF, performing AI analysis."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF documents (.pdf) are supported."
        )

    file_bytes = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    doc_id = str(uuid.uuid4())

    try:
        pdf = parse_pdf_bytes(doc_id=doc_id, filename=file.filename, file_bytes=file_bytes)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing PDF file: {str(e)}"
        )

    storage.save_pdf(pdf)

    # Perform AI analysis
    analysis = await analyze_document_with_llm(pdf)
    analysis.created_at = datetime.now(timezone.utc).isoformat()
    storage.save_analysis(analysis)

    return UploadResponse(
        doc_id=doc_id,
        filename=file.filename,
        total_pages=pdf.total_pages,
        has_readable_text=pdf.has_readable_text,
        message="PDF processed and analyzed successfully." if pdf.has_readable_text else "PDF uploaded, but no extractable text was found.",
        analysis=analysis
    )

@app.get("/api/analysis/{doc_id}", response_model=DocumentAnalysis)
async def get_analysis(doc_id: str):
    analysis = storage.get_analysis(doc_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis for specified document ID not found."
        )
    return analysis

@app.post("/api/chat", response_model=ChatResponse)
async def chat_document(req: ChatRequest):
    pdf = storage.get_pdf(req.doc_id)
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or session expired. Please re-upload the document."
        )

    if not req.question or not req.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question text cannot be empty."
        )

    res = await answer_chat_with_llm(pdf, req.question.strip())
    return res

@app.get("/api/document/{doc_id}/file")
async def get_document_file(doc_id: str):
    pdf = storage.get_pdf(doc_id)
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found."
        )
    return Response(
        content=pdf.raw_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{pdf.filename}"'}
    )

@app.delete("/api/document/{doc_id}")
async def clear_document(doc_id: str):
    pdf = storage.get_pdf(doc_id)
    if pdf:
        storage.remove(doc_id)
        return {"status": "cleared", "doc_id": doc_id}
    return {"status": "not_found"}
