import React, { useState, useEffect, useRef } from 'react';
import { useStore } from './state/hooks';
import MessageList from './MessageList';
import InputArea from './InputArea';
import LoadingIndicator from './LoadingIndicator';
import ErrorMessage from './ErrorMessage';
import ApiClient from './ApiClient';
import { Message } from './models/Message';
import { Message as MessageType } from './types';
import errorService from './services/error';
import './ChatContainer.css';

interface ChatState {
  session: any;
  activeConversation: any;
  loading: boolean;
  error: string | null;
  apiConnected: boolean;
}

const ChatContainer: React.FC = () => {
  const [state, store] = useStore();
  const [inputValue, setInputValue] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const apiClient = new ApiClient();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [state.activeConversation?.messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Ensure an active conversation exists when the component mounts
  useEffect(() => {
    if (!state.activeConversation) {
      store.createNewConversation();
    }
  }, [state.activeConversation, store]);

  // Handle sending a message
  const handleSendMessage = async (messageText: string) => {
    console.log('handleSendMessage called with:', messageText);
    console.log('Current state.activeConversation:', state.activeConversation);

    // Ensure there's an active conversation before sending
    if (!state.activeConversation) {
      console.log('No active conversation, creating one');
      store.createNewConversation();
    }

    // Add user message to the conversation immediately
    const userMessage = new Message({
      content: messageText,
      role: 'user',
      timestamp: new Date()
    });

    console.log('Created user message:', userMessage);

    // Add the user's message to the store immediately
    const addedMessage = store.addMessageToActiveConversation(userMessage);
    console.log('Added message to store:', addedMessage);
    console.log('Active conversation after adding user message:', state.activeConversation);

    try {
      // Show loading state
      store.setLoading(true);
      console.log('Set loading to true');

      // Submit query to API
      const response = await apiClient.submitQuery(
        messageText,
        state.activeConversation?.id
      );
      console.log('API response received:', response);

      // Extract the AI answer from the response
      // The response should now have an 'answer' field as per AnswerResponse
      let aiContent = response.answer || 'No answer generated for your query.';

      // If the response doesn't have the expected format, fall back to the old format
      if (!response.answer && response.results && response.results.length > 0) {
        // Fallback for old format
        aiContent = response.results[0].text;
      }

      // Create citations from the response
      const citations = response.citations ? response.citations.map((citation, index) => ({
        id: citation.source_id || citation.id || `citation-${index}`,
        source: citation.source_title || citation.source || 'Unknown source',
        content: citation.excerpt || citation.content || '',
        url: citation.url || undefined,
        documentId: citation.source_id || citation.id || `doc-${index}`,
        source_id: citation.source_id || citation.id || `source-${index}`,
        excerpt: citation.excerpt || citation.content || '',
        relevance_score: citation.relevance_score || citation.score || 0.5
      })) : response.results ? response.results.map((chunk, index) => ({
        id: chunk.id,
        source: chunk.source || 'Unknown source',
        content: chunk.text,
        url: chunk.metadata?.url || undefined,
        documentId: chunk.id,
        source_id: chunk.id,
        excerpt: chunk.text,
        relevance_score: chunk.score
      })) : [];

      const aiMessage = new Message({
        content: aiContent,
        role: 'assistant',  // Use 'assistant' to match the updated type definition
        timestamp: new Date(),
        citations: citations
      });
      console.log('Created AI message:', aiMessage);

      // Add the AI's response to the store
      const addedAIMessage = store.addMessageToActiveConversation(aiMessage);
      console.log('Added AI message to store:', addedAIMessage);
      console.log('Active conversation after adding AI message:', state.activeConversation);
    } catch (err: any) {
      console.error('Error sending message:', err);
      const userFriendlyError = errorService.mapError(err);
      store.setError(userFriendlyError);
      setError(userFriendlyError);
    } finally {
      store.setLoading(false);
      console.log('Set loading to false');
    }
  };

  // Handle retry action
  const handleRetry = async () => {
    if (inputValue.trim()) {
      setError(null);
      await handleSendMessage(inputValue);
    }
  };

  // Handle dismiss error
  const handleDismissError = () => {
    setError(null);
    store.clearError();
  };

  return (
    <div className="chat-container" role="main" aria-label="AI Knowledge Assistant Chat Interface">
      <header className="chat-header" role="banner">
        <h1 id="chat-title">AI Knowledge Assistant</h1>
        <p>Ask questions and get answers from our knowledge base</p>
      </header>

      <main className="chat-main" role="main" aria-labelledby="chat-title">
        <div
          id="message-history"
          className="message-history-container"
          aria-live={state.loading ? "polite" : "assertive"}
          aria-relevant="additions text"
        >
          <MessageList messages={state.activeConversation?.messages || []} />

          {/* Scroll anchor for auto-scrolling */}
          <div ref={messagesEndRef} />

          {state.loading && (
            <LoadingIndicator message="AI is thinking..." />
          )}

          {state.error && !error && (
            <ErrorMessage
              message={state.error}
              onRetry={handleRetry}
              onDismiss={handleDismissError}
            />
          )}

          {error && (
            <ErrorMessage
              message={error}
              onRetry={handleRetry}
              onDismiss={handleDismissError}
            />
          )}
        </div>

        <div className="input-area-container" role="form" aria-label="Message input area">
          <InputArea
            onSendMessage={handleSendMessage}
            loading={state.loading}
          />
        </div>
      </main>

      <footer className="chat-footer" role="contentinfo">
        <p>Powered by RAG Technology Made by Muhib Ali Siddiqui</p>
      </footer>
    </div>
  );
};

export default ChatContainer;