// Session management module for handling user sessions
import chatStore from './store';
import { Session as SessionType, Conversation as ConversationType } from '../types';
import { Session } from '../models/Session';

interface SessionStatus {
  isAuthenticated: boolean;
  isExpired: boolean;
  session: SessionType | null;
  activeConversation: ConversationType | null;
  apiConnected: boolean;
}

interface ConversationStats {
  totalConversations: number;
  totalMessages: number;
  lastActive: number | null;
}

class SessionManager {
  private store: any;

  constructor(store: any = chatStore) {
    this.store = store;
  }

  // Get the current session
  getCurrentSession(): SessionType | null {
    return this.store.getState().session;
  }

  // Get the active conversation
  getActiveConversation(): ConversationType | null {
    return this.store.getState().activeConversation;
  }

  // Create a new conversation
  createNewConversation(title?: string): ConversationType {
    return this.store.createNewConversation(title);
  }

  // Switch to an existing conversation
  switchConversation(conversationId: string): boolean {
    return this.store.switchConversation(conversationId);
  }

  // Get all conversations in the current session
  getAllConversations(): ConversationType[] {
    const session = this.getCurrentSession();
    return session ? session.getAllConversations() : [];
  }

  // Check if session is expired
  isSessionExpired(): boolean {
    const session = this.getCurrentSession();
    return session ? session.isExpired() : true;
  }

  // Extend session expiration
  extendSession(hours: number = 24): boolean {
    const session = this.getCurrentSession();
    if (session) {
      session.extendExpiration(hours);
      this.store.saveSessionToStorage();
      return true;
    }
    return false;
  }

  // Clear the current session
  clearSession(): void {
    this.store.clearSession();
  }

  // Get session status
  getSessionStatus(): SessionStatus {
    const state = this.store.getState();
    return {
      isAuthenticated: !!state.session,
      isExpired: this.isSessionExpired(),
      session: state.session,
      activeConversation: state.activeConversation,
      apiConnected: state.apiConnected
    };
  }

  // Initialize a new session
  initializeSession(): void {
    this.store.createSession();
  }

  // Create a new conversation within the session
  createNewConversation(title?: string): ConversationType {
    return this.store.createNewConversation(title);
  }

  // End the current session
  endSession(): void {
    this.store.clearSession();
  }

  // Load session from storage
  loadSession(): SessionType | null {
    const session = this.store.loadSessionFromStorage();
    if (session && !session.isExpired()) {
      this.store.state.session = session;
      this.store.state.activeConversation = session.getActiveConversation();
      this.store.notifyListeners();
      return session;
    }
    return null;
  }

  // Check if user has any conversations
  hasConversations(): boolean {
    const conversations = this.getAllConversations();
    return conversations && conversations.length > 0;
  }

  // Get conversation statistics
  getConversationStats(): ConversationStats | null {
    const conversations = this.getAllConversations();
    if (!conversations) return null;

    return {
      totalConversations: conversations.length,
      totalMessages: conversations.reduce((total, conv) => total + conv.messages.length, 0),
      lastActive: conversations.length > 0
        ? Math.max(...conversations.map(conv => new Date(conv.updatedAt as string).getTime()))
        : null
    };
  }
}

// Create a singleton instance
const sessionManager = new SessionManager();

// Export the singleton instance
export default sessionManager;