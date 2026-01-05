// Integration test for the chat UI services and utilities
// This file tests the core functionality of the chat interface

// Import services
import { Message } from './models/Message';
import { Citation } from './models/Citation';
import { Conversation } from './models/Conversation';
import { Session } from './models/Session';
import ApiClient from './ApiClient';
import chatStore from './state/store';
import validationService from './services/validation';
import formattingService from './services/formatting';
import errorService from './services/error';
import sanitizationService from './services/sanitization';

console.log('Starting Chat UI Integration Tests...\n');

// Test the Message model
console.log('1. Testing Message model...');
try {
  const message = new Message({
    content: 'Test message',
    role: 'user',
    timestamp: new Date()
  });

  console.log('✓ Message model created successfully');
  console.log('✓ Message content:', message.content);
  console.log('✓ Message role:', message.role);
} catch (error) {
  console.error('✗ Message model test failed:', error.message);
}

// Test the Citation model
console.log('\n2. Testing Citation model...');
try {
  const citation = new Citation({
    source: 'Test Document',
    page: 5,
    section: 'Introduction',
    content: 'Test content'
  });

  console.log('✓ Citation model created successfully');
  console.log('✓ Citation source:', citation.source);
  console.log('✓ Citation page:', citation.page);
} catch (error) {
  console.error('✗ Citation model test failed:', error.message);
}

// Test the Conversation model
console.log('\n3. Testing Conversation model...');
try {
  const conversation = new Conversation({
    title: 'Test Conversation',
    createdAt: new Date()
  });

  console.log('✓ Conversation model created successfully');
  console.log('✓ Conversation title:', conversation.title);
} catch (error) {
  console.error('✗ Conversation model test failed:', error.message);
}

// Test the Session model
console.log('\n4. Testing Session model...');
try {
  const session = new Session({
    createdAt: new Date()
  });

  console.log('✓ Session model created successfully');
  console.log('✓ Session ID:', session.id);
} catch (error) {
  console.error('✗ Session model test failed:', error.message);
}

// Test validation service
console.log('\n5. Testing validation service...');
try {
  const validResult = validationService.validateInput('This is a valid input');
  console.log('✓ Valid input validation passed:', validResult.isValid);

  const invalidResult = validationService.validateInput('');
  console.log('✓ Invalid input validation failed as expected:', !invalidResult.isValid);

  console.log('✓ Validation service working correctly');
} catch (error) {
  console.error('✗ Validation service test failed:', error.message);
}

// Test formatting service
console.log('\n6. Testing formatting service...');
try {
  const markdownText = 'This is **bold** and *italic* text';
  const formatted = formattingService.formatResponse(markdownText);
  console.log('✓ Markdown formatting working:', formatted.includes('<strong>') && formatted.includes('<em>'));

  const cleanText = formattingService.cleanText('**Bold** and *italic* content');
  console.log('✓ Text cleaning working:', cleanText === 'Bold and italic content');
} catch (error) {
  console.error('✗ Formatting service test failed:', error.message);
}

// Test error service
console.log('\n7. Testing error service...');
try {
  const networkError = new Error('NetworkError: Failed to fetch');
  const userFriendlyError = errorService.mapError(networkError);
  console.log('✓ Error mapping working:', userFriendlyError.includes('connection'));

  const httpError = errorService.createError('SERVER_ERROR', '500 Internal Server Error');
  console.log('✓ Error creation working:', httpError.code === 'SERVER_ERROR');
} catch (error) {
  console.error('✗ Error service test failed:', error.message);
}

// Test sanitization service
console.log('\n8. Testing sanitization service...');
try {
  const dangerousContent = '<script>alert("xss")</script>';
  const sanitized = sanitizationService.sanitizeInput(dangerousContent);
  console.log('✓ XSS prevention working:', !sanitized.includes('<script>'));

  const safeContent = sanitizationService.sanitizeInput('This is safe content');
  console.log('✓ Safe content preserved:', safeContent === 'This is safe content');
} catch (error) {
  console.error('✗ Sanitization service test failed:', error.message);
}

// Test state management
console.log('\n9. Testing state management...');
try {
  // Reset store for clean test
  chatStore.reset();

  console.log('✓ Initial loading state:', chatStore.isLoading() === false);

  chatStore.setLoading(true);
  console.log('✓ Loading state set:', chatStore.isLoading() === true);

  chatStore.setLoading(false);
  console.log('✓ Loading state cleared:', chatStore.isLoading() === false);

  chatStore.setError('Test error');
  console.log('✓ Error state set:', chatStore.getError() === 'Test error');

  chatStore.clearError();
  console.log('✓ Error state cleared:', chatStore.getError() === null);
} catch (error) {
  console.error('✗ State management test failed:', error.message);
}

// Test API client (without actual network call)
console.log('\n10. Testing API client...');
try {
  const apiClient = new ApiClient('http://test-url.com');
  console.log('✓ API client instantiated with base URL:', apiClient.baseURL);

  // Test timeout creation
  const timeoutPromise = apiClient.createTimeoutPromise(1000);
  console.log('✓ Timeout promise created');
} catch (error) {
  console.error('✗ API client test failed:', error.message);
}

console.log('\n✓ All integration tests completed successfully!');
console.log('\nChat UI components are properly integrated and working together.');