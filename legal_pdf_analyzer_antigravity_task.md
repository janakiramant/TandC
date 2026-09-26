# Antigravity One-Time Build Task — Legal PDF Analyzer AI

## Mission

Build a complete, runnable, tested MVP web application called **Legal PDF Analyzer AI** based strictly on the requirements in this file.

The goal is a simple but polished GenAI application for the challenge theme **AI for Legal Assistance & Access**.

The application must help a user understand one uploaded legal PDF, ask questions about it, identify positive/favorable points, concerns/risks, and important clauses, and connect every AI finding back to its source location in the original PDF.

This is a **single-document MVP**. Do not expand the scope with unrelated features.

---

## 1. Non-Negotiable Product Scope

Build exactly these core capabilities:

1. Upload one PDF using drag-and-drop and file selection.
2. Extract readable text from the PDF.
3. Analyze the document with an LLM.
4. Generate:
   - a concise document summary;
   - favorable/positive points;
   - concerns/risks;
   - important clauses;
   - source references for every finding.
5. Provide a chat window where the user can ask questions about the uploaded document.
6. Answers must be grounded in the uploaded document, not generic legal speculation.
7. Every useful AI finding or chat answer must expose a source reference such as page number and section/clause when available.
8. Clicking a finding or source reference must navigate the PDF viewer to the referenced page.
9. When feasible, visually highlight the referenced text in the PDF. If exact text-coordinate highlighting is not reliable for a given PDF, page-level navigation must still work correctly.
10. The PDF viewer must support:
    - page navigation;
    - zoom in;
    - zoom out;
    - readable scrolling.
11. Show a clear legal-information disclaimer that the application is not a substitute for professional legal advice.

---

## 2. Explicitly Out of Scope

Do NOT implement these unless they are required internally to make the core MVP work:

- multiple-document workflows;
- contract-to-contract comparison;
- lawyer marketplace or lawyer matching;
- legal case prediction;
- legal outcome prediction;
- legal web search engine;
- external legal database integration;
- voice input/output;
- mobile application;
- user authentication;
- payment system;
- user profiles;
- admin dashboard;
- model training or fine-tuning;
- autonomous agents;
- complex multi-agent workflows;
- unnecessary microservices;
- unnecessary cloud infrastructure;
- unrelated analytics dashboards.

Do not add features merely because they sound impressive.

---

## 3. Target User Experience

The main application screen must be divided into **three functional columns/panels**.

### Left panel — Upload + Chat

Top section:

- application title/branding;
- drag-and-drop PDF area;
- browse/select PDF button;
- selected filename and basic status;
- upload/processing state;
- clear/reset document option.

Bottom section:

- chat conversation area;
- input placeholder:
  **"Anything particular to check in the document?"**
- send button;
- loading state while the AI is answering.

### Middle panel — AI Analysis

Show:

1. Document summary.
2. Favorable / positive points.
3. Concerns / risks.
4. Important clauses.

Each item must be clickable.

Every item should show enough source information to understand where it came from, for example:

- Page 7
- Section 8.2
- Clause 12.3

When a user clicks an item, the PDF viewer on the right must navigate to the corresponding source.

### Right panel — PDF Viewer

Display the uploaded PDF directly in the application.

Required controls:

- previous/next page;
- current page indicator;
- zoom out;
- zoom in;
- fit/readable view where practical;
- scrolling.

When an analysis item or chat answer source is selected:

- jump to the referenced page;
- attempt exact text highlighting when technically reliable;
- otherwise use page navigation and clearly identify the referenced clause/text.

---

## 4. Recommended Technical Direction

Use the simplest reliable architecture that can be completed and tested end-to-end.

Preferred baseline:

### Frontend

- React
- TypeScript if practical
- clean component-based UI

### Backend

- Python
- FastAPI

### Document processing

Use a reliable PDF text extraction library such as PyMuPDF or an equivalent stable option.

### AI

Use a production-ready hosted LLM API through an environment variable for the API key.

Do NOT hardcode secrets.

### Retrieval

For the MVP, choose the simplest reliable grounding strategy based on actual document size and model context limits.

- For small documents, direct structured analysis may be sufficient.
- For larger documents or chat retrieval, use chunking + embeddings/vector retrieval (RAG).

Do not add a vector database unless it materially improves reliability or is needed for the chosen approach.

### PDF viewer

Use a mature React-compatible PDF viewing solution rather than writing a PDF renderer from scratch.

The exact library may be chosen by the implementation agent based on compatibility and reliability.

