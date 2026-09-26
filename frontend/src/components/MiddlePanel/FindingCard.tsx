import React from 'react';
import { ShieldAlert, CheckCircle2, FileText, ArrowRight } from 'lucide-react';
import type { Finding } from '../../types';

interface FindingCardProps {
  finding: Finding;
  isActive: boolean;
  onSelect: (finding: Finding) => void;
}

export const FindingCard: React.FC<FindingCardProps> = ({
  finding,
  isActive,
  onSelect,
}) => {
  const getCategoryConfig = (type: Finding['type']) => {
    switch (type) {
      case 'risk':
        return {
          label: 'Concern / Risk',
          icon: <ShieldAlert size={13} aria-hidden="true" />,
          badgeClass: 'badge-risk',
          cardClass: 'card-risk',
        };
      case 'favorable':
        return {
          label: 'Favorable Point',
          icon: <CheckCircle2 size={13} aria-hidden="true" />,
          badgeClass: 'badge-favorable',
          cardClass: 'card-favorable',
        };
      case 'important':
      default:
        return {
          label: 'Important Clause',
          icon: <FileText size={13} aria-hidden="true" />,
          badgeClass: 'badge-important',
          cardClass: 'card-important',
        };
    }
  };

  const config = getCategoryConfig(finding.type);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSelect(finding);
    }
  };

  return (
    <div
      className={`finding-card ${config.cardClass} ${isActive ? 'active' : ''}`}
      onClick={() => onSelect(finding)}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-pressed={isActive}
      aria-label={`${config.label}: ${finding.title}, page ${finding.page}${finding.section ? `, ${finding.section}` : ''}`}
    >
      <div className="card-top-row">
        <span className={`finding-type-badge ${config.badgeClass}`} aria-hidden="true">
          {config.icon}
          <span>{config.label}</span>
        </span>
        <span className="source-location-tag" aria-hidden="true">
          <span>Page {finding.page}{finding.section ? ` • ${finding.section}` : ''}</span>
          <ArrowRight size={13} className="arrow-icon" aria-hidden="true" />
        </span>
      </div>

      <h4 className="finding-title">{finding.title}</h4>
      <p className="finding-summary">{finding.summary}</p>

      {finding.section && (
        <div className="source-section-info">
          <span className="source-section-label">Source:</span> {finding.section}
        </div>
      )}

      {finding.source_text && (
        <blockquote className="source-quote-box">
          <span className="quote-label">Excerpt:</span> &quot;{finding.source_text}&quot;
        </blockquote>
      )}
    </div>
  );
};
