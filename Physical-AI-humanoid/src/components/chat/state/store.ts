// State management module for managing conversation state
import { Session as SessionType, Conversation as ConversationType, Message as MessageType } from '../types';
import { Session } from '../models/Session';
import { Conversation } from '../models/Conversation';
import { Message } from '../models/Message';

interface State {
  session: SessionType | null;
  activeConversation: ConversationType | null;
  loading: boolean;
  error: string | null;
  apiConnected: boolean;
}

type Listener = (state: State) => void;

class ChatStore {
  private state: State;
  private listeners: Listener[];

  constructor() {
    this.state = {
      session: null,
      activeConversation: null,
      loading: false,
      error: null,
      apiConnected: false
    };

    this.listeners = [];
    this.initializeSession();
  }

  // Initialize session from localStorage or create a new one
  initializeSession(): void {
    // Only try to load from localStorage if we're in the browser
    if (typeof window !== 'undefined' && window.localStorage) {
      const savedSession = this.loadSessionFromStorage();
      if (savedSession && !savedSession.isExpired()) {
        this.state.session = savedSession;
        this.state.activeConversation = savedSession.getActiveConversation();
      } else {
        this.createSession();
      }
    } else {
      // On the server, create a new session
      this.createSession();
    }
  }

  // Create a new session
  createSession(): void {
    this.state.session = new Session({});
    this.state.activeConversation = this.state.session.getActiveConversation();
    this.saveSessionToStorage();
    this.notifyListeners();
  }

  // Get current state
  getState(): State {
    return { ...this.state };
  }

  // Subscribe to state changes
  subscribe(listener: Listener): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  // Notify all listeners of state changes
  notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.getState()));
  }

  // Set loading state
  setLoading(loading: boolean): void {
    this.state.loading = loading;
    this.notifyListeners();
  }

  // Get loading state
  isLoading(): boolean {
    return this.state.loading;
  }

  // Set error state
  setError(error: string | null): void {
    this.state.error = error;
    this.notifyListeners();
  }

  // Clear error state
  clearError(): void {
    this.state.error = null;
    this.notifyListeners();
  }

  // Get error state
  getError(): string | null {
    return this.state.error;
  }

  // Set API connection status
  setApiConnected(connected: boolean): void {
    this.state.apiConnected = connected;
    this.notifyListeners();
  }

  // Create a new conversation
  createNewConversation(title?: string): ConversationType {
    if (!this.state.session) {
      throw new Error('No session available');
    }

    const conversation = this.state.session.createConversation(title);
    this.state.activeConversation = conversation;
    this.saveSessionToStorage();
    this.notifyListeners();
    return conversation;
  }

  // Switch to an existing conversation
  switchConversation(conversationId: string): ConversationType {
    if (!this.state.session) {
      throw new Error('No session available');
    }

    const conversation = this.state.session.getAllConversations()
      .find((conv: ConversationType) => conv.id === conversationId);

    if (conversation) {
      this.state.activeConversation = conversation;
      this.notifyListeners();
      return conversation;
    }

    throw new Error(`Conversation with ID ${conversationId} not found`);
  }

  // Add a message to the active conversation
  addMessageToActiveConversation(message: MessageType | Partial<MessageType> & { content: string; role: 'user' | 'assistant' }): Message {
    if (!this.state.activeConversation) {
      throw new Error('No active conversation');
    }

    const msg = this.state.activeConversation.addMessage(message);
    this.saveSessionToStorage();
    this.notifyListeners();
    return msg;
  }

  // Get all conversation history
  getConversationHistory(conversationId: string | null = null): MessageType[] {
    const conv = conversationId
      ? (this.state.session as SessionType & { conversations: ConversationType[] })?.conversations?.find(c => c.id === conversationId)
      : this.state.activeConversation;

    return conv ? conv.messages : [];
  }

  // Clear conversation history for the active conversation
  clearConversationHistory(conversationId: string | null = null): void {
    const conv = conversationId
      ? (this.state.session as SessionType & { conversations: ConversationType[] })?.conversations?.find(c => c.id === conversationId)
      : this.state.activeConversation;

    if (conv) {
      conv.messages = [];
      conv.updatedAt = new Date();
      this.saveSessionToStorage();
      this.notifyListeners();
    }
  }

  // Update conversation title
  updateConversationTitle(conversationId: string, title: string): void {
    const conv = (this.state.session as SessionType & { conversations: ConversationType[] })?.conversations?.find(c => c.id === conversationId);
    if (conv) {
      conv.title = title;
      conv.updatedAt = new Date();
      this.saveSessionToStorage();
      this.notifyListeners();
    }
  }

  // Update the active conversation
  updateActiveConversation(updates: Partial<ConversationType>): void {
    if (!this.state.activeConversation) {
      throw new Error('No active conversation');
    }

    Object.assign(this.state.activeConversation, updates);
    this.saveSessionToStorage();
    this.notifyListeners();
  }

  // Save session to localStorage
  saveSessionToStorage(): void {
    if (this.state.session && typeof window !== 'undefined' && window.localStorage) {
      try {
        const serializedSession = JSON.stringify(this.state.session.toJSON());
        localStorage.setItem('chat-session', serializedSession);
      } catch (error) {
        console.error('Failed to save session to localStorage:', error);
      }
    }
  }

  // Load session from localStorage
  loadSessionFromStorage(): SessionType | null {
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        const serializedSession = localStorage.getItem('chat-session');
        if (serializedSession) {
          const sessionData = JSON.parse(serializedSession);
          return Session.fromData(sessionData);
        }
      } catch (error) {
        console.error('Failed to load session from localStorage:', error);
      }
    }
    return null;
  }

  // Clear the current session
  clearSession(): void {
    this.state.session = null;
    this.state.activeConversation = null;
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('chat-session');
    }
    this.notifyListeners();
  }

  // Reset the store to initial state
  reset(): void {
    this.clearSession();
    this.initializeSession();
  }
}

// Create a singleton instance
const chatStore = new ChatStore();

// Export the singleton instance
export default chatStore;