---

## 5. Core AI Behavior

The AI must be instructed to analyze **only the uploaded document content** for document-specific claims.

It must not invent clauses, page numbers, section numbers, penalties, obligations, rights, or facts that are not supported by the document.

For every generated finding, capture structured metadata such as:

```json
{
  "type": "risk",
  "title": "90-day notice period",
  "summary": "The agreement requires a 90-day notice period for termination by the employee.",
  "page": 7,
  "section": "8.2",
  "source_text": "...exact relevant text from the document..."
}
```

The exact schema may be improved during implementation, but these concepts are required:

- finding type;
- human-readable title;
- concise explanation;
- page reference;
- section/clause reference when available;
- source text or evidence where practical.

Use structured JSON output from the model whenever the selected model/API supports reliable structured output.

---

## 6. Definitions for Findings

Do not force every legal point into a simplistic good/bad judgment.

Use these categories:

### Favorable / Positive

Facts or provisions that may reasonably be viewed as favorable from the user's document-review perspective, while keeping the wording descriptive and grounded.

### Concerns / Risks

Clauses or provisions that may deserve attention, such as:

- unusually long notice periods;
- termination conditions;
- financial penalties;
- automatic renewal;
- restrictive obligations;
- deadlines;
- broad confidentiality obligations;
- unusual responsibility/liability language;
- inconsistent wording.

The system must describe the actual clause and why it may deserve attention rather than making unsupported legal conclusions.

### Important Clauses

Clauses that a user should reasonably know about, even when they are not inherently positive or negative.

Examples:

- termination;
- notice period;
- payment;
- confidentiality;
- intellectual property;
- renewal;
- dispute resolution;
- governing law;
- obligations/deadlines.

Do not claim that a clause is legally invalid, illegal, enforceable, or unenforceable unless the application has authoritative legal support for that claim.

---

## 7. Chat Requirements

The chat must answer questions about the uploaded PDF.

Example questions:

- "What is the notice period?"
- "Is there any termination penalty?"
- "What are my major obligations?"
- "Is there an automatic renewal clause?"
- "What should I review carefully?"

Chat answers should follow this pattern where applicable:

1. direct answer;
2. concise explanation;
3. source reference;
4. clickable "View source" behavior.

Example:

> Yes. The agreement requires a 60-day notice period.
>
> Source: Section 8.2, Page 7.
>
> [View source]

If the answer cannot be established from the uploaded document, the system must say so clearly instead of guessing.

Example:

> The uploaded document does not provide enough information to answer that question.

If a question asks for legal advice rather than document interpretation, provide document-grounded information and recommend consulting a qualified legal professional when appropriate.

---

## 8. Source Linking Requirements

This is a critical feature and must be treated as a primary acceptance criterion.

Create a consistent source-reference model connecting:

**AI finding/chat answer -> page -> source text/section -> PDF viewer**

At minimum:

- clicking an analysis item navigates to the correct page;
- clicking a chat source navigates to the correct page;
- current selected finding is visually indicated in the middle panel;
- PDF viewer visibly changes to the correct page;
- if exact highlighting is implemented, it must correspond to the cited source text.

Never fabricate page references.

If extraction makes page tracking ambiguous, preserve page boundaries during text extraction so references remain traceable.

---

## 9. PDF Processing Requirements

Support normal text-based PDFs first.

On upload:

1. validate file type;
2. safely parse the PDF;
3. preserve page boundaries;
4. extract text per page;
5. reject or clearly report invalid/corrupted PDFs;
6. show processing progress/status;
7. analyze only after successful extraction.

If a PDF contains no extractable text because it is scanned/image-only, do NOT hallucinate content.

Show a clear message such as:

> This PDF does not contain readable text. Text extraction/OCR is not available for this document in the current version.

OCR may be added only if it is simple and reliable enough for the implementation timeframe.

---

## 10. UI/UX Requirements

Keep the UI simple, professional, and focused.

Prioritize readability over decorative design.

Required states:

- initial/empty state;
- drag-over upload state;
- uploading/processing state;
- analysis loading state;
- chat loading state;
- successful analysis state;
- invalid PDF/error state;
- API/configuration error state;
- empty results state.

Do not create a complicated navigation system.

The application should work well on a normal desktop/laptop screen because the primary use case is the three-panel document-review workflow.

---

## 11. Legal Safety and Trust Requirements

Display a visible disclaimer such as:

