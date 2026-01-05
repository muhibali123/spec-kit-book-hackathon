import React from 'react';
import { Citation as CitationType } from './types';
import './Citation.css';

interface CitationProps {
  citation: CitationType;
  [key: string]: any; // For additional aria props
}

const Citation: React.FC<CitationProps> = ({ citation, ...ariaProps }) => {
  return (
    <div className="citation" role="listitem" {...ariaProps}>
      <div className="citation-source">
        <strong>{citation.source}</strong>
        {citation.page !== undefined && citation.page !== null && <span>, Page {citation.page}</span>}
        {citation.section && <span>, Section: {citation.section}</span>}
      </div>
      {citation.content && (
        <div className="citation-content" aria-label="Citation content">
          "{citation.content}"
        </div>
      )}
      {citation.url && (
        <a
          href={citation.url}
          className="citation-link"
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`Link to source: ${citation.source}`}
        >
          View Source
        </a>
      )}
    </div>
  );
};

export default Citation;