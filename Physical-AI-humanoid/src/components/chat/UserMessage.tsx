import React from 'react';
import './UserMessage.css';

interface UserMessageProps {
  content: string;
  timestamp?: string | Date;
}

const UserMessage: React.FC<UserMessageProps> = ({ content, timestamp }) => {
  // Format the timestamp for display
  const formatTimestamp = (timestamp: string | Date | undefined): string => {
    if (!timestamp) return '';

    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="message user" role="listitem" aria-label="User message">
      <div className="message-header">
        <span className="user-label" aria-hidden="true">You</span>
      </div>
      <div className="message-content" aria-label="Message content">
        {content}
      </div>
      {timestamp && (
        <div className="message-timestamp" aria-label="Message timestamp">
          {formatTimestamp(timestamp)}
        </div>
      )}
    </div>
  );
};

export default UserMessage;