> This tool provides general information based on the uploaded document and is not a substitute for professional legal advice. Consult a qualified legal professional for advice specific to your situation.

The AI must:

- distinguish document facts from interpretation;
- avoid pretending to be a lawyer;
- avoid unsupported legal conclusions;
- avoid invented citations;
- avoid invented sections/pages;
- say when information is missing or uncertain.

Do not use wording that implies the application guarantees legal correctness.

---

## 12. Backend/API Design

Keep the API small and practical.

A reasonable API may include:

- upload/analyze PDF;
- retrieve analysis result;
- ask a question about the active document;
- retrieve or resolve a source reference if needed.

Do not build an unnecessary API surface.

The backend should return structured data rather than UI-specific HTML.

Add validation for:

- file type;
- file size;
- malformed input;
- missing API key/configuration;
- LLM failures;
- extraction failures;
- timeout/error handling.

---

## 13. Environment and Secrets

Use environment variables for all secrets/configuration that may differ by environment.

At minimum:

- LLM API key;
- model name where applicable;
- backend/frontend configuration values when needed.

Provide a safe `.env.example` file.

Never commit actual secrets.

---

## 14. Error Handling

The system must fail clearly rather than hallucinate or silently continue.

Examples:

### LLM unavailable

Show a user-friendly message that analysis could not be completed.

### PDF extraction failed

Tell the user that the document could not be read.

### Question not answerable from document

Explicitly state that the document does not contain enough information.

### Unsupported PDF

Explain the limitation.

### Invalid AI response

Validate structured output. Do not render malformed or invented data.

Implement reasonable retries only where safe and useful.

Do not create infinite retry loops.

---

## 15. Testing Strategy

Testing is mandatory. Do not stop after the application appears to run.

Create and execute tests for at least:

### Backend

- PDF upload validation;
- text extraction;
- page boundary preservation;
- structured AI response validation;
- source/page reference integrity;
- chat handling;
- missing-answer behavior;
- invalid PDF behavior.

### Frontend

Test at minimum:

- upload interaction;
- analysis rendering;
- clicking an analysis finding;
- PDF page navigation;
- zoom controls;
- chat submission;
- chat source navigation;
- loading/error states.

### End-to-end

Perform at least one real end-to-end test with a representative legal-style PDF:

1. upload PDF;
2. wait for analysis;
3. confirm summary is displayed;
4. confirm findings are displayed;
5. click a finding;
6. verify PDF changes to the expected page;
7. ask a document question;
8. verify grounded answer;
9. click chat source;
10. verify PDF navigation;
11. verify zoom controls.

Do not mark the application complete based only on unit tests.

---

## 16. Self-Debugging and Rebuild Loop

Operate as an implementation agent, not as a planning-only assistant.

Follow this loop:

1. Inspect the existing project/repository before changing anything.
2. Build the smallest complete implementation.
3. Run the application.
4. Run automated tests.
5. Perform end-to-end validation.
6. If anything fails, inspect the actual error/log/output.
7. Fix the root cause.
8. Re-run the failed test and relevant surrounding tests.
9. Re-run end-to-end validation after significant fixes.
10. Continue until the application satisfies the acceptance criteria.

Do not claim success based on assumptions.

Do not say something works unless it has been tested or verified by inspecting the actual result.

Do not invent missing library behavior, API responses, file formats, or framework features.

When uncertain about an implementation detail, inspect the installed project/dependencies, official documentation available to the environment, or the actual runtime behavior before deciding.

Do not replace working code with speculative rewrites.

---

## 17. Anti-Hallucination Development Rules

These rules apply to both the AI functionality and the implementation process.

### During coding

- Never assume a dependency is installed.
- Verify package versions and APIs actually available in the project.
- Never invent file paths.
- Never invent environment variables that are not documented.
- Never claim a test passed without running it.
- Never claim a UI behavior works without testing it.
- Do not hide errors merely to make the build appear successful.

### During AI analysis

- Never invent facts not present in the PDF.
- Never invent page numbers.
- Never invent clause numbers.
- Never invent quotations.
- Never infer legal conclusions without evidence.
- If evidence is missing, explicitly say so.

---

## 18. Data Flow

Implement a clear flow similar to:

```text
PDF Upload
   ↓
PDF Validation
   ↓
Page-by-page Text Extraction
   ↓
Document Representation
   ↓
AI Analysis
   ↓
Structured Findings
   ├── Summary
   ├── Favorable Points
   ├── Concerns/Risks
   └── Important Clauses
          ↓
      Source References
          ↓
      React UI
          ↓
   Click Finding / Source
          ↓
      PDF Viewer
          ↓
     Page Navigation
```

