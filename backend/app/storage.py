from typing import Dict, Optional
from app.pdf_parser import ProcessedPDF
from app.schemas import DocumentAnalysis

class Storage:
    def __init__(self):
        self._pdfs: Dict[str, ProcessedPDF] = {}
        self._analyses: Dict[str, DocumentAnalysis] = {}

    def save_pdf(self, pdf: ProcessedPDF):
        self._pdfs[pdf.doc_id] = pdf

    def get_pdf(self, doc_id: str) -> Optional[ProcessedPDF]:
        return self._pdfs.get(doc_id)

    def save_analysis(self, analysis: DocumentAnalysis):
        self._analyses[analysis.doc_id] = analysis

    def get_analysis(self, doc_id: str) -> Optional[DocumentAnalysis]:
        return self._analyses.get(doc_id)

    def clear(self):
        self._pdfs.clear()
        self._analyses.clear()

    def remove(self, doc_id: str):
        """Remove a single document and its analysis by ID."""
        self._pdfs.pop(doc_id, None)
        self._analyses.pop(doc_id, None)

storage = Storage()
