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

  return (
    <div className="upload-section-card">
      <div className="section-title">
        <span>Document Upload</span>
      </div>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="application/pdf,.pdf"
        className="hidden-file-input"
        style={{ display: 'none' }}
      />

      {activeDoc ? (
        <div className="active-doc-banner">
          <div className="doc-info-row">
            <FileCheck className="icon-success" size={20} />
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
            title="Clear and upload new document"
          >
            <RefreshCw size={14} /> Clear / Reset
          </button>
        </div>
      ) : (
        <div
          className={`drop-zone ${isDragOver ? 'drag-over' : ''} ${isProcessing ? 'disabled' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={!isProcessing ? triggerFileBrowser : undefined}
        >
          {isProcessing ? (
            <div className="upload-state-loading">
              <Loader2 size={32} className="spinner-icon" />
              <p className="loading-text">Parsing & Analyzing PDF...</p>
              <span className="loading-sub">Extracting text & identifying key clauses</span>
            </div>
          ) : (
            <div className="upload-state-idle">
              <UploadCloud size={36} className="upload-icon" />
              <p className="upload-prompt">
                Drag & drop legal PDF here or <span className="browse-link">Browse files</span>
              </p>
              <span className="upload-hint">Supports text-based legal contracts, agreements, & terms</span>
            </div>
          )}
        </div>
      )}

      {errorMessage && (
        <div className="upload-error-alert">
          <AlertCircle size={16} />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
};
