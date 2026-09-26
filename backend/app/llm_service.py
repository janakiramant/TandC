import json
import re
import uuid
import logging
from typing import List, Dict, Any, Optional
import httpx

from app.config import settings
from app.schemas import DocumentAnalysis, Finding, ChatResponse, ChatSource
from app.pdf_parser import ProcessedPDF, PageData
from app.prompts import SYSTEM_ANALYSIS_PROMPT, SYSTEM_CHAT_PROMPT

logger = logging.getLogger("legal_pdf_analyzer.llm")


async def analyze_document_with_llm(pdf: ProcessedPDF) -> DocumentAnalysis:
    """Analyzes document pages with LLM (Gemini or OpenAI) or fallback rule engine."""

    if not pdf.has_readable_text:
        return DocumentAnalysis(
            doc_id=pdf.doc_id,
            filename=pdf.filename,
            total_pages=pdf.total_pages,
            summary="This PDF does not contain readable text. Text extraction/OCR is not available for this document in the current version.",
            findings=[],
            created_at="",
            has_readable_text=False,
            error_message="This PDF does not contain readable text. Text extraction/OCR is not available for this document in the current version."
        )

    # 1. Try Gemini API if key exists
    if settings.GEMINI_API_KEY:
        try:
            result = await _call_gemini_analysis(pdf)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Gemini API analysis failed, falling back to local extractor: {e}")

    # 2. Try OpenAI API if key exists
    if settings.OPENAI_API_KEY:
        try:
            result = await _call_openai_analysis(pdf)
            if result:
                return result
        except Exception as e:
            logger.warning(f"OpenAI API analysis failed, falling back to local extractor: {e}")

    # 3. Fallback: Intelligent Local Rule Engine
    return _local_rule_based_analysis(pdf)


async def answer_chat_with_llm(pdf: ProcessedPDF, question: str) -> ChatResponse:
    """Answers user question grounded in the document using LLM or local search engine."""

    if not pdf.has_readable_text:
        return ChatResponse(
            answer="This PDF does not contain readable text. Chat cannot answer questions for scanned/empty documents.",
            sources=[],
            is_grounded=False
        )

    # 1. Try Gemini API if key exists
    if settings.GEMINI_API_KEY:
        try:
            res = await _call_gemini_chat(pdf, question)
            if res:
                return res
        except Exception as e:
            logger.warning(f"Gemini API chat failed, falling back to local QA: {e}")

    # 2. Try OpenAI API if key exists
    if settings.OPENAI_API_KEY:
        try:
            res = await _call_openai_chat(pdf, question)
            if res:
                return res
        except Exception as e:
            logger.warning(f"OpenAI API chat failed, falling back to local QA: {e}")

    # 3. Fallback: Local Grounded Search Engine
    return _local_rule_based_chat(pdf, question)


# ==========================================
# Gemini API Integration
# ==========================================

async def _call_gemini_analysis(pdf: ProcessedPDF) -> Optional[DocumentAnalysis]:
    full_text = pdf.get_full_text()
    prompt = f"{SYSTEM_ANALYSIS_PROMPT}\n\nDOCUMENT CONTENT:\n{full_text}"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code != 200:
            logger.error(f"Gemini API error {resp.status_code}: {resp.text}")
            return None

        data = resp.json()
        raw_text = data['candidates'][0]['content']['parts'][0]['text']
        parsed = json.loads(raw_text)

        findings = []
        for i, f in enumerate(parsed.get("findings", [])):
            findings.append(
                Finding(
                    id=f.get("id", f"finding-{i+1}"),
                    type=f.get("type", "important"),
                    title=f.get("title", "Clause Note"),
                    summary=f.get("summary", ""),
                    page=int(f.get("page", 1)),
                    section=f.get("section"),
                    source_text=f.get("source_text", "")
                )
            )

        return DocumentAnalysis(
            doc_id=pdf.doc_id,
            filename=pdf.filename,
            total_pages=pdf.total_pages,
            summary=parsed.get("summary", "Document analysis complete."),
            findings=findings,
            created_at="",
            has_readable_text=True
        )


