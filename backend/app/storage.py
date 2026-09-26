from collections import OrderedDict
from typing import Optional
from app.pdf_parser import ProcessedPDF
from app.schemas import DocumentAnalysis
from app.config import settings


class Storage:
    """In-memory document store with LRU-style eviction capped at MAX_STORAGE_DOCS."""

    def __init__(self):
        self._pdfs: OrderedDict[str, ProcessedPDF] = OrderedDict()
        self._analyses: OrderedDict[str, DocumentAnalysis] = OrderedDict()

    def _evict_if_needed(self) -> None:
        """Remove the oldest document when storage exceeds the configured cap."""
        while len(self._pdfs) > settings.MAX_STORAGE_DOCS:
            oldest_id, _ = self._pdfs.popitem(last=False)
            self._analyses.pop(oldest_id, None)

    def save_pdf(self, pdf: ProcessedPDF) -> None:
        # Move to end if already stored (refresh recency)
        if pdf.doc_id in self._pdfs:
            self._pdfs.move_to_end(pdf.doc_id)
        self._pdfs[pdf.doc_id] = pdf
        self._evict_if_needed()

    def get_pdf(self, doc_id: str) -> Optional[ProcessedPDF]:
        if doc_id in self._pdfs:
            self._pdfs.move_to_end(doc_id)  # refresh recency on access
        return self._pdfs.get(doc_id)

    def save_analysis(self, analysis: DocumentAnalysis) -> None:
        if analysis.doc_id in self._analyses:
            self._analyses.move_to_end(analysis.doc_id)
        self._analyses[analysis.doc_id] = analysis

    def get_analysis(self, doc_id: str) -> Optional[DocumentAnalysis]:
        return self._analyses.get(doc_id)

    def clear(self) -> None:
        self._pdfs.clear()
        self._analyses.clear()

    def remove(self, doc_id: str) -> None:
        """Remove a single document and its analysis by ID."""
        self._pdfs.pop(doc_id, None)
        self._analyses.pop(doc_id, None)

    @property
    def doc_count(self) -> int:
        return len(self._pdfs)


storage = Storage()
