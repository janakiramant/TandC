import io
import fitz
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_mock_pdf_bytes() -> bytes:
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 50), "MASTER SERVICES AGREEMENT\n1. Payment Terms\nInvoices due in 30 days.")
    p2 = doc.new_page()
    p2.insert_text((50, 50), "4. Automatic Renewal\nTerm renews automatically for 12 months unless 90 days notice given.")
    b = doc.tobytes()
    doc.close()
    return b

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "ok"
    assert "service" in json_data

def test_upload_valid_pdf():
    pdf_bytes = create_mock_pdf_bytes()
    files = {"file": ("test_agreement.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "doc_id" in data
    assert data["filename"] == "test_agreement.pdf"
    assert data["total_pages"] == 2
    assert data["has_readable_text"] is True
    assert "analysis" in data
    assert len(data["analysis"]["findings"]) > 0

def test_upload_invalid_file_extension():
    files = {"file": ("invalid_file.txt", io.BytesIO(b"Hello world"), "text/plain")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_chat_endpoint():
    pdf_bytes = create_mock_pdf_bytes()
    files = {"file": ("agreement.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    upload_res = client.post("/api/upload", files=files)
    doc_id = upload_res.json()["doc_id"]

    chat_res = client.post("/api/chat", json={"doc_id": doc_id, "question": "What is the automatic renewal notice period?"})
    assert chat_res.status_code == 200
    data = chat_res.json()
    assert "answer" in data
    assert len(data["sources"]) > 0

def test_get_document_file():
    pdf_bytes = create_mock_pdf_bytes()
    files = {"file": ("agreement.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    upload_res = client.post("/api/upload", files=files)
    doc_id = upload_res.json()["doc_id"]

    file_res = client.get(f"/api/document/{doc_id}/file")
    assert file_res.status_code == 200
    assert file_res.headers["content-type"] == "application/pdf"
    assert len(file_res.content) > 0
