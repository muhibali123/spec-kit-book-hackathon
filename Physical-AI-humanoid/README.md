# AI Knowledge Assistant - Chat Interface

This project implements an AI-powered chat interface integrated into the Docusaurus documentation website. The chat interface allows users to ask questions and receive answers from the knowledge base with proper citations and source references.

## Features

- Multi-turn conversations with context preservation
- AI-generated answers with citations and source references
- Loading indicators for processing states
- Error handling with user-friendly messages
- Responsive design for all device sizes
- Accessibility features (WCAG 2.1 AA compliant)

## Prerequisites

- Node.js (version 20 or higher)
- npm or yarn package manager

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Physical-AI-humanoid
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with the following content:
   ```
   RAG_AGENT_API_URL=http://localhost:8000
   ```
   Replace `http://localhost:8000` with the actual URL of your Module 05 RAG Agent API.

4. Start the development server:
   ```bash
   npm start
   # or
   yarn start
   ```

5. The chat interface will be available at `http://localhost:3000/chat`

## Development

To run the project in development mode:
```bash
npm start
```

To build the project for production:
```bash
npm run build
```

To serve the built project locally:
```bash
npm run serve
```

## API Integration

The chat interface connects to the Module 05 RAG Agent API. The API endpoints used are:

- `POST /api/v1/query` - Submit a query and receive an answer with citations
- `GET /health` - Check the health status of the API

## Architecture

The chat interface follows a component-based architecture:

- `ChatContainer.js` - Main container component managing state and API communication
- `MessageList.js` - Component for displaying conversation history
- `InputArea.js` - Component for user input with validation
- `UserMessage.js` - Component for displaying user messages
- `AIMessage.js` - Component for displaying AI responses with citations
- `LoadingIndicator.js` - Component for showing loading states
- `ErrorMessage.js` - Component for displaying error messages

## Testing

To run the test suite:
```bash
npm test
# or
yarn test
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
