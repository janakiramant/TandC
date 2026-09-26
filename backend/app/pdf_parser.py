import fitz  # PyMuPDF
import re
from typing import List, Dict, Any, Optional

SECTION_REGEX = re.compile(
    r'(?:(?:Section|Clause|Article|Paragraph)\s+([0-9A-Z\.]+)|(?:\b[0-9]{1,2}\.[0-9]{1,2}(?:\.[0-9]{1,2})?\b))\s*[:\.\-–—]?\s*([^\n\r]+)?',
    re.IGNORECASE
)

class PageData:
    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text.strip()
        self.sections = self._extract_sections(self.text)

    def _extract_sections(self, text: str) -> List[str]:
        found = []
        for match in SECTION_REGEX.finditer(text):
            sec_num = match.group(1) or match.group(0).split()[0]
            sec_title = match.group(2) or ""
            ref = f"Section {sec_num}".strip()
            if sec_title:
                ref += f" ({sec_title.strip()[:40]})"
            if ref not in found:
                found.append(ref)
        return found

class ProcessedPDF:
    def __init__(self, doc_id: str, filename: str, pages: List[PageData], raw_bytes: bytes):
        self.doc_id = doc_id
        self.filename = filename
        self.pages = pages
        self.raw_bytes = raw_bytes
        self.total_pages = len(pages)
        self.total_chars = sum(len(p.text) for p in pages)
        self.has_readable_text = self.total_chars >= 30

    def get_full_text(self) -> str:
        formatted = []
        for p in self.pages:
            formatted.append(f"--- PAGE {p.page_number} ---\n{p.text}")
        return "\n\n".join(formatted)

def parse_pdf_bytes(doc_id: str, filename: str, file_bytes: bytes) -> ProcessedPDF:
    """Parses raw PDF bytes using PyMuPDF and extracts page-level text."""
    if not file_bytes or len(file_bytes) == 0:
        raise ValueError("Uploaded file is empty.")

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"Failed to parse PDF document. Invalid or corrupted file format. Detail: {str(e)}")

    if doc.page_count == 0:
        raise ValueError("PDF document contains 0 pages.")

    pages: List[PageData] = []
    for idx in range(doc.page_count):
        page = doc.load_page(idx)
        text = page.get_text("text") or ""
        pages.append(PageData(page_number=idx + 1, text=text))

    doc.close()

    return ProcessedPDF(
        doc_id=doc_id,
        filename=filename,
        pages=pages,
        raw_bytes=file_bytes
    )
