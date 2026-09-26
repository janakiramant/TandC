import React, { useState } from 'react';
import type { DocumentAnalysis, Finding, FindingType } from '../../types';
import { FindingCard } from './FindingCard';
import { Sparkles, Filter, Search, FileText, CheckCircle2, ShieldAlert, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';

interface AnalysisDashboardProps {
  analysis: DocumentAnalysis | null;
  selectedFindingId: string | null;
  onSelectFinding: (finding: Finding) => void;
  isLoading: boolean;
}

export const AnalysisDashboard: React.FC<AnalysisDashboardProps> = ({
  analysis,
  selectedFindingId,
  onSelectFinding,
  isLoading,
}) => {
  const [activeTab, setActiveTab] = useState<'all' | FindingType>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isSummaryExpanded, setIsSummaryExpanded] = useState(false);

  if (isLoading) {
    return (
      <div className="middle-panel-loading">
        <div className="analysis-skeleton">
          <div className="skeleton-title"></div>
          <div className="skeleton-line"></div>
          <div className="skeleton-line short"></div>
          <div className="skeleton-cards">
            <div className="skeleton-card"></div>
            <div className="skeleton-card"></div>
            <div className="skeleton-card"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="middle-panel-empty">
        <BookOpen size={44} className="empty-panel-icon" />
        <h3>AI Analysis Dashboard</h3>
        <p>Upload a legal PDF document on the left panel to automatically extract summary, favorable terms, risk concerns, and clause locations.</p>
      </div>
    );
  }

  const counts = {
    all: analysis.findings.length,
    favorable: analysis.findings.filter((f) => f.type === 'favorable').length,
    risk: analysis.findings.filter((f) => f.type === 'risk').length,
    important: analysis.findings.filter((f) => f.type === 'important').length,
  };

  const filteredFindings = analysis.findings.filter((f) => {
    const matchesTab = activeTab === 'all' || f.type === activeTab;
    const matchesSearch =
      !searchTerm.trim() ||
      f.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (f.source_text && f.source_text.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (f.section && f.section.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesTab && matchesSearch;
  });

  const isLongSummary = analysis.summary && analysis.summary.length > 240;

  return (
    <div className="analysis-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="title-group">
          <Sparkles className="sparkle-icon" size={18} />
          <h2>AI Document Analysis</h2>
        </div>
        <span className="analysis-badge">Grounded Extraction</span>
      </div>

      {/* Compact Executive Summary */}
      <div className="summary-card">
        <div className="summary-header-row">
          <div className="summary-title-row">
            <FileText size={15} className="summary-icon" />
            <h3>Document Executive Summary</h3>
          </div>
          {isLongSummary && (
            <button
              onClick={() => setIsSummaryExpanded(!isSummaryExpanded)}
              className="btn-toggle-summary"
            >
              {isSummaryExpanded ? (
                <>Less <ChevronUp size={12} /></>
              ) : (
                <>More <ChevronDown size={12} /></>
              )}
            </button>
          )}
        </div>
        <p className={`summary-text ${!isSummaryExpanded && isLongSummary ? 'summary-clamped' : ''}`}>
          {analysis.summary}
        </p>
      </div>

      {/* Filter Tabs & Search Controls */}
      <div className="controls-bar">
        <div className="category-tabs">
          <button
            className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => setActiveTab('all')}
          >
            All ({counts.all})
          </button>
          <button
            className={`tab-btn tab-favorable ${activeTab === 'favorable' ? 'active' : ''}`}
            onClick={() => setActiveTab('favorable')}
          >
            <CheckCircle2 size={13} />
            Favorable ({counts.favorable})
          </button>
          <button
            className={`tab-btn tab-risk ${activeTab === 'risk' ? 'active' : ''}`}
            onClick={() => setActiveTab('risk')}
          >
            <ShieldAlert size={13} />
            Concerns ({counts.risk})
          </button>
          <button
            className={`tab-btn tab-important ${activeTab === 'important' ? 'active' : ''}`}
            onClick={() => setActiveTab('important')}
          >
            <FileText size={13} />
            Clauses ({counts.important})
          </button>
        </div>

        <div className="search-box">
          <Search size={14} className="search-icon" />
          <input
            type="text"
            placeholder="Search findings..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Main Single Scroll Findings List */}
      <div className="findings-scroll-container">
        {filteredFindings.length === 0 ? (
          <div className="no-findings">
            <Filter size={24} />
            <p>No findings matching the selected filter.</p>
          </div>
        ) : (
          filteredFindings.map((finding) => (
            <FindingCard
              key={finding.id}
              finding={finding}
              isActive={selectedFindingId === finding.id}
              onSelect={onSelectFinding}
            />
          ))
        )}
      </div>
    </div>
  );
};
