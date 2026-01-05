// API client service following contracts/api-contracts.md
import { QueryRequest, QueryResponse, HealthCheckResponse, AnswerResponse } from './types';

const API_BASE_URL = 'http://localhost:8000'; // Backend server URL
const DEFAULT_TIMEOUT = 30000; // 30 seconds

class ApiClient {
  private baseURL: string;
  private timeout: number;

  constructor(baseURL: string = API_BASE_URL, timeout: number = DEFAULT_TIMEOUT) {
    this.baseURL = baseURL;
    this.timeout = timeout;
  }

  // Create a timeout promise
  private createTimeoutPromise(timeout: number): Promise<never> {
    return new Promise((_, reject) => {
      setTimeout(() => reject(new Error('CONNECTION_TIMEOUT')), timeout);
    });
  }

  // Method to submit a query to the RAG agent with retry mechanism and timeout
  async submitQuery(query: string, conversationId: string | null = null, context: any = null, maxRetries: number = 3): Promise<AnswerResponse> {
    let lastError: any;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const requestBody: QueryRequest = {
          query,
          conversationId,
        };

        // Include context if provided (e.g., previous conversation history)
        if (context) {
          (requestBody as any).context = context;
        }

        // Create the fetch request with a timeout using Promise.race
        const fetchPromise = fetch(`${this.baseURL}/v1/answer`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        });

        const response = await Promise.race([
          fetchPromise,
          this.createTimeoutPromise(this.timeout)
        ]);

        // Read the response body once since Response body can only be consumed once
        const responseBody = await response.text();
        const responseJson = JSON.parse(responseBody);

        if (!response.ok) {
          let errorMessage = `API request failed with status ${response.status}`;

          if (responseJson.message) {
            errorMessage += `: ${responseJson.message}`;
          }

          // Don't retry for client errors (4xx)
          if (response.status >= 400 && response.status < 500) {
            throw new Error(errorMessage);
          }

          throw new Error(errorMessage);
        }

        return responseJson;
      } catch (error) {
        lastError = error;
        console.error(`API request attempt ${attempt + 1} failed:`, error);

        // Check if the error is a timeout
        if (error.message === 'CONNECTION_TIMEOUT') {
          console.error(`Request timed out after ${this.timeout}ms`);
          throw new Error('CONNECTION_TIMEOUT');
        }

        // For network errors or server errors (5xx), retry with exponential backoff
        if (attempt < maxRetries) {
          // Exponential backoff: wait 1s, 2s, 4s, etc.
          const delay = Math.pow(2, attempt) * 1000;
          console.log(`Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    // If all retries failed, throw the last error
    console.error('All retry attempts failed');
    throw lastError;
  }

  // Method to check API health
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/v1/health`);
      return response.ok;
    } catch (error) {
      console.error('Health check error:', error);
      return false;
    }
  }
}

export default ApiClient;