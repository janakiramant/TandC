"""
Additional tests covering security hardening and storage efficiency improvements.
"""
import io
import fitz
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import Storage
from app.config import settings

client = TestClient(app)


def _make_pdf(text: str = "Test contract content.") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    b = doc.tobytes()
    doc.close()
    return b


# ---------------------------------------------------------------------------
# Security: input validation
# ---------------------------------------------------------------------------

class TestSecurityInputValidation:
    def test_upload_non_pdf_extension_rejected(self):
        files = {"file": ("report.docx", io.BytesIO(b"fake content"), "application/msword")}
        resp = client.post("/api/upload", files=files)
        assert resp.status_code == 400
        assert "Invalid file type" in resp.json()["detail"]

    def test_upload_pdf_with_fake_magic_bytes_rejected(self):
        """File named .pdf but without PDF magic bytes should be rejected."""
        files = {"file": ("trap.pdf", io.BytesIO(b"NOT_A_REAL_PDF_CONTENT"), "application/pdf")}
        resp = client.post("/api/upload", files=files)
        assert resp.status_code == 400

    def test_chat_empty_question_rejected(self):
        pdf_bytes = _make_pdf()
        files = {"file": ("contract.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        doc_id = client.post("/api/upload", files=files).json()["doc_id"]

        resp = client.post("/api/chat", json={"doc_id": doc_id, "question": "   "})
        assert resp.status_code == 400
        assert "empty" in resp.json()["detail"].lower()

    def test_chat_question_too_long_rejected(self):
        pdf_bytes = _make_pdf()
        files = {"file": ("contract.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        doc_id = client.post("/api/upload", files=files).json()["doc_id"]

        long_question = "x" * (settings.MAX_QUESTION_LENGTH + 1)
        resp = client.post("/api/chat", json={"doc_id": doc_id, "question": long_question})
        assert resp.status_code == 400
        assert "maximum allowed length" in resp.json()["detail"].lower()

    def test_chat_unknown_doc_id_returns_404(self):
        resp = client.post("/api/chat", json={"doc_id": "nonexistent-id", "question": "What is this?"})
        assert resp.status_code == 404

    def test_get_analysis_unknown_id_returns_404(self):
        resp = client.get("/api/analysis/nonexistent-doc-id")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Security: response headers
# ---------------------------------------------------------------------------

class TestSecurityHeaders:
    def test_health_response_has_security_headers(self):
        resp = client.get("/api/health")
        assert resp.headers.get("x-content-type-options") == "nosniff"
        assert resp.headers.get("x-frame-options") == "DENY"
        assert resp.headers.get("referrer-policy") == "strict-origin-when-cross-origin"

    def test_document_file_endpoint_returns_pdf_content_type(self):
        pdf_bytes = _make_pdf("Confidential Agreement")
        files = {"file": ("secure.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        doc_id = client.post("/api/upload", files=files).json()["doc_id"]

        resp = client.get(f"/api/document/{doc_id}/file")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        # Ensure Content-Disposition is present and contains safe filename
        cd = resp.headers.get("content-disposition", "")
        assert "secure.pdf" in cd


# ---------------------------------------------------------------------------
# Efficiency: LRU storage eviction
# ---------------------------------------------------------------------------

class TestStorageEviction:
    def test_lru_eviction_respects_cap(self):
        store = Storage()
        # Override cap for the test
        original_cap = settings.MAX_STORAGE_DOCS
        settings.MAX_STORAGE_DOCS = 3

        from app.pdf_parser import ProcessedPDF, PageData

        def _make_pdf_obj(doc_id: str) -> ProcessedPDF:
            return ProcessedPDF(
                doc_id=doc_id,
                filename=f"{doc_id}.pdf",
                pages=[PageData(1, "Sample text for testing purposes here.")],
                raw_bytes=_make_pdf(),
            )

        for i in range(5):
            store.save_pdf(_make_pdf_obj(f"doc-{i}"))

        # After inserting 5 docs with cap=3, only the 3 most recent should remain
        assert store.doc_count == 3
        assert store.get_pdf("doc-0") is None  # evicted
        assert store.get_pdf("doc-1") is None  # evicted
        assert store.get_pdf("doc-4") is not None  # retained

        # Restore
        settings.MAX_STORAGE_DOCS = original_cap

    def test_remove_decrements_count(self):
        store = Storage()
        from app.pdf_parser import ProcessedPDF, PageData
        pdf = ProcessedPDF("rm-test", "rm.pdf", [PageData(1, "Test content text here.")], _make_pdf())
        store.save_pdf(pdf)
        assert store.doc_count == 1
        store.remove("rm-test")
        assert store.doc_count == 0
