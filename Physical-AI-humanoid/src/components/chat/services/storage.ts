// Local storage service for persisting conversation history
import { Session as SessionType, Conversation as ConversationType } from '../types';
import { Session } from '../models/Session';
import { Conversation } from '../models/Conversation';

interface StorageInfo {
  sessionSize: number;
  conversationsSize: number;
  totalSize: number;
}

interface AvailableStorage {
  used: number;
  limit: number;
  available: number;
}

class StorageService {
  private storageKey: string;
  private conversationsKey: string;

  constructor() {
    this.storageKey = 'chat-session';
    this.conversationsKey = 'chat-conversations';
  }

  // Save session to localStorage
  saveSession(session: SessionType): boolean {
    try {
      const serializedSession = JSON.stringify(session.toJSON ? session.toJSON() : session);
      localStorage.setItem(this.storageKey, serializedSession);
      return true;
    } catch (error) {
      console.error('Failed to save session to localStorage:', error);
      return false;
    }
  }

  // Load session from localStorage
  loadSession(): SessionType | null {
    try {
      const serializedSession = localStorage.getItem(this.storageKey);
      if (serializedSession) {
        const sessionData = JSON.parse(serializedSession);
        return Session.fromData(sessionData);
      }
    } catch (error) {
      console.error('Failed to load session from localStorage:', error);
    }
    return null;
  }

  // Clear session from localStorage
  clearSession(): boolean {
    try {
      localStorage.removeItem(this.storageKey);
      return true;
    } catch (error) {
      console.error('Failed to clear session from localStorage:', error);
      return false;
    }
  }

  // Save conversations to localStorage
  saveConversations(conversations: ConversationType[]): boolean {
    try {
      const serializedConversations = JSON.stringify(
        conversations.map(conv => conv.toJSON ? conv.toJSON() : conv)
      );
      localStorage.setItem(this.conversationsKey, serializedConversations);
      return true;
    } catch (error) {
      console.error('Failed to save conversations to localStorage:', error);
      return false;
    }
  }

  // Load conversations from localStorage
  loadConversations(): ConversationType[] {
    try {
      const serializedConversations = localStorage.getItem(this.conversationsKey);
      if (serializedConversations) {
        const conversationsData = JSON.parse(serializedConversations);
        return conversationsData.map((data: any) => Conversation.fromData(data));
      }
    } catch (error) {
      console.error('Failed to load conversations from localStorage:', error);
    }
    return [];
  }

  // Clear conversations from localStorage
  clearConversations(): boolean {
    try {
      localStorage.removeItem(this.conversationsKey);
      return true;
    } catch (error) {
      console.error('Failed to clear conversations from localStorage:', error);
      return false;
    }
  }

