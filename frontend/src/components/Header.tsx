import React from 'react';
import { Scale, FileText } from 'lucide-react';

interface HeaderProps {
  filename?: string;
  totalPages?: number;
}

export const Header: React.FC<HeaderProps> = ({ filename, totalPages }) => {
  return (
    <header className="app-header">
      <div className="header-brand">
        <div className="brand-logo">
          <Scale className="logo-icon" size={24} />
        </div>
        <div className="brand-titles">
          <h1>Legal PDF Analyzer <span className="highlight-ai">AI</span></h1>
          <span className="badge-theme">AI Legal Assistance</span>
        </div>
      </div>

      {filename && (
        <div className="header-doc-status">
          <FileText size={16} className="doc-icon" />
          <span className="doc-name">{filename}</span>
          {totalPages && <span className="doc-pages">{totalPages} page{totalPages > 1 ? 's' : ''}</span>}
        </div>
      )}
    </header>
  );
};
