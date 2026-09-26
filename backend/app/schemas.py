from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class Finding(BaseModel):
    id: str = Field(..., description="Unique identifier for the finding")
    type: Literal["favorable", "risk", "important"] = Field(
        ..., description="Category: favorable (positive), risk (concern), or important (clause)"
    )
    title: str = Field(..., description="Short descriptive title of the finding")
    summary: str = Field(..., description="Concise explanation grounded in the document")
    page: int = Field(..., description="Page number where finding appears (1-indexed)")
    section: Optional[str] = Field(None, description="Section or clause reference e.g., 'Section 8.2'")
    source_text: str = Field(..., description="Exact quoted text or evidence snippet from the PDF")

class DocumentAnalysis(BaseModel):
    doc_id: str
    filename: str
    total_pages: int
    summary: str
    findings: List[Finding]
    created_at: str
    has_readable_text: bool = True
    error_message: Optional[str] = None

class ChatRequest(BaseModel):
    doc_id: str
    question: str

class ChatSource(BaseModel):
    page: int
    section: Optional[str] = None
    snippet: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource] = []
    is_grounded: bool = True

class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    total_pages: int
    has_readable_text: bool
    message: str
    analysis: Optional[DocumentAnalysis] = None
