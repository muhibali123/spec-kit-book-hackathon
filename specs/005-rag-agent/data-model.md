# Data Model: RAG Agent & Answer Generation Service

## Core Entities

### UserQuery
**Description**: The natural language question or request submitted by the user
**Attributes**:
- query_text: string - The user's question in natural language
- query_id: string - Unique identifier for the query
- conversation_id: string (optional) - Identifier for multi-turn conversations
- metadata: object (optional) - Additional context like user preferences, query type
- timestamp: datetime - When the query was submitted

### RetrievedContext
**Description**: The relevant document chunks and metadata retrieved from Module 04
**Attributes**:
- context_chunks: array of ContextChunk - List of relevant document segments
- relevance_scores: array of float - Confidence scores for each chunk
- metadata: object - Additional information about the retrieval

### ContextChunk
**Description**: A segment of content from the knowledge base that is relevant to the query
**Attributes**:
- chunk_id: string - Unique identifier for the chunk
- content: string - The actual text content
- source_document: string - Reference to the original document
- source_section: string (optional) - Section within the document
- metadata: object - Additional metadata like page number, chapter, etc.
- relevance_score: float - How relevant this chunk is to the query

### GeneratedAnswer
**Description**: The AI-produced response that addresses the user's query
**Attributes**:
- answer_id: string - Unique identifier for the answer
- answer_text: string - The generated answer text
- confidence_score: float - Confidence in the answer's accuracy
- citations: array of Citation - References to source documents
- metadata: object - Additional information about the generation process
- timestamp: datetime - When the answer was generated

### Citation
**Description**: Reference to the specific document and section that informed the answer
**Attributes**:
- source_id: string - Identifier of the source document
- source_title: string - Title of the source document
- excerpt: string - Relevant excerpt from the source
- page_number: integer (optional) - Page in the original document
- section_reference: string (optional) - Section identifier
- relevance_score: float - How much this source contributed to the answer

### ConversationContext
**Description**: History of interactions between the user and system
**Attributes**:
- conversation_id: string - Unique identifier for the conversation
- turns: array of ConversationTurn - Chronological list of exchanges
- metadata: object - Additional context like user preferences
- created_at: datetime - When the conversation started
- last_activity: datetime - When the last interaction occurred

### ConversationTurn
**Description**: A single exchange in a conversation
**Attributes**:
- turn_id: string - Unique identifier for the turn
- user_query: UserQuery - The user's input
- system_response: GeneratedAnswer - The system's response
- timestamp: datetime - When the exchange occurred
- context_summary: string (optional) - Brief summary of context for this turn

## Relationships

- UserQuery may be part of one ConversationContext (optional)
- GeneratedAnswer is associated with one UserQuery
- GeneratedAnswer references multiple ContextChunk through citations
- ConversationContext contains multiple ConversationTurn
- ContextChunk is part of RetrievedContext
- Citation references ContextChunk or source document directly

## Validation Rules

### UserQuery Validation
- query_text must be 1-1000 characters
- query_text cannot be empty or whitespace-only
- conversation_id format must be valid UUID if provided

### GeneratedAnswer Validation
- answer_text must be provided and non-empty
- confidence_score must be between 0.0 and 1.0
- citations array cannot exceed 20 items
- Each citation must reference a valid source

### ContextChunk Validation
- content must be 1-10000 characters
- relevance_score must be between 0.0 and 1.0
- source_document cannot be empty

### ConversationContext Validation
- conversation_id must be valid UUID
- cannot exceed 25 turns
- must be active within 2 hours of last activity