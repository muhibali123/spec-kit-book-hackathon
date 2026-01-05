// Message entity model following data-model.md specifications
import { Message as MessageType, Citation } from '../types';

export class Message implements MessageType {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date | string;
  citations: Citation[];
  conversationId: string | null;

  constructor({ id, content, role, timestamp, citations = [], conversationId = null }: Partial<MessageType> & { content: string; role: 'user' | 'assistant' }) {
    this.id = id || this.generateId();
    this.content = content;
    this.role = role; // 'user' or 'assistant'
    this.timestamp = timestamp || new Date();
    this.citations = citations || []; // Array of citation objects
    this.conversationId = conversationId;
  }

  generateId(): string {
    return 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // Validate the message object
  static validate(message: Partial<MessageType>): boolean {
    if (!message.content || typeof message.content !== 'string') {
      throw new Error('Message content is required and must be a string');
    }

    if (!message.role || !['user', 'assistant'].includes(message.role)) {
      throw new Error('Message role is required and must be either "user" or "assistant"');
    }

    if (message.citations && !Array.isArray(message.citations)) {
      throw new Error('Citations must be an array');
    }

    return true;
  }

  // Create a new message instance from raw data
  static fromData(data: Partial<MessageType> & { content: string; role: 'user' | 'assistant' }): Message {
    this.validate(data);
    return new Message(data);
  }

  // Convert message to plain object for serialization
  toJSON(): MessageType {
    return {
      id: this.id,
      content: this.content,
      role: this.role,
      timestamp: this.timestamp instanceof Date ? this.timestamp.toISOString() : this.timestamp,
      citations: this.citations,
      conversationId: this.conversationId
    };
  }
}