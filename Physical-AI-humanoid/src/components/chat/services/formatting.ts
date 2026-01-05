// Response formatting service for AI responses
import { Citation } from '../types';

interface FormattingPatterns {
  bold: RegExp;
  italic: RegExp;
  code: RegExp;
  link: RegExp;
  lineBreak: RegExp;
  paragraph: RegExp;
  header: RegExp;
}

class FormattingService {
  private patterns: FormattingPatterns;

  constructor() {
    // Define supported formatting patterns
    this.patterns = {
      // Bold: **text** or __text__
      bold: /\*\*(.*?)\*\*|__(.*?)__/g,
      // Italic: *text* or _text_ (not adjacent to other underscores)
      italic: /(?<!\*)\*([^\*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)/g,
      // Code: `code`
      code: /`(.*?)`/g,
      // Links: [text](url)
      link: /\[([^\]]+)\]\(([^)]+)\)/g,
      // Line breaks: two spaces at the end of a line
      lineBreak: / {2}\n/g,
      // Paragraphs: double newlines
      paragraph: /\n\s*\n/g,
      // Headers: # Header
      header: /^(#{1,6})\s+(.*?)$/gm,
    };
  }

  // Format text with markdown-like syntax
  formatText(text: any): string {
    if (typeof text !== 'string') {
      return text;
    }

    let formattedText = text;

    // Handle headers first
    formattedText = formattedText.replace(this.patterns.header, (match, hashes, content) => {
      const level = hashes.length;
      return `<h${level}>${content}</h${level}>`;
    });

    // Handle line breaks
    formattedText = formattedText.replace(this.patterns.lineBreak, '<br>');

    // Handle paragraphs
    formattedText = formattedText.replace(this.patterns.paragraph, '</p><p>');

    // Handle bold
    formattedText = formattedText.replace(this.patterns.bold, (match, p1, p2) => {
      const content = p1 || p2;
      return `<strong>${content}</strong>`;
    });

    // Handle italic
    formattedText = formattedText.replace(this.patterns.italic, (match, p1, p2) => {
      const content = p1 || p2;
      return `<em>${content}</em>`;
    });

    // Handle code
    formattedText = formattedText.replace(this.patterns.code, (match, content) => {
      return `<code>${this.escapeHtml(content)}</code>`;
    });

    // Handle links
    formattedText = formattedText.replace(this.patterns.link, (match, text, url) => {
      return `<a href="${this.escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${this.escapeHtml(text)}</a>`;
    });

    // Wrap in paragraph tags if not already wrapped
    if (!formattedText.startsWith('<') && !formattedText.endsWith('>')) {
      formattedText = `<p>${formattedText}</p>`;
    }

    // Replace any remaining newlines with line breaks
    formattedText = formattedText.replace(/\n/g, '<br>');

    return formattedText;
  }

  // Escape HTML to prevent XSS
  escapeHtml(text: any): string {
    if (typeof text !== 'string') {
      return text;
    }
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Format a complete response with paragraphs and line breaks
  formatResponse(response: any): string {
    if (typeof response !== 'string') {
      return response;
    }

    // First escape HTML to prevent XSS
    let safeResponse = this.escapeHtml(response);

    // Then apply formatting
    // Split by paragraphs (double newlines)
    const paragraphs = safeResponse.split(/\n\s*\n/);

    // Format each paragraph
    const formattedParagraphs = paragraphs.map(paragraph => {
      if (paragraph.trim() === '') return '';

      // Format the paragraph content
      let formatted = paragraph;

      // Handle bold
      formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      formatted = formatted.replace(/__(.*?)__/g, '<strong>$1</strong>');

      // Handle italic
      formatted = formatted.replace(/(?<!\*)\*([^\*]+)\*(?!\*)/g, '<em>$1</em>');
      formatted = formatted.replace(/(?<!_)_([^_]+)_(?!_)/g, '<em>$1</em>');

      // Handle code
      formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');

      // Handle links
      formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

      // Handle single newlines as line breaks
      formatted = formatted.replace(/\n/g, '<br>');

      return `<p>${formatted}</p>`;
    });

    return formattedParagraphs.join('');
  }

  // Clean text by removing markdown-like syntax
  cleanText(text: any): string {
    if (typeof text !== 'string') {
      return text;
    }

    let cleanedText = text;

    // Remove bold markers
    cleanedText = cleanedText.replace(/\*\*(.*?)\*\*/g, '$1');
    cleanedText = cleanedText.replace(/__(.*?)__/g, '$1');

    // Remove italic markers
    cleanedText = cleanedText.replace(/\*([^*]+)\*/g, '$1');
    cleanedText = cleanedText.replace(/_([^_]+)_/g, '$1');

    // Remove code markers
    cleanedText = cleanedText.replace(/`(.*?)`/g, '$1');

    // Remove link markers
    cleanedText = cleanedText.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

    // Remove headers
    cleanedText = cleanedText.replace(/^#{1,6}\s+(.*?)$/gm, '$1');

    return cleanedText;
  }

  // Format citations in a user-friendly way
  formatCitations(citations: any[]): any[] {
    if (!Array.isArray(citations)) {
      return [];
    }

    return citations.map(citation => ({
      ...citation,
      content: this.cleanText(citation.content || ''),
      source: this.cleanText(citation.source || '')
    }));
  }
}

// Create a singleton instance
const formattingService = new FormattingService();

// Export the singleton instance
export default formattingService;