import pytest
import fitz
from app.pdf_parser import parse_pdf_bytes, ProcessedPDF

def test_parse_valid_pdf():
    # Create simple 2-page test PDF in memory
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 50), "Section 1.1 Scope of Work\nThis is page 1 of the test agreement.")
    p2 = doc.new_page()
    p2.insert_text((50, 50), "Section 8.2 Notice Period\nNotice must be given 60 days prior to termination.")
    
    pdf_bytes = doc.tobytes()
    doc.close()

    result = parse_pdf_bytes("doc-test-1", "test.pdf", pdf_bytes)

    assert result.doc_id == "doc-test-1"
    assert result.filename == "test.pdf"
    assert result.total_pages == 2
    assert result.has_readable_text is True
    assert "Section 1.1 Scope of Work" in result.pages[0].text
    assert result.pages[0].page_number == 1
    assert result.pages[1].page_number == 2


def test_parse_empty_pdf_bytes():
    with pytest.raises(ValueError, match="empty"):
        parse_pdf_bytes("doc-test-2", "empty.pdf", b"")


def test_parse_corrupted_pdf_bytes():
    with pytest.raises(ValueError, match="Failed to parse PDF"):
        parse_pdf_bytes("doc-test-3", "corrupted.pdf", b"NOT_A_PDF_CONTENT_HEADER")


def test_parse_scanned_image_pdf():
    # PDF with no text
    doc = fitz.open()
    doc.new_page()
    pdf_bytes = doc.tobytes()
    doc.close()

    result = parse_pdf_bytes("doc-test-4", "scanned.pdf", pdf_bytes)
    assert result.total_pages == 1
    assert result.has_readable_text is False
