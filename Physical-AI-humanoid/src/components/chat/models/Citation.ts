// Citation entity model following data-model.md specifications
import { Citation as CitationType } from '../types';

export class Citation implements CitationType {
  id: string;
  source: string;
  page?: number | null;
  section?: string;
  content: string;
  url?: string | null;
  documentId?: string | null;

  constructor({ id, source, page, section, content, url = null, documentId = null }: Partial<CitationType> & { source: string; content: string }) {
    this.id = id || this.generateId();
    this.source = source; // Name of the source document
    this.page = page; // Page number if applicable
    this.section = section; // Section title if applicable
    this.content = content; // Snippet of the cited content
    this.url = url; // URL to the source if available
    this.documentId = documentId; // ID of the source document
  }

  generateId(): string {
    return 'cit_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // Validate the citation object
  static validate(citation: Partial<CitationType>): boolean {
    if (!citation.source || typeof citation.source !== 'string') {
      throw new Error('Citation source is required and must be a string');
    }

    if (!citation.content || typeof citation.content !== 'string') {
      throw new Error('Citation content is required and must be a string');
    }

    if (citation.page !== undefined && citation.page !== null && typeof citation.page !== 'number') {
      throw new Error('Citation page must be a number if provided');
    }

    if (citation.section && typeof citation.section !== 'string') {
      throw new Error('Citation section must be a string if provided');
    }

    if (citation.url && typeof citation.url !== 'string') {
      throw new Error('Citation URL must be a string if provided');
    }

    if (citation.documentId && typeof citation.documentId !== 'string') {
      throw new Error('Citation documentId must be a string if provided');
    }

    return true;
  }

  // Create a new citation instance from raw data
  static fromData(data: Partial<CitationType> & { source: string; content: string }): Citation {
    this.validate(data);
    return new Citation(data);
  }

  // Convert citation to plain object for serialization
  toJSON(): CitationType {
    return {
      id: this.id,
      source: this.source,
      page: this.page,
      section: this.section,
      content: this.content,
      url: this.url,
      documentId: this.documentId
    };
  }
}