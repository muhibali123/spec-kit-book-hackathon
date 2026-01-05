// Input validation service for chat interface
import { Message, Citation, Conversation } from '../types';

interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

class ValidationService {
  private maxInputLength: number;
  private minInputLength: number;
  private xssPattern: RegExp;

  constructor() {
    // Maximum length for input (configurable)
    this.maxInputLength = 2000;
    // Minimum length for valid input
    this.minInputLength = 1;
    // Regular expression for detecting potentially harmful content
    this.xssPattern = /(<script|javascript:|vbscript:|onload|onerror)/gi;
  }

  // Validate user input for questions
  validateInput(input: any): ValidationResult {
    const errors: string[] = [];

    // Check if input is provided
    if (!input) {
      errors.push('Input is required');
    } else {
      // Check if input is a string
      if (typeof input !== 'string') {
        errors.push('Input must be a string');
      } else {
        // Check for empty or whitespace-only input
        if (this.isEmptyOrWhitespace(input)) {
          errors.push('Input cannot be empty or contain only whitespace');
        }

        // Check input length
        if (input.length < this.minInputLength) {
          errors.push(`Input must be at least ${this.minInputLength} character(s) long`);
        }

        if (input.length > this.maxInputLength) {
          errors.push(`Input exceeds maximum length of ${this.maxInputLength} characters`);
        }

        // Check for potential XSS attempts
        if (this.xssPattern.test(input)) {
          errors.push('Input contains potentially harmful content');
        }
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Check if string is empty or contains only whitespace
  isEmptyOrWhitespace(str: string): boolean {
    return typeof str === 'string' && str.trim().length === 0;
  }

  // Validate for empty or whitespace-only input specifically
  validateEmptyOrWhitespace(input: any): boolean {
    if (typeof input !== 'string') {
      return false;
    }
    return input.trim().length === 0;
  }

  // Validate input length against limits
  validateInputLength(input: any): ValidationResult {
    if (typeof input !== 'string') {
      return {
        isValid: false,
        errors: ['Input must be a string']
      };
    }

    const errors: string[] = [];

    if (input.length < this.minInputLength) {
      errors.push(`Input must be at least ${this.minInputLength} character(s) long`);
    }

    if (input.length > this.maxInputLength) {
      errors.push(`Input exceeds maximum length of ${this.maxInputLength} characters`);
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Validate a message object
  validateMessage(message: any): ValidationResult {
    const errors: string[] = [];

    // Check if message object exists
    if (!message) {
      errors.push('Message is required');
      return {
        isValid: false,
        errors
      };
    }

    // Validate content
    const contentValidation = this.validateInput(message.content);
    if (!contentValidation.isValid) {
      errors.push(...contentValidation.errors.map(error => `Content: ${error}`));
    }

    // Validate role
    if (!message.role) {
      errors.push('Message role is required');
    } else if (!['user', 'ai'].includes(message.role)) {
      errors.push('Message role must be either "user" or "ai"');
    }

    // Validate citations if present
    if (message.citations) {
      if (!Array.isArray(message.citations)) {
        errors.push('Citations must be an array');
      } else {
        message.citations.forEach((citation: any, index: number) => {
          const citationValidation = this.validateCitation(citation);
          if (!citationValidation.isValid) {
            errors.push(`Citation at index ${index}: ${citationValidation.errors.join(', ')}`);
          }
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Validate a citation object
  validateCitation(citation: any): ValidationResult {
    const errors: string[] = [];

    if (!citation) {
      errors.push('Citation is required');
      return {
        isValid: false,
        errors
      };
    }

    if (!citation.source) {
      errors.push('Citation source is required');
    }

    if (!citation.content) {
      errors.push('Citation content is required');
    }

    if (citation.page !== undefined && citation.page !== null && typeof citation.page !== 'number') {
      errors.push('Citation page must be a number if provided');
    }

    if (citation.section && typeof citation.section !== 'string') {
      errors.push('Citation section must be a string if provided');
    }

    if (citation.url && typeof citation.url !== 'string') {
      errors.push('Citation URL must be a string if provided');
    }

    if (citation.documentId && typeof citation.documentId !== 'string') {
      errors.push('Citation documentId must be a string if provided');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Validate a conversation object
  validateConversation(conversation: any): ValidationResult {
    const errors: string[] = [];

    if (!conversation) {
      errors.push('Conversation is required');
      return {
        isValid: false,
        errors
      };
    }

    if (!conversation.title) {
      errors.push('Conversation title is required');
    } else if (typeof conversation.title !== 'string') {
      errors.push('Conversation title must be a string');
    }

    if (conversation.messages && !Array.isArray(conversation.messages)) {
      errors.push('Conversation messages must be an array');
    } else if (conversation.messages) {
      conversation.messages.forEach((message: any, index: number) => {
        const messageValidation = this.validateMessage(message);
        if (!messageValidation.isValid) {
          errors.push(`Message at index ${index}: ${messageValidation.errors.join(', ')}`);
        }
      });
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Sanitize input to remove potentially harmful content
  sanitizeInput(input: any): string {
    if (typeof input !== 'string') {
      return '';
    }

    // Remove potential XSS attempts
    let sanitized = input.replace(this.xssPattern, '');

    // Additional sanitization could be added here
    // For example, removing other potentially harmful patterns

    return sanitized;
  }

  // Update the maximum input length
  setMaxInputLength(length: number): void {
    if (typeof length === 'number' && length > 0) {
      this.maxInputLength = length;
    }
  }

  // Update the minimum input length
  setMinInputLength(length: number): void {
    if (typeof length === 'number' && length >= 0) {
      this.minInputLength = length;
    }
  }
}

// Create a singleton instance
const validationService = new ValidationService();

// Export the singleton instance
export default validationService;