// Error mapping service for user-friendly messages
interface ErrorMappings {
  [key: string]: string;
  [key: number]: string;
}

interface StandardizedError {
  code: string;
  message: string;
  title: string;
  isRetryable: boolean;
  details: any;
  timestamp: string;
}

class ErrorService {
  private errorMappings: ErrorMappings;

  constructor() {
    // Define error mappings
    this.errorMappings = {
      // Network errors
      'NetworkError': 'Network error: Unable to connect to the server. Please check your connection.',
      'TypeError': 'Connection error: Unable to reach the server. Please try again.',

      // HTTP status codes
      400: 'Bad request: The request was invalid. Please try rephrasing your question.',
      401: 'Unauthorized: Please log in to continue.',
      403: 'Forbidden: You do not have permission to access this resource.',
      404: 'Not found: The requested resource could not be found.',
      429: 'Too many requests: Please wait before trying again.',
      500: 'Server error: Something went wrong on our end. Please try again later.',
      502: 'Server error: The server is temporarily unavailable. Please try again.',
      503: 'Service unavailable: The server is currently busy. Please try again later.',
      504: 'Gateway timeout: The server took too long to respond. Please try again.',

      // Custom application errors
      'CONNECTION_TIMEOUT': 'Connection timeout: The server is taking too long to respond. Please try again.',
      'RATE_LIMIT_EXCEEDED': 'Rate limit exceeded: Please wait before submitting another question.',
      'BACKEND_SERVICE_UNAVAILABLE': 'Service unavailable: The backend service is currently down. Please try again later.',
      'INVALID_INPUT': 'Invalid input: Please make sure your question is properly formatted.',
      'EMPTY_INPUT': 'Empty input: Please enter a question before submitting.',
      'MAX_LENGTH_EXCEEDED': 'Input too long: Please shorten your question and try again.',
      'SESSION_EXPIRED': 'Session expired: Please refresh the page to continue.',
      'CONVERSATION_NOT_FOUND': 'Conversation not found: Starting a new conversation.',
      'EC-001': 'Backend service unavailable: The RAG Agent service is currently down. Please try again later.',
      'EC-002': 'Rate limit exceeded: You have sent too many requests. Please wait before submitting another question.',
      'EC-004': 'Invalid or empty input: Please enter a valid question before submitting.',
      'EC-006': 'Network timeout: The connection to the server timed out. Please check your network connection and try again.',
    };
  }

  // Map an error to a user-friendly message
  mapError(error: any): string {
    // If it's already a user-friendly message, return it
    if (typeof error === 'string') {
      return error;
    }

    // If it's an Error object
    if (error instanceof Error) {
      // Check for specific error types
      if (error.message.includes('NetworkError') || error.message.includes('fetch failed')) {
        return this.errorMappings['NetworkError'];
      }

      if (error.message.includes('TypeError')) {
        return this.errorMappings['TypeError'];
      }

      // Check if the error message contains an HTTP status code
      const statusCodeMatch = error.message.match(/status (\d{3})/);
      if (statusCodeMatch) {
        const statusCode = parseInt(statusCodeMatch[1]);
        if (this.errorMappings[statusCode]) {
          return this.errorMappings[statusCode];
        }
      }

      // Return the original error message if no mapping found
      return error.message || 'An unknown error occurred. Please try again.';
    }

    // If it's a response-like object with status
    if (error && typeof error === 'object' && error.status) {
      const status = parseInt(error.status);
      if (this.errorMappings[status]) {
        return this.errorMappings[status];
      }
    }

    // Default fallback
    return 'An unexpected error occurred. Please try again.';
  }

  // Get error title for display
  getErrorTitle(error: any): string {
    if (typeof error === 'string') {
      if (error.includes('Network') || error.includes('Connection')) {
        return 'Connection Error';
      } else if (error.includes('Rate') || error.includes('limit')) {
        return 'Rate Limit Error';
      } else if (error.includes('Server') || error.includes('service')) {
        return 'Service Error';
      } else if (error.includes('Invalid') || error.includes('Bad request')) {
        return 'Input Error';
      }
    }

    return 'Error';
  }

  // Check if an error is retryable
  isRetryable(error: any): boolean {
    // If it's a string error message
    if (typeof error === 'string') {
      return (
        error.includes('Network') ||
        error.includes('Connection') ||
        error.includes('timeout') ||
        error.includes('Server error') ||
        error.includes('Service unavailable') ||
        error.includes('Gateway timeout')
      );
    }

    // If it's an Error object
    if (error instanceof Error) {
      // Check for network-related errors
      if (error.message.includes('NetworkError') || error.message.includes('fetch failed')) {
        return true;
      }

      // Check for specific status codes that are retryable
      const statusCodeMatch = error.message.match(/status (\d{3})/);
      if (statusCodeMatch) {
        const statusCode = parseInt(statusCodeMatch[1]);
        // Retry on 5xx server errors and some 4xx errors
        return statusCode >= 500 || statusCode === 429 || statusCode === 408;
      }
    }

    return false;
  }

  // Create a standardized error object
  createError(code: string, message: any, details: any = null): StandardizedError {
    return {
      code,
      message: this.mapError(message),
      title: this.getErrorTitle(message),
      isRetryable: this.isRetryable(message),
      details,
      timestamp: new Date().toISOString()
    };
  }

  // Handle API error response
  handleApiError(response: any): StandardizedError | null {
    if (response.status >= 500) {
      return this.createError(
        'SERVER_ERROR',
        this.errorMappings[response.status] || `Server error: ${response.status}`
      );
    } else if (response.status === 429) {
      return this.createError(
        'RATE_LIMIT',
        this.errorMappings[429]
      );
    } else if (response.status >= 400) {
      return this.createError(
        'CLIENT_ERROR',
        this.errorMappings[response.status] || `Client error: ${response.status}`
      );
    }

    return null; // Not an error that needs special handling
  }
}

// Create a singleton instance
const errorService = new ErrorService();

// Export the singleton instance
export default errorService;