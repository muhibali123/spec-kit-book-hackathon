import React from 'react';
import './ErrorMessage.css';

interface ErrorMessageProps {
  message: string;
  onRetry?: (() => void) | null;
  onDismiss?: (() => void) | null;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry = null, onDismiss = null }) => {
  return (
    <div className="error-message" role="alert">
      <div className="error-content">
        <div className="error-icon" aria-hidden="true">⚠️</div>
        <div className="error-text">{message}</div>
      </div>
      <div className="error-actions">
        {onRetry && (
          <button
            className="error-retry-button"
            onClick={onRetry}
            aria-label="Retry the last action"
          >
            Retry
          </button>
        )}
        {onDismiss && (
          <button
            className="error-dismiss-button"
            onClick={onDismiss}
            aria-label="Dismiss this error message"
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;