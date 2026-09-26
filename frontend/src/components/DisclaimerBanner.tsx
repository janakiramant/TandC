import React, { useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';

export const DisclaimerBanner: React.FC = () => {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div className="disclaimer-banner">
      <div className="disclaimer-content">
        <AlertTriangle size={18} className="disclaimer-icon" />
        <p className="disclaimer-text">
          <strong>Legal Information Disclaimer:</strong> This tool provides general information based on the uploaded document and is not a substitute for professional legal advice. Consult a qualified legal professional for advice specific to your situation.
        </p>
      </div>
      <button 
        onClick={() => setDismissed(true)} 
        className="btn-dismiss-disclaimer" 
        title="Dismiss notice"
        aria-label="Dismiss disclaimer"
      >
        <X size={16} />
      </button>
    </div>
  );
};
