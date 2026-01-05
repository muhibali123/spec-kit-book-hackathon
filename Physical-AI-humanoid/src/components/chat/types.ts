// TypeScript interfaces for chat entities

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date | string;
  citations: Citation[];
  conversationId: string | null;
}

export interface Citation {
  id: string;
  source: string;
  source_id?: string;
  source_title?: string;
  excerpt?: string;
  page?: number | null;
  page_number?: number | null;
  section?: string;
  section_reference?: string;
  content: string;
  relevance_score?: number;
  url?: string | null;
  documentId?: string | null;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date | string;
  updatedAt: Date | string;
  isActive: boolean;
}

export interface Session {
  id: string;
  userId: string | null;
  conversations: Conversation[];
  createdAt: Date | string;
  expiresAt: Date | string;
  updatedAt?: Date | string;
  isActive: boolean;
}

// API Request/Response models
export interface DocumentChunk {
  id: string;
  text: string;
  score: number;
  metadata: Record<string, any>;
  source: string;
}

export interface QueryRequest {
  query: string;
  conversationId?: string | null;
  filters?: Record<string, any>;
  top_k?: number;
  score_threshold?: number;
}

export interface QueryResponse {
  query: string;
  results: DocumentChunk[];
  total_results: number;
  processing_time: number;
}

// Define AnswerResponse interface for the /v1/answer endpoint
export interface AnswerResponse {
  query: string;
  answer: string;
  citations: Citation[];
  conversation_id: string;
  confidence_score?: number;
  processing_time: number;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  services: Record<string, boolean>;
}