import React from 'react';
import './LoadingIndicator.css';

interface LoadingIndicatorProps {
  message?: string;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ message = 'Thinking...' }) => {
  return (
    <div className="loading-indicator" role="status" aria-live="polite">
      <div className="loading-content">
        <div className="loading-spinner" aria-hidden="true"></div>
        <span className="loading-text">{message}</span>
      </div>
    </div>
  );
};

export default LoadingIndicator;