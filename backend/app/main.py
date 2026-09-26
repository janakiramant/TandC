import re
import uuid
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.pdf_parser import parse_pdf_bytes
from app.llm_service import analyze_document_with_llm, answer_chat_with_llm
from app.schemas import (
    UploadResponse, DocumentAnalysis, ChatRequest, ChatResponse
)
from app.storage import storage

logger = logging.getLogger("legal_pdf_analyzer.api")

# ---------------------------------------------------------------------------
# Rate limiter (backed by in-process memory – suitable for single-instance)
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Legal PDF Analyzer AI API",
    description="Backend API for Legal PDF Analyzer MVP",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization"],
)

# ---------------------------------------------------------------------------
# Security headers middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_SAFE_FILENAME_RE = re.compile(r'[^\w\-. ]')

def _sanitize_filename(filename: str) -> str:
    """Strip characters unsafe for Content-Disposition headers."""
    safe = _SAFE_FILENAME_RE.sub('_', filename)
    return safe[:200]  # cap length

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Legal PDF Analyzer AI",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/upload", response_model=UploadResponse)
@limiter.limit("10/minute")
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    """Uploads and parses a legal PDF, performing AI analysis."""
    # Validate file extension
    if not file.filename or not file.filename.lower().endswith(".pdf"):
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

    # Validate the file begins with the PDF magic bytes
    if not file_bytes.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file does not appear to be a valid PDF document."
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
        logger.exception("Unexpected error parsing PDF")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error parsing PDF file. Please ensure the document is not corrupted."
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
@limiter.limit("30/minute")
async def chat_document(request: Request, req: ChatRequest):
    pdf = storage.get_pdf(req.doc_id)
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or session expired. Please re-upload the document."
        )

    question = (req.question or "").strip()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question text cannot be empty."
        )

    if len(question) > settings.MAX_QUESTION_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question exceeds the maximum allowed length of {settings.MAX_QUESTION_LENGTH} characters."
        )

    res = await answer_chat_with_llm(pdf, question)
    return res


@app.get("/api/document/{doc_id}/file")
async def get_document_file(doc_id: str):
    pdf = storage.get_pdf(doc_id)
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found."
        )
    safe_name = _sanitize_filename(pdf.filename)
    return Response(
        content=pdf.raw_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{safe_name}"'}
    )


@app.delete("/api/document/{doc_id}")
async def clear_document(doc_id: str):
    pdf = storage.get_pdf(doc_id)
    if pdf:
        storage.remove(doc_id)
        return {"status": "cleared", "doc_id": doc_id}
    return {"status": "not_found"}