  // Save conversation to a specific session
  saveConversationToSession(sessionId: string, conversation: ConversationType): boolean {
    try {
      // Load existing session
      const session = this.loadSession();
      if (session && session.id === sessionId) {
        // Add or update the conversation in the session
        const existingIndex = session.conversations.findIndex((c: ConversationType) => c.id === conversation.id);
        if (existingIndex >= 0) {
          session.conversations[existingIndex] = conversation;
        } else {
          session.conversations.push(conversation);
        }
        // Save the updated session
        this.saveSession(session);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to save conversation to session:', error);
      return false;
    }
  }

  // Get conversation from a specific session
  getConversationFromSession(sessionId: string, conversationId: string): ConversationType | null {
    try {
      const session = this.loadSession();
      if (session && session.id === sessionId) {
        return session.conversations.find((c: ConversationType) => c.id === conversationId) || null;
      }
      return null;
    } catch (error) {
      console.error('Failed to get conversation from session:', error);
      return null;
    }
  }

  // Update session with new data
  updateSession(session: SessionType): boolean {
    try {
      // Save the entire session
      this.saveSession(session);
      return true;
    } catch (error) {
      console.error('Failed to update session:', error);
      return false;
    }
  }

  // Encrypt data before storing (simplified version for browser)
  encryptData(data: any): string | null {
    try {
      // In a real implementation, you would use a proper encryption library
      // For now, we'll use a simple approach for demonstration
      const jsonString = JSON.stringify(data);
      // This is NOT real encryption - just for demonstration
      // In production, use Web Crypto API or a proper encryption library
      return btoa(encodeURIComponent(jsonString));
    } catch (error) {
      console.error('Failed to encrypt data:', error);
      return null;
    }
  }

  // Decrypt data after retrieving (simplified version for browser)
  decryptData(encryptedData: string): any {
    try {
      // In a real implementation, you would use a proper decryption library
      // For now, we'll use a simple approach for demonstration
      const jsonString = decodeURIComponent(atob(encryptedData));
      return JSON.parse(jsonString);
    } catch (error) {
      console.error('Failed to decrypt data:', error);
      return null;
    }
  }

  // Securely save session with optional encryption
  saveSessionSecure(session: SessionType, encrypt: boolean = false): boolean {
    try {
      let dataToSave: any = session;
      if (encrypt) {
        const encrypted = this.encryptData(session);
        if (!encrypted) return false;
        // Store both the encrypted data and a flag
        dataToSave = {
          encrypted: true,
          data: encrypted
        };
      }

      const serializedSession = JSON.stringify(dataToSave.toJSON ? dataToSave.toJSON() : dataToSave);
      localStorage.setItem(this.storageKey, serializedSession);
      return true;
    } catch (error) {
      console.error('Failed to save session securely:', error);
      return false;
    }
  }

  // Securely load session with optional decryption
  loadSessionSecure(): SessionType | null {
    try {
      const serializedSession = localStorage.getItem(this.storageKey);
      if (serializedSession) {
        const sessionData = JSON.parse(serializedSession);

        // Check if the data is encrypted
        if (sessionData.encrypted && sessionData.data) {
          const decryptedData = this.decryptData(sessionData.data);
          if (!decryptedData) return null;
          return Session.fromData(decryptedData);
        }

        // Data is not encrypted, load normally
        return Session.fromData(sessionData);
      }
    } catch (error) {
      console.error('Failed to load session securely:', error);
    }
    return null;
  }

  // Get storage usage information
  getStorageInfo(): StorageInfo {
    try {
      const sessionData = localStorage.getItem(this.storageKey);
      const conversationsData = localStorage.getItem(this.conversationsKey);

      return {
        sessionSize: sessionData ? new Blob([sessionData]).size : 0,
        conversationsSize: conversationsData ? new Blob([conversationsData]).size : 0,
        totalSize: (sessionData ? new Blob([sessionData]).size : 0) +
                  (conversationsData ? new Blob([conversationsData]).size : 0)
      };
    } catch (error) {
      console.error('Failed to get storage info:', error);
      return { sessionSize: 0, conversationsSize: 0, totalSize: 0 };
    }
  }

  // Check if storage is available
  isStorageAvailable(): boolean {
    try {
      const test = '__storage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch (e) {
      return false;
    }
  }

  // Get available storage space (approximation)
  getAvailableStorage(): AvailableStorage {
    const info = this.getStorageInfo();
    // Most browsers have a 5-10MB limit for localStorage
    const estimatedLimit = 5 * 1024 * 1024; // 5MB in bytes
    return {
      used: info.totalSize,
      limit: estimatedLimit,
      available: Math.max(0, estimatedLimit - info.totalSize)
    };
  }

  // Check if storage is nearly full (more than 80% used)
  isStorageNearlyFull(): boolean {
    const storageInfo = this.getAvailableStorage();
    return storageInfo.limit > 0 && (storageInfo.used / storageInfo.limit) > 0.8;
  }
}

// Create a singleton instance
const storageService = new StorageService();

// Export the singleton instance
export default storageService;