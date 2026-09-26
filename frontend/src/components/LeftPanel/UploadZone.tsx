import React, { useRef, useState } from 'react';
import { UploadCloud, FileCheck, RefreshCw, AlertCircle, Loader2 } from 'lucide-react';
import type { UploadResponse } from '../../types';

interface UploadZoneProps {
  onFileSelected: (file: File) => void;
  isProcessing: boolean;
  activeDoc: UploadResponse | null;
  onClearDocument: () => void;
  errorMessage?: string | null;
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  onFileSelected,
  isProcessing,
  activeDoc,
  onClearDocument,
  errorMessage,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
        onFileSelected(file);
      } else {
        alert('Invalid file format. Please upload a PDF document (.pdf).');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelected(e.target.files[0]);
    }
  };

  const triggerFileBrowser = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
      fileInputRef.current.click();
    }
  };

  /** Allow keyboard users to activate the drop zone with Enter/Space */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isProcessing && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      triggerFileBrowser();
    }
  };

  return (
    <div className="upload-section-card">
      <div className="section-title" aria-hidden="true">
        <span>Document Upload</span>
      </div>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="application/pdf,.pdf"
        className="hidden-file-input"
        style={{ display: 'none' }}
        aria-label="Upload PDF document"
        tabIndex={-1}
      />

      {activeDoc ? (
        <div
          className="active-doc-banner"
          role="status"
          aria-label={`Document loaded: ${activeDoc.filename}, ${activeDoc.total_pages} pages`}
        >
          <div className="doc-info-row">
            <FileCheck className="icon-success" size={20} aria-hidden="true" />
            <div className="doc-details">
              <span className="doc-filename">{activeDoc.filename}</span>
              <span className="doc-meta">
                {activeDoc.total_pages} Page{activeDoc.total_pages > 1 ? 's' : ''} • Grounded Analysis Ready
              </span>
            </div>
          </div>
          <button
            onClick={onClearDocument}
            className="btn-reset-doc"
            aria-label="Clear document and upload a new one"
          >
            <RefreshCw size={14} aria-hidden="true" /> Clear / Reset
          </button>
        </div>
      ) : (
        <div
          className={`drop-zone ${isDragOver ? 'drag-over' : ''} ${isProcessing ? 'disabled' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={!isProcessing ? triggerFileBrowser : undefined}
          onKeyDown={handleKeyDown}
          role="button"
          tabIndex={isProcessing ? -1 : 0}
          aria-label="Upload PDF: drag and drop a file here or press Enter to browse"
          aria-disabled={isProcessing}
        >
          {isProcessing ? (
            <div className="upload-state-loading" aria-live="polite" aria-busy="true">
              <Loader2 size={32} className="spinner-icon" aria-hidden="true" />
              <p className="loading-text">Parsing &amp; Analyzing PDF...</p>
              <span className="loading-sub">Extracting text &amp; identifying key clauses</span>
            </div>
          ) : (
            <div className="upload-state-idle">
              <UploadCloud size={36} className="upload-icon" aria-hidden="true" />
              <p className="upload-prompt">
                Drag &amp; drop legal PDF here or <span className="browse-link">Browse files</span>
              </p>
              <span className="upload-hint">Supports text-based legal contracts, agreements, &amp; terms</span>
            </div>
          )}
        </div>
      )}

      {errorMessage && (
        <div
          className="upload-error-alert"
          role="alert"
          aria-live="assertive"
        >
          <AlertCircle size={16} aria-hidden="true" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
};
