# Data Model: Module 06 - Chat UI & Frontend Integration

## 1. Core Entities

### Message Entity
- **Name**: Message
- **Description**: Represents a single message in the conversation
- **Fields**:
  - id: string (unique identifier for the message)
  - sender: string (enum: "user", "ai")
  - content: string (the message content)
  - timestamp: Date (when the message was created/sent)
  - status: string (enum: "pending", "sent", "received", "error")
  - citations: array of Citation objects (optional, for AI responses)
  - conversationId: string (link to parent conversation)
- **Validation Rules**:
  - content must not be empty for user messages
  - sender must be either "user" or "ai"
  - timestamp must be in valid date format
- **State Transitions**:
  - pending → sent/received → error (for handling message lifecycle)

### Citation Entity
- **Name**: Citation
- **Description**: Represents a source citation for AI-generated content
- **Fields**:
  - sourceId: string (unique identifier for the source)
  - sourceTitle: string (title of the source document)
  - excerpt: string (relevant excerpt from the source)
  - pageNumber: number (optional, page number in source)
  - sectionReference: string (optional, section reference in source)
  - relevanceScore: number (0.0 to 1.0, relevance of citation to answer)
- **Validation Rules**:
  - sourceId and sourceTitle must not be empty
  - relevanceScore must be between 0.0 and 1.0
  - pageNumber must be positive if provided

### Conversation Entity
- **Name**: Conversation
- **Description**: Represents a single conversation session
- **Fields**:
  - id: string (unique identifier for the conversation)
  - title: string (auto-generated from first question or user-provided)
  - messages: array of Message objects (ordered list of messages)
  - createdAt: Date (when the conversation was started)
  - lastActiveAt: Date (when the last message was added)
  - isActive: boolean (whether the conversation is currently active)
- **Validation Rules**:
  - id must be unique
  - createdAt must be in valid date format
  - messages must be in chronological order
- **State Transitions**:
  - active → inactive (when session expires or user ends conversation)

### Session Entity
- **Name**: Session
- **Description**: Represents a user's active session with conversation history
- **Fields**:
  - id: string (unique session identifier)
  - userId: string (optional, user identifier if applicable)
  - activeConversationId: string (currently active conversation)
  - conversationHistory: array of Conversation objects
  - createdAt: Date (session start time)
  - expiresAt: Date (session expiration time)
- **Validation Rules**:
  - id must be unique per user
  - expiresAt must be after createdAt
  - activeConversationId must reference a valid conversation in history

## 2. Relationships

### Message → Conversation
- **Relationship**: One-to-Many (one conversation contains many messages)
- **Cardinality**: Each message belongs to exactly one conversation
- **Constraint**: Messages must reference a valid conversation ID

### Citation → Message
- **Relationship**: One-to-Many (one message can have multiple citations)
- **Cardinality**: Each citation belongs to exactly one message
- **Constraint**: Citations are optional and only present in AI-generated messages

### Session → Conversation
- **Relationship**: One-to-Many (one session contains many conversations)
- **Cardinality**: Each conversation belongs to exactly one session
- **Constraint**: Session must maintain conversation history

## 3. Data Flow Patterns

### Message Creation Flow
1. User submits question → Message created with sender="user", status="pending"
2. API request sent → Message status updated to "sent"
3. Response received → AI Message created with sender="ai", status="received", citations included
4. Both messages added to Conversation.messages array

### Citation Processing Flow
1. AI response includes citation data
2. Citation objects extracted from response
3. Citations linked to the AI Message
4. Citations displayed separately in UI with source information

## 4. Client-Side Storage Schema

### Local Storage Structure
- Key: "chat_sessions" → Value: JSON object containing session data
- Key: "active_conversation_id" → Value: Current conversation ID string
- Key: "user_preferences" → Value: User preference settings (accessibility, etc.)

### Session Data Structure
```json
{
  "id": "session-123",
  "userId": "optional-user-id",
  "activeConversationId": "conv-456",
  "conversationHistory": [
    {
      "id": "conv-456",
      "title": "How to use RAG system?",
      "createdAt": "2025-12-17T10:00:00Z",
      "lastActiveAt": "2025-12-17T10:15:00Z",
      "isActive": true,
      "messages": [
        {
          "id": "msg-789",
          "sender": "user",
          "content": "How do I use the RAG system?",
          "timestamp": "2025-12-17T10:00:00Z",
          "status": "sent"
        },
        {
          "id": "msg-790",
          "sender": "ai",
          "content": "The RAG system retrieves relevant documents...",
          "timestamp": "2025-12-17T10:00:05Z",
          "status": "received",
          "citations": [
            {
              "sourceId": "doc-001",
              "sourceTitle": "RAG System Guide",
              "excerpt": "The RAG system retrieves documents...",
              "relevanceScore": 0.95
            }
          ]
        }
      ]
    }
  ],
  "createdAt": "2025-12-17T10:00:00Z",
  "expiresAt": "2025-12-17T18:00:00Z"
}
```