Chat:

```text
User Question
      ↓
Retrieve relevant document content
      ↓
LLM
      ↓
Grounded answer + source reference
      ↓
Chat UI
      ↓
View Source
      ↓
PDF Viewer
```

---

## 19. Initial Analysis Prompt Requirements

Design the internal analysis prompt so that the model is explicitly told:

- the input is a legal document;
- the objective is document understanding and issue spotting, not legal representation;
- use only supplied document content for document-specific facts;
- return structured findings;
- provide page and clause references only when supported;
- quote or extract only the relevant source text needed to justify a finding;
- distinguish favorable points, concerns, and important clauses;
- do not invent missing information;
- state uncertainty when appropriate.

The actual production prompt should be stored in the project in a maintainable configuration/module rather than hidden inside scattered code.

---

## 20. Chat Prompt Requirements

The chat system prompt must tell the model:

- answer questions using the uploaded document context;
- prioritize retrieved/source text over general knowledge;
- cite page and clause references where supported;
- never fabricate document content;
- if the answer is not supported by the document, say that it cannot be determined from the uploaded document;
- provide concise answers;
- do not present itself as a lawyer;
- mention professional legal advice when the user is asking for individualized legal advice rather than document explanation.

---

## 21. Representative Test Document

Create or use a safe synthetic/sample legal-style document for testing if no suitable test PDF exists.

Do NOT depend on a real person's confidential legal document for automated testing.

The test document should contain enough variety to validate:

- summary;
- obligations;
- notice period;
- termination;
- renewal;
- payment/financial language;
- confidentiality;
- at least one potentially concerning clause;
- clearly identifiable page references.

Do not fabricate real legal authority or present the sample as actual legal advice.

---

## 22. Final Acceptance Criteria

The project is complete only when all of the following are true:

### Upload

- [ ] User can drag and drop a PDF.
- [ ] User can select a PDF through a file chooser.
- [ ] Invalid file type is rejected clearly.
- [ ] Processing status is visible.

### AI Analysis

- [ ] Summary appears after successful processing.
- [ ] Favorable/positive points appear.
- [ ] Concerns/risks appear.
- [ ] Important clauses appear.
- [ ] Findings are grounded in the document.
- [ ] Findings contain valid source references.

### Chat

- [ ] Placeholder exactly or closely follows: "Anything particular to check in the document?"
- [ ] User can submit a question.
- [ ] Response is grounded in the PDF.
- [ ] Unsupported questions do not cause hallucinated answers.
- [ ] Response can link to its source.

### PDF Viewer

- [ ] PDF is visible in the third panel.
- [ ] Page navigation works.
- [ ] Zoom in works.
- [ ] Zoom out works.
- [ ] Clicking an analysis finding navigates to the relevant page.
- [ ] Clicking a chat source navigates to the relevant page.
- [ ] Exact text highlighting works when reliable, or page-level source navigation works consistently.

### Reliability

- [ ] Backend tests pass.
- [ ] Frontend tests pass.
- [ ] End-to-end test passes.
- [ ] No known blocking errors remain.
- [ ] No secrets are hardcoded.
- [ ] Error states are handled clearly.
- [ ] The application can be started using the documented project instructions.

### Legal safety

- [ ] Legal-information disclaimer is visible.
- [ ] No unsupported legal conclusions are presented as facts.
- [ ] No fabricated source/page/section references exist in tested flows.

---

## 23. Final Deliverable Requirements

At completion, provide a concise project summary containing only verified information:

1. what was built;
2. technology actually used;
3. how to configure the required AI API key;
4. how to run frontend/backend;
5. tests executed and their results;
6. known limitations that genuinely remain.

Do not claim that unsupported features exist.

Do not hide known failures.

Do not leave placeholder TODOs for any feature listed as a mandatory acceptance criterion.

The final state must be a **working, tested Legal PDF Analyzer AI MVP**, not a prototype mockup.

---

## 24. Final Instruction to the Implementation Agent

Treat this entire file as the task specification.

Build the application end-to-end.

Make reasonable implementation decisions without asking for unnecessary clarification.

Keep the solution intentionally simple.

Prioritize:

**working upload -> grounded AI analysis -> clickable findings -> source-linked PDF navigation -> grounded chat**

over additional features.

Test the real application, fix the actual problems you encounter, and only finish when the acceptance criteria are met as far as the environment permits.
