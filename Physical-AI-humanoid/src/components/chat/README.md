# AI Chat Interface Components

This directory contains all components for the AI-powered chat interface integrated into the Docusaurus documentation website.

## Architecture Overview

```
src/
└── components/
    └── chat/
        ├── models/           # Data models (Message, Citation, Conversation, Session)
        ├── services/         # Business logic services (API, validation, formatting, error handling)
        ├── state/            # State management (store, session management, hooks)
        ├── pages/            # Docusaurus pages (chat interface page)
        ├── *.js              # React components (ChatContainer, MessageList, etc.)
        └── *.css             # Component-specific styles
```

## Components

### Core Components
- `ChatContainer.js` - Main container component managing state and API communication
- `MessageList.js` - Component for displaying conversation history
- `InputArea.js` - Component for user input with validation
- `UserMessage.js` - Component for displaying user messages
- `AIMessage.js` - Component for displaying AI responses with citations
- `Citation.js` - Component for displaying source citations
- `LoadingIndicator.js` - Component for showing loading states
- `ErrorMessage.js` - Component for displaying error messages

### Services
- `ApiClient.js` - API client for connecting to Module 05 RAG Agent API
- `validation.js` - Input validation service
- `formatting.js` - Response formatting service with markdown support
- `error.js` - Error mapping service for user-friendly messages
- `sanitization.js` - Input sanitization service to prevent injection attacks
- `storage.js` - Local storage service for persisting conversation history

### State Management
- `store.js` - Centralized state management for conversations
- `session.js` - Session management service
- `hooks.js` - React hooks for accessing state

### Models
- `Message.js` - Message entity model
- `Citation.js` - Citation entity model
- `Conversation.js` - Conversation entity model
- `Session.js` - Session entity model

## Features Implemented

### Multi-turn Conversations
- Conversation history preservation
- Context management across turns
- Session handling with localStorage persistence

### Citation Rendering
- Proper citation display with source information
- Clickable links to source documents
- Citation formatting with visual distinction

### Loading and Error States
- Loading indicators during API requests
- Comprehensive error handling with user-friendly messages
- Retry mechanisms for recoverable errors

### Accessibility Features
- WCAG 2.1 AA compliant interface
- Proper ARIA labels and attributes
- Keyboard navigation support
- Screen reader compatibility

### Security Measures
- Input sanitization to prevent XSS
- Client-side data protection
- Validation of URLs and content

## API Integration

The chat interface connects to the Module 05 RAG Agent API using the following endpoints:

- `POST /api/v1/query` - Submit a query and receive an answer with citations
- `GET /health` - Check the health status of the API

The API client includes:
- Request/response validation
- Error handling with retry mechanisms
- Timeout management
- Authentication support (when implemented)

## Styling

All components include responsive CSS that works across device sizes. The styling follows the Docusaurus theme and can be customized by modifying the CSS files in this directory.

## Testing

Integration tests are available in `test-integration.js` to validate that all components work together correctly.

## Environment Variables

The following environment variables can be set:

- `RAG_AGENT_API_URL` - URL of the RAG Agent API (defaults to http://localhost:8000)