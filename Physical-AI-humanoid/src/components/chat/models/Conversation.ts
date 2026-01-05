// Conversation entity model following data-model.md specifications
import { Conversation as ConversationType, Message as MessageType } from '../types';
import { Message } from './Message';

export class Conversation implements ConversationType {
  id: string;
  title: string;
  messages: MessageType[];
  createdAt: Date | string;
  updatedAt: Date | string;
  isActive: boolean;

  constructor({ id, title, messages = [], createdAt, updatedAt, isActive = true }: Partial<ConversationType> & { title?: string }) {
    this.id = id || this.generateId();
    this.title = title || 'New Conversation';
    this.messages = messages ? messages.map(msg => msg instanceof Message ? msg : new Message(msg)) : []; // Convert to Message instances
    this.createdAt = createdAt || new Date();
    this.updatedAt = updatedAt || new Date();
    this.isActive = isActive;
  }

  generateId(): string {
    return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // Add a message to the conversation
  addMessage(message: MessageType | Partial<MessageType> & { content: string; role: 'user' | 'assistant' }): Message {
    const msgInstance = message instanceof Message ? message : new Message(message);
    this.messages = [...this.messages, msgInstance]; // Create a new array to ensure React detects the change
    this.updatedAt = new Date();
    return msgInstance;
  }

  // Get all user messages
  getUserMessages(): MessageType[] {
    return this.messages.filter(msg => msg.role === 'user');
  }

  // Get all AI messages
  getAssistantMessages(): MessageType[] {
    return this.messages.filter(msg => msg.role === 'assistant');
  }

  // Get the last message in the conversation
  getLastMessage(): MessageType | null {
    return this.messages.length > 0 ? this.messages[this.messages.length - 1] : null;
  }

  // Get messages by role
  getMessagesByRole(role: 'user' | 'assistant'): MessageType[] {
    return this.messages.filter(msg => msg.role === role);
  }

  // Validate the conversation object
  static validate(conversation: Partial<ConversationType>): boolean {
    if (!conversation.title || typeof conversation.title !== 'string') {
      throw new Error('Conversation title is required and must be a string');
    }

    if (conversation.messages && !Array.isArray(conversation.messages)) {
      throw new Error('Conversation messages must be an array');
    }

    if (conversation.messages) {
      conversation.messages.forEach((msg, index) => {
        try {
          Message.validate(msg);
        } catch (error) {
          throw new Error(`Message at index ${index} is invalid: ${error.message}`);
        }
      });
    }

    return true;
  }

  // Create a new conversation instance from raw data
  static fromData(data: Partial<ConversationType> & { title?: string }): Conversation {
    this.validate(data);
    return new Conversation(data);
  }

  // Convert conversation to plain object for serialization
  toJSON(): ConversationType {
    return {
      id: this.id,
      title: this.title,
      messages: this.messages.map(msg => msg.toJSON()),
      createdAt: this.createdAt instanceof Date ? this.createdAt.toISOString() : this.createdAt,
      updatedAt: this.updatedAt instanceof Date ? this.updatedAt.toISOString() : this.updatedAt,
      isActive: this.isActive
    };
  }
}