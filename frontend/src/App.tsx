import React, { useState } from 'react';
import { Header } from './components/Header';
import { DisclaimerBanner } from './components/DisclaimerBanner';
import { UploadZone } from './components/LeftPanel/UploadZone';
import { ChatSection } from './components/LeftPanel/ChatSection';
import { AnalysisDashboard } from './components/MiddlePanel/AnalysisDashboard';
import { PdfViewer } from './components/RightPanel/PdfViewer';
import type { UploadResponse, Finding, ChatMessage } from './types';
import { uploadPdfDocument, sendChatMessage, getPdfFileUrl, clearDocumentSession } from './services/api';

export const App: React.FC = () => {
  const [activeDoc, setActiveDoc] = useState<UploadResponse | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [selectedFindingId, setSelectedFindingId] = useState<string | null>(null);
  const [targetPage, setTargetPage] = useState<number>(1);
  const [highlightText, setHighlightText] = useState<string>('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isChatLoading, setIsChatLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const pdfUrl = activeDoc?.doc_id ? getPdfFileUrl(activeDoc.doc_id) : null;

  const handleFileSelected = async (file: File) => {
    setIsProcessing(true);
    setErrorMessage(null);
    setSelectedFindingId(null);
    setTargetPage(1);

    try {
      const res = await uploadPdfDocument(file);
      setActiveDoc(res);
      setIsProcessing(false);

      if (!res.has_readable_text) {
        setErrorMessage("This PDF does not contain readable text. Text extraction/OCR is not available for this document in the current version.");
      } else {
        // Initial AI chat introduction
        setChatMessages([
          {
            id: 'welcome-1',
            sender: 'ai',
            text: `Analysis complete for "${res.filename}". Ask any specific question about notice periods, obligations, penalties, or termination clauses below!`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            is_grounded: true,
          },
        ]);
      }
    } catch (err: any) {
      console.error('File upload failed:', err);
      setErrorMessage(err.message || 'Failed to upload and analyze PDF document.');
      setIsProcessing(false);
    }
  };

  const handleClearDocument = async () => {
    if (activeDoc?.doc_id) {
      await clearDocumentSession(activeDoc.doc_id);
    }
    setActiveDoc(null);
    setSelectedFindingId(null);
    setTargetPage(1);
    setHighlightText('');
    setChatMessages([]);
    setErrorMessage(null);
  };

  const handleSelectFinding = (finding: Finding) => {
    setSelectedFindingId(finding.id);
    setTargetPage(finding.page);
    setHighlightText(finding.source_text || '');
  };

  const handleSendMessage = async (question: string) => {
    if (!activeDoc?.doc_id) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: question,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setChatMessages((prev) => [...prev, userMsg]);
    setIsChatLoading(true);

    try {
      const res = await sendChatMessage(activeDoc.doc_id, question);
      const aiMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        sender: 'ai',
        text: res.answer,
        sources: res.sources,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        is_grounded: res.is_grounded,
      };

      setChatMessages((prev) => [...prev, aiMsg]);
      setIsChatLoading(false);
    } catch (err: any) {
      console.error('Chat error:', err);
      const errorMsg: ChatMessage = {
        id: `ai-err-${Date.now()}`,
        sender: 'ai',
        text: 'Sorry, an error occurred while processing your question. Please try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        is_grounded: false,
      };
      setChatMessages((prev) => [...prev, errorMsg]);
      setIsChatLoading(false);
    }
  };

  const handleNavigateToPage = (page: number, textSnippet?: string) => {
    setTargetPage(page);
    if (textSnippet) {
      setHighlightText(textSnippet);
    }
  };

  return (
    <div className="app-container">
      <Header
        filename={activeDoc?.filename}
        totalPages={activeDoc?.total_pages}
      />

      <DisclaimerBanner />

      {/* Screen-reader live region for status messages */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        id="app-status-live-region"
      >
        {isProcessing ? 'Parsing and analyzing PDF document, please wait…' : ''}
        {errorMessage ? `Error: ${errorMessage}` : ''}
      </div>

      <main id="main-content" className="three-panel-layout" aria-label="Document analysis workspace">
        {/* Left Panel: Upload + Chat */}
        <section className="panel panel-left" aria-label="Document upload and chat">
          <UploadZone
            onFileSelected={handleFileSelected}
            isProcessing={isProcessing}
            activeDoc={activeDoc}
            onClearDocument={handleClearDocument}
            errorMessage={errorMessage}
          />
          <ChatSection
            messages={chatMessages}
            onSendMessage={handleSendMessage}
            isLoading={isChatLoading}
            onNavigateToPage={handleNavigateToPage}
            isDisabled={!activeDoc || !activeDoc.has_readable_text}
            onClearChat={() => setChatMessages([])}
          />
        </section>

        {/* Middle Panel: AI Analysis */}
        <section className="panel panel-middle" aria-label="AI analysis results">
          <AnalysisDashboard
            analysis={activeDoc?.analysis || null}
            selectedFindingId={selectedFindingId}
            onSelectFinding={handleSelectFinding}
            isLoading={isProcessing}
          />
        </section>

        {/* Right Panel: PDF Viewer */}
        <section className="panel panel-right" aria-label="PDF document viewer">
          <PdfViewer
            pdfUrl={pdfUrl}
            targetPage={targetPage}
            highlightText={highlightText}
            onPageChange={(p) => setTargetPage(p)}
          />
        </section>
      </main>
    </div>
  );
};

export default App;