async def _call_gemini_chat(pdf: ProcessedPDF, question: str) -> Optional[ChatResponse]:
    # Retrieve top 4 relevant page contexts
    relevant_pages = _search_relevant_pages(pdf, question)
    context_text = "\n\n".join([f"PAGE {p.page_number}:\n{p.text}" for p in relevant_pages])

    prompt = f"{SYSTEM_CHAT_PROMPT}\n\nDOCUMENT EXCERPTS:\n{context_text}\n\nUSER QUESTION: {question}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code != 200:
            return None

        data = resp.json()
        raw_text = data['candidates'][0]['content']['parts'][0]['text']
        parsed = json.loads(raw_text)

        sources = []
        for s in parsed.get("sources", []):
            sources.append(
                ChatSource(
                    page=int(s.get("page", 1)),
                    section=s.get("section"),
                    snippet=s.get("snippet", "")
                )
            )

        return ChatResponse(
            answer=parsed.get("answer", "No answer available."),
            sources=sources,
            is_grounded=parsed.get("is_grounded", True)
        )


# ==========================================
# OpenAI API Integration
# ==========================================

async def _call_openai_analysis(pdf: ProcessedPDF) -> Optional[DocumentAnalysis]:
    full_text = pdf.get_full_text()
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_ANALYSIS_PROMPT},
            {"role": "user", "content": full_text}
        ],
        "response_format": {"type": "json_object"}
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code != 200:
            return None

        data = resp.json()
        raw_text = data["choices"][0]["message"]["content"]
        parsed = json.loads(raw_text)

        findings = [
            Finding(
                id=f.get("id", f"finding-{i+1}"),
                type=f.get("type", "important"),
                title=f.get("title", "Clause Note"),
                summary=f.get("summary", ""),
                page=int(f.get("page", 1)),
                section=f.get("section"),
                source_text=f.get("source_text", "")
            )
            for i, f in enumerate(parsed.get("findings", []))
        ]

        return DocumentAnalysis(
            doc_id=pdf.doc_id,
            filename=pdf.filename,
            total_pages=pdf.total_pages,
            summary=parsed.get("summary", "Document summary."),
            findings=findings,
            created_at="",
            has_readable_text=True
        )


async def _call_openai_chat(pdf: ProcessedPDF, question: str) -> Optional[ChatResponse]:
    relevant_pages = _search_relevant_pages(pdf, question)
    context_text = "\n\n".join([f"PAGE {p.page_number}:\n{p.text}" for p in relevant_pages])

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_CHAT_PROMPT},
            {"role": "user", "content": f"EXCERPTS:\n{context_text}\n\nQUESTION: {question}"}
        ],
        "response_format": {"type": "json_object"}
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code != 200:
            return None

        data = resp.json()
        raw_text = data["choices"][0]["message"]["content"]
        parsed = json.loads(raw_text)

        sources = [
            ChatSource(
                page=int(s.get("page", 1)),
                section=s.get("section"),
                snippet=s.get("snippet", "")
            )
            for s in parsed.get("sources", [])
        ]

        return ChatResponse(
            answer=parsed.get("answer", ""),
            sources=sources,
            is_grounded=parsed.get("is_grounded", True)
        )


# ==========================================
# Local Rule Engine (Fallback & Test Grounding)
# ==========================================

def _local_rule_based_analysis(pdf: ProcessedPDF) -> DocumentAnalysis:
    """Intelligent fallback analysis when no API key is set."""
    findings: List[Finding] = []

    # Legal clause patterns
    patterns = [
        # Risk / Concerns
        ("risk", r"(notice period|terminate|termination|penalty|damages|indemnification|non-compete|automatic renewal|renew automatically|late payment|interest|liability cap|unilateral)", "Concern / Risk Item"),
        # Favorable
        ("favorable", r"(intellectual property|ownership|warrant|warrants|confidential|reimburse|grace period|cure period|mutually|right to inspect|non-exclusive license)", "Favorable Provision"),
        # Important
        ("important", r"(governing law|jurisdiction|dispute resolution|arbitration|payment terms|compensation|fee|fees|confidentiality|term and termination|scope of work)", "Important Clause")
    ]

    finding_counter = 1
    seen_titles = set()

    for p in pdf.pages:
        lines = [line.strip() for line in p.text.split('\n') if len(line.strip()) > 10]
        
        for line in lines:
            for category, regex, default_label in patterns:
                match = re.search(regex, line, re.IGNORECASE)
                if match:
                    matched_term = match.group(0).title()
                    sec_ref = p.sections[0] if p.sections else None
                    
                    title = f"{matched_term} Provision"
                    if title in seen_titles:
                        continue
                    seen_titles.add(title)

                    # Extract snippet context around line
                    snippet = line[:200]
                    
                    summary_desc = _generate_clause_summary(category, matched_term, line)

                    findings.append(
                        Finding(
                            id=f"finding-{finding_counter}",
                            type=category,
                            title=title,
                            summary=summary_desc,
                            page=p.page_number,
                            section=sec_ref,
                            source_text=snippet
                        )
                    )
                    finding_counter += 1
                    break

    # If no findings detected by regex, generate default page-level findings
    if not findings:
        for p in pdf.pages:
            sec_ref = p.sections[0] if p.sections else f"Page {p.page_number}"
            snippet = p.text[:150] if p.text else "Document excerpt."
            findings.append(
                Finding(
                    id=f"finding-{finding_counter}",
                    type="important",
                    title=f"General Provision (Page {p.page_number})",
                    summary=f"Key terms and obligations documented on page {p.page_number}.",
                    page=p.page_number,
                    section=sec_ref,
                    source_text=snippet
                )
            )
            finding_counter += 1

    # Generate document summary
    first_page_text = pdf.pages[0].text[:300].replace('\n', ' ') if pdf.pages else ""
    summary_text = (
        f"This document is '{pdf.filename}' containing {pdf.total_pages} page(s). "
        f"Key provisions identified include {len([f for f in findings if f.type == 'risk'])} risks/concerns, "
        f"{len([f for f in findings if f.type == 'favorable'])} favorable terms, and "
        f"{len([f for f in findings if f.type == 'important'])} standard clauses.\n\n"
        f"Excerpt overview: {first_page_text}..."
    )

    return DocumentAnalysis(
        doc_id=pdf.doc_id,
        filename=pdf.filename,
        total_pages=pdf.total_pages,
        summary=summary_text,
        findings=findings,
        created_at="",
        has_readable_text=True
    )


def _generate_clause_summary(category: str, term: str, sentence: str) -> str:
    if category == "risk":
        return f"Provisions regarding '{term}' require attention: {sentence[:120]}..."
    elif category == "favorable":
        return f"Advantageous terms regarding '{term}' documented: {sentence[:120]}..."
    else:
        return f"Standard clause regulating '{term}': {sentence[:120]}..."


def _local_rule_based_chat(pdf: ProcessedPDF, question: str) -> ChatResponse:
    # Stop words to filter out common query framing words
    stop_words = {
        "what", "where", "when", "which", "who", "how", "why", "is", "are", "was", "were", "be", "been", "being",
        "the", "a", "an", "for", "with", "does", "do", "did", "have", "has", "had", "any", "policy", "there",
        "mentioned", "document", "agreement", "contract", "clause", "section", "stated", "specified", "provided",
        "according", "about", "this", "that", "in", "on", "at", "to", "from", "by", "of"
    }
    q_words = [w.lower() for w in re.findall(r'\w+', question) if len(w) > 2 and w.lower() not in stop_words]

    if not q_words:
        return ChatResponse(
            answer="Information requested is not specified or found in the uploaded document.",
            sources=[],
            is_grounded=False
        )

    matching_snippets = []

    for p in pdf.pages:
        sentences = re.split(r'[\.\n]+', p.text)
        for s in sentences:
            s_clean = s.strip()
            if not s_clean or len(s_clean) < 12:
                continue
            s_lower = s_clean.lower()

            matches = sum(1 for w in q_words if w in s_lower)
            if matches > 0:
                sec = p.sections[0] if p.sections else f"Page {p.page_number}"
                matching_snippets.append((matches, p.page_number, sec, s_clean))

    if not matching_snippets:
        return ChatResponse(
            answer="The requested information was not found in the uploaded document.",
            sources=[],
            is_grounded=False
        )

    matching_snippets.sort(key=lambda x: x[0], reverse=True)
    top_matches = matching_snippets[:3]

    answer_parts = []
    sources = []

    for _, p_num, sec, snippet in top_matches:
        answer_parts.append(f"• On Page {p_num} ({sec}): \"{snippet}\"")
        sources.append(
            ChatSource(
                page=p_num,
                section=sec,
                snippet=snippet
            )
        )

    direct_answer = (
        f"Based on the uploaded document:\n" + "\n".join(answer_parts)
    )

    return ChatResponse(
        answer=direct_answer,
        sources=sources,
        is_grounded=True
    )


def _search_relevant_pages(pdf: ProcessedPDF, question: str) -> List[PageData]:
    q_words = [w.lower() for w in re.findall(r'\w+', question) if len(w) > 3]
    scored_pages = []

    for p in pdf.pages:
        score = sum(1 for w in q_words if w in p.text.lower())
        scored_pages.append((score, p))

    scored_pages.sort(key=lambda x: x[0], reverse=True)
    return [p for score, p in scored_pages[:4]]
