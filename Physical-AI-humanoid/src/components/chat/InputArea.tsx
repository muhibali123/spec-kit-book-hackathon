import React, { useState, useRef, useEffect } from 'react';
import validationService from './services/validation';
import './InputArea.css';

interface InputAreaProps {
  onSendMessage: (message: string) => void;
  loading?: boolean;
}

const InputArea: React.FC<InputAreaProps> = ({ onSendMessage, loading = false }) => {
  const [inputValue, setInputValue] = useState<string>('');
  const [error, setError] = useState<string>('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 150) + 'px';
    }
  }, [inputValue]);

  // Handle input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setInputValue(value);

    // Clear error when user starts typing
    if (error) {
      setError('');
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage();
  };

  // Send message function
  const sendMessage = () => {
    // Don't send if already loading or input is empty
    if (loading || !inputValue.trim()) {
      return;
    }

    // Validate input
    const validation = validationService.validateInput(inputValue);

    if (!validation.isValid) {
      setError(validation.errors[0]); // Show the first error
      return;
    }

    // If valid, send the message
    onSendMessage(inputValue);

    // Clear input and error
    setInputValue('');
    setError('');
  };

  // Handle key down for Enter key submission
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift for new line)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
    // Allow Shift+Enter for new line
  };

  return (
    <div className="input-area">
      <form onSubmit={handleSubmit} className="input-form" role="form">
        <div className="input-container">
          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about the content..."
            aria-label="Enter your question"
            className={`question-input ${error ? 'input-error' : ''}`}
            disabled={loading}
            rows={1}
            aria-describedby={error ? "input-error-message" : undefined}
          />
          <button
            type="submit"
            onClick={sendMessage}
            disabled={loading || !inputValue.trim()}
            className={`submit-button ${loading ? 'button-loading' : ''}`}
            aria-label={loading ? 'Sending message, please wait' : 'Send message'}
          >
            {loading ? (
              <>
                <span className="button-spinner" aria-hidden="true"></span>
                Sending...
              </>
            ) : 'Send'}
          </button>
        </div>

        {error && (
          <div id="input-error-message" className="input-error-message" role="alert" aria-live="assertive">
            {error}
          </div>
        )}
      </form>
    </div>
  );
};

export default InputArea;