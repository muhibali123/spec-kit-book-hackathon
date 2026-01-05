// Input sanitization service to prevent injection attacks
import { Message as MessageType, Citation as CitationType } from '../types';

class SanitizationService {
  private allowedTags: string[];
  private dangerousPatterns: RegExp[];

  constructor() {
    // Define allowed HTML tags and attributes for safe content
    this.allowedTags = [
      'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'code', 'pre',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li'
    ];

    // Define potentially dangerous patterns to remove
    this.dangerousPatterns = [
      /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
      /<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi,
      /<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi,
      /<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi,
      /<form\b[^<]*(?:(?!<\/form>)<[^<]*)*<\/form>/gi,
      /javascript:/gi,
      /vbscript:/gi,
      /onload=/gi,
      /onerror=/gi,
      /onmouseover=/gi,
      /onmouseout=/gi,
      /data:/gi,
      /file:/gi,
    ];
  }

  // Sanitize HTML content
  sanitizeHtml(html: any): any {
    if (typeof html !== 'string') {
      return html;
    }

    let sanitized = html;

    // Remove dangerous patterns first
    this.dangerousPatterns.forEach(pattern => {
      sanitized = sanitized.replace(pattern, '');
    });

    // Remove any remaining script-like content
    sanitized = sanitized.replace(/<\s*\/?\s*script[^>]*>/gi, '');

    return sanitized;
  }

  // Sanitize plain text
  sanitizeText(text: any): any {
    if (typeof text !== 'string') {
      return text;
    }

    // Remove dangerous patterns
    let sanitized = text;
    this.dangerousPatterns.forEach(pattern => {
      sanitized = sanitized.replace(pattern, '');
    });

    // Escape HTML characters
    return sanitized
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;');
  }

  // Sanitize user input
  sanitizeInput(input: any): any {
    if (typeof input !== 'string') {
      return input;
    }

    // First, sanitize HTML if present
    let sanitized = this.sanitizeHtml(input);

    // Then escape any remaining HTML characters
    sanitized = this.sanitizeText(sanitized);

    return sanitized;
  }

  // Sanitize message content
  sanitizeMessage(message: any): any {
    if (!message || typeof message !== 'object') {
      return message;
    }

    const sanitizedMessage = { ...message };

    if (message.content) {
      sanitizedMessage.content = this.sanitizeInput(message.content);
    }

    if (message.citations && Array.isArray(message.citations)) {
      sanitizedMessage.citations = message.citations.map((citation: CitationType) => {
        const sanitizedCitation = { ...citation };
        if (citation.content) {
          sanitizedCitation.content = this.sanitizeInput(citation.content);
        }
        if (citation.source) {
          sanitizedCitation.source = this.sanitizeInput(citation.source);
        }
        return sanitizedCitation;
      });
    }

    return sanitizedMessage;
  }

  // Validate URL for safe usage
  isValidUrl(url: any): boolean {
    if (typeof url !== 'string') {
      return false;
    }

    try {
      const parsedUrl = new URL(url);
      // Only allow http, https, and mailto protocols
      return ['http:', 'https:', 'mailto:'].includes(parsedUrl.protocol);
    } catch (e) {
      return false;
    }
  }

  // Sanitize URL
  sanitizeUrl(url: any): string | null {
    if (!this.isValidUrl(url)) {
      return null;
    }
    return url;
  }

  // Check if content is safe
  isContentSafe(content: any): boolean {
    if (typeof content !== 'string') {
      return true; // Non-string content is considered safe by default
    }

    // Check for dangerous patterns
    for (const pattern of this.dangerousPatterns) {
      if (pattern.test(content)) {
        return false;
      }
    }

    return true;
  }
}

// Create a singleton instance
const sanitizationService = new SanitizationService();

// Export the singleton instance
export default sanitizationService;