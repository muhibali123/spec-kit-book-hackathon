// Session entity model following data-model.md specifications
import { Session as SessionType, Conversation as ConversationType } from '../types';
import { Conversation } from './Conversation';

export class Session implements SessionType {
  id: string;
  userId: string | null;
  conversations: ConversationType[];
  createdAt: Date | string;
  expiresAt: Date | string;
  updatedAt?: Date | string;
  isActive: boolean;

  constructor({ id, userId = null, conversations = [], createdAt, expiresAt, isActive = true }: Partial<SessionType> & { userId?: string | null }) {
    this.id = id || this.generateId();
    this.userId = userId;
    this.conversations = conversations ? conversations.map(conv => conv instanceof Conversation ? conv : new Conversation(conv)) : []; // Convert to Conversation instances
    this.createdAt = createdAt || new Date();
    this.expiresAt = expiresAt || new Date(Date.now() + 24 * 60 * 60 * 1000); // Default: 24 hours from now
    this.isActive = isActive;
  }

  generateId(): string {
    return 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // Create a new conversation in this session
  createConversation(title?: string): Conversation {
    const conversation = new Conversation({
      title: title || `Conversation ${this.conversations.length + 1}`,
      createdAt: new Date()
    });
    this.conversations.push(conversation);
    this.updateTimestamps();
    return conversation;
  }

  // Get the active conversation (last one or the one marked active)
  getActiveConversation(): ConversationType | null {
    if (this.conversations.length === 0) {
      return null;
    }
    // Return the last conversation as the active one
    return this.conversations[this.conversations.length - 1];
  }

  // Get all conversations
  getAllConversations(): ConversationType[] {
    return this.conversations;
  }

  // Check if session is expired
  isExpired(): boolean {
    return new Date() > new Date(this.expiresAt);
  }

  // Extend session expiration
  extendExpiration(hours: number = 24): void {
    this.expiresAt = new Date(Date.now() + hours * 60 * 60 * 1000);
    this.updateTimestamps();
  }

  // Update timestamps
  updateTimestamps(): void {
    this.updatedAt = new Date();
  }

  // Validate the session object
  static validate(session: Partial<SessionType>): boolean {
    if (session.conversations && !Array.isArray(session.conversations)) {
      throw new Error('Session conversations must be an array');
    }

    if (session.conversations) {
      session.conversations.forEach((conv, index) => {
        try {
          Conversation.validate(conv);
        } catch (error) {
          throw new Error(`Conversation at index ${index} is invalid: ${error.message}`);
        }
      });
    }

    if (session.expiresAt && !(typeof session.expiresAt === 'string' || session.expiresAt instanceof Date) && isNaN(Date.parse(session.expiresAt as string))) {
      throw new Error('Session expiresAt must be a valid date');
    }

    return true;
  }

  // Create a new session instance from raw data
  static fromData(data: Partial<SessionType> & { userId?: string | null }): Session {
    this.validate(data);
    return new Session(data);
  }

  // Convert session to plain object for serialization
  toJSON(): SessionType {
    return {
      id: this.id,
      userId: this.userId,
      conversations: this.conversations.map(conv => conv.toJSON()),
      createdAt: this.createdAt instanceof Date ? this.createdAt.toISOString() : this.createdAt,
      expiresAt: this.expiresAt instanceof Date ? this.expiresAt.toISOString() : this.expiresAt,
      updatedAt: this.updatedAt instanceof Date ? this.updatedAt.toISOString() : this.updatedAt,
      isActive: this.isActive
    };
  }
}