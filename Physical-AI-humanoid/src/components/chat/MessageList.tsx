import React, { useMemo } from 'react';
import { Message as MessageType } from './types';
import UserMessage from './UserMessage';
import AIMessage from './AIMessage';
import './MessageList.css';

interface MessageListProps {
  messages?: MessageType[];
}

const MessageList: React.FC<MessageListProps> = ({ messages = [] }) => {
  // Memoize the message components to prevent unnecessary re-renders
  const messageElements = useMemo(() => {
    return messages.map((message, index) => {
      if (message.role === 'user') {
        return (
          <UserMessage
            key={message.id}
            content={message.content}
            timestamp={message.timestamp}
          />
        );
      } else if (message.role === 'assistant') {
        return (
          <AIMessage
            key={message.id}
            content={message.content}
            citations={message.citations || []}
            timestamp={message.timestamp}
          />
        );
      }
      return null;
    });
  }, [messages]);

  return (
    <div
      className="message-history"
      aria-live="polite"
      aria-atomic="true"
      role="log"
      aria-label="Conversation history"
    >
      {messageElements}
    </div>
  );
};

export default MessageList;