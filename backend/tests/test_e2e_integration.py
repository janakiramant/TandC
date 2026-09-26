import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_end_to_end_flow():
    sample_pdf_path = os.path.join(os.path.dirname(__file__), "..", "sample_docs", "sample_service_agreement.pdf")
    assert os.path.exists(sample_pdf_path), "Sample PDF must exist for E2E integration testing"

    with open(sample_pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Step 1: Upload PDF
    files = {"file": ("sample_service_agreement.pdf", pdf_bytes, "application/pdf")}
    upload_resp = client.post("/api/upload", files=files)
    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()

    doc_id = upload_data["doc_id"]
    assert doc_id is not None
    assert upload_data["total_pages"] == 3
    assert upload_data["has_readable_text"] is True

    # Step 2: Validate AI Analysis
    analysis = upload_data["analysis"]
    assert analysis["doc_id"] == doc_id
    assert len(analysis["summary"]) > 0
    findings = analysis["findings"]
    assert len(findings) > 0

    # Verify findings contain page numbers, titles, and sources
    risk_findings = [f for f in findings if f["type"] == "risk"]
    favorable_findings = [f for f in findings if f["type"] == "favorable"]
    important_findings = [f for f in findings if f["type"] == "important"]

    assert len(risk_findings) + len(favorable_findings) + len(important_findings) == len(findings)

    for finding in findings:
        assert finding["page"] in [1, 2, 3]
        assert len(finding["title"]) > 0
        assert len(finding["summary"]) > 0
        assert len(finding["source_text"]) > 0

    # Step 3: Grounded Chat Question 1 - Notice period
    chat_resp1 = client.post("/api/chat", json={
        "doc_id": doc_id,
        "question": "What is the notice period for non-renewal?"
    })
    assert chat_resp1.status_code == 200
    chat_data1 = chat_resp1.json()
    assert chat_data1["is_grounded"] is True
    assert len(chat_data1["sources"]) > 0
    assert any(s["page"] in [2, 3] for s in chat_data1["sources"])

    # Step 4: Grounded Chat Question 2 - Unsupported question
    chat_resp2 = client.post("/api/chat", json={
        "doc_id": doc_id,
        "question": "What is the policy for employee remote work stipends?"
    })
    assert chat_resp2.status_code == 200
    chat_data2 = chat_resp2.json()
    assert "not provide enough information" in chat_data2["answer"].lower() or chat_data2["is_grounded"] is False

    # Step 5: PDF stream download verification
    file_resp = client.get(f"/api/document/{doc_id}/file")
    assert file_resp.status_code == 200
    assert len(file_resp.content) == len(pdf_bytes)
