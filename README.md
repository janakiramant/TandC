# Legal PDF Analyzer AI

A full-stack GenAI web application built for **AI for Legal Assistance & Access**. It enables users to upload a legal PDF, view automated structured analysis (Summary, Favorable Terms, Risks/Concerns, Important Clauses), chat with an AI assistant grounded strictly in the document, and jump directly to source citations in an embedded PDF viewer.

---

## Architecture Overview

- **Frontend**: React (Vite, TypeScript), Lucide React Icons, PDF.js (`pdfjs-dist`) rendering canvas viewer.
- **Backend**: Python FastAPI, PyMuPDF (`fitz`) text extractor, Pydantic schema validation.
- **AI Engine**: Hosted LLM API (Google Gemini API `gemini-2.5-flash` or OpenAI API) with an intelligent local fallback grounding engine.

---

## Key Features

1. **Three-Panel Review Interface**:
   - **Left Panel**: Drag & Drop PDF Uploader + Grounded Document Chat Q&A.
   - **Middle Panel**: Executive Summary + Categorized Findings (Favorable, Risks, Important Clauses).
   - **Right Panel**: Interactive PDF Canvas Viewer with Page Navigation, Zoom, and Source Text Highlighting.
2. **Source Linking & Citation Navigation**:
   - Clicking any AI analysis item or chat source badge automatically scrolls and jumps the PDF viewer to the exact cited page.
3. **Legal Information Disclaimer**:
   - Clear banner stating the tool provides general information and is not a substitute for professional legal advice.

---

## Quick Start Guide

### 1. Environment Setup & Configuration

Copy `.env.example` to `.env` and insert your Gemini API Key:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
LLM_MODEL=gemini-2.5-flash
PORT=8000
HOST=0.0.0.0
```

### 2. Run Backend Server

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run FastAPI backend
python backend/run.py
```
Backend will start on `http://localhost:8000`. API documentation available at `http://localhost:8000/docs`.

### 3. Run Frontend Application

```bash
cd frontend
npm install
npm run dev
```
Frontend will start on `http://localhost:5173`.

---

## Running Automated Tests

```bash
# Run pytest backend test suite (unit + E2E integration)
$env:PYTHONPATH="backend"; .\venv\Scripts\python.exe -m pytest backend/tests/ -v

# Run frontend TypeScript & bundle check
cd frontend
npm run build
```

---

## Test Sample Document

A synthetic representative test PDF is included at:
`backend/sample_docs/sample_service_agreement.pdf`

To regenerate:
```bash
.\venv\Scripts\python.exe backend/sample_docs/generate_sample_pdf.py
```
