import React, { useState } from 'react';
import Citation from './Citation';
import formattingService from './services/formatting';
import { Citation as CitationType } from './types';
import './AIMessage.css';

interface AIMessageProps {
  content: string;
  citations?: CitationType[];
  timestamp?: string | Date;
}

const AIMessage: React.FC<AIMessageProps> = ({ content, citations = [], timestamp }) => {
  // Format the timestamp for display
  const formatTimestamp = (timestamp: string | Date | undefined): string => {
    if (!timestamp) return '';

    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const [showSourcesModal, setShowSourcesModal] = useState(false);

  const openSourcesModal = () => {
    setShowSourcesModal(true);
  };

  const closeSourcesModal = () => {
    setShowSourcesModal(false);
  };

  return (
    <div className="message ai" role="listitem" aria-label="AI response">
      <div className="message-header">
        <span className="ai-label" aria-hidden="true">🤖</span>
        <span className="ai-label-text" aria-hidden="true">AI Assistant</span>
      </div>
      <div
        className="message-content"
        aria-label="AI response content"
        dangerouslySetInnerHTML={{ __html: formattingService.formatResponse(content) }}
      />
      {citations && citations.length > 0 && (
        <div className="citations" aria-label="Supporting citations">
          <button
            className="toggle-sources"
            onClick={openSourcesModal}
            aria-label="View sources"
          >
            Sources ({citations.length})
          </button>
        </div>
      )}
      {timestamp && (
        <div className="message-timestamp" aria-label="Message timestamp">
          {formatTimestamp(timestamp)}
        </div>
      )}

      {/* Sources Modal */}
      {showSourcesModal && (
        <div className="sources-modal" onClick={closeSourcesModal}>
          <div className="sources-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="sources-modal-header">
              <h3 className="sources-modal-title">Sources</h3>
              <button className="sources-modal-close" onClick={closeSourcesModal} aria-label="Close sources">
                ×
              </button>
            </div>
            <div className="sources-list">
              {citations.map((citation, index) => (
                <Citation
                  key={citation.id || `citation-${index}`}
                  citation={citation}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIMessage;