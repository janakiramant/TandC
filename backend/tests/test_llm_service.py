import pytest
import fitz
from app.pdf_parser import parse_pdf_bytes
from app.llm_service import analyze_document_with_llm, answer_chat_with_llm

@pytest.mark.asyncio
async def test_analyze_document():
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 50), "Section 8.2 Notice Period\nEither party may terminate this agreement upon 90 days written notice.")
    p2 = doc.new_page()
    p2.insert_text((50, 50), "Section 12.1 Governing Law\nThis agreement is governed by the laws of Delaware.")
    pdf_bytes = doc.tobytes()
    doc.close()

    pdf = parse_pdf_bytes("doc-llm-1", "contract.pdf", pdf_bytes)
    analysis = await analyze_document_with_llm(pdf)

    assert analysis.doc_id == "doc-llm-1"
    assert len(analysis.findings) > 0
    assert any(f.page == 1 for f in analysis.findings)
    assert any(f.type in ["risk", "favorable", "important"] for f in analysis.findings)


@pytest.mark.asyncio
async def test_chat_grounded_question():
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 50), "Section 8.2 Notice Period\nThe required notice period for termination is 90 days.")
    pdf_bytes = doc.tobytes()
    doc.close()

    pdf = parse_pdf_bytes("doc-llm-2", "contract.pdf", pdf_bytes)

    res = await answer_chat_with_llm(pdf, "What is the notice period?")
    assert res.is_grounded is True
    assert "90 days" in res.answer.lower() or "notice" in res.answer.lower()
    assert len(res.sources) > 0
    assert res.sources[0].page == 1


@pytest.mark.asyncio
async def test_chat_unsupported_question():
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 50), "This agreement covers software development fees of $10,000.")
    pdf_bytes = doc.tobytes()
    doc.close()

    pdf = parse_pdf_bytes("doc-llm-3", "contract.pdf", pdf_bytes)

    res = await answer_chat_with_llm(pdf, "What is the penalty for late pet grooming?")
    assert "not provide enough information" in res.answer or res.is_grounded is False
