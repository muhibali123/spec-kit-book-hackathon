# Quickstart: Embeddings Generation (Cohere)

**Feature**: 1-embeddings-generation
**Created**: 2025-12-14

## Prerequisites

- Node.js 18+ installed
- Cohere API key
- Module 01 output files (structured JSON chunks)

## Setup

1. **Install Dependencies**
   ```bash
   cd /backend
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your COHERE_API_KEY
   ```

3. **Prepare Input Data**
   - Ensure Module 01 output is in JSON format with chunks containing `chunk_id`, `text`, and `metadata`

## Usage

### Command Line
```bash
cd /backend
npm run generate-embeddings -- --input=/path/to/module01-output.json --output=/path/to/embeddings-output.json
```

### Configuration Options
- `--model`: Cohere model to use (default: 'embed-english-v3.0')
- `--batch-size`: Batch size for API calls (default: 64)
- `--max-retries`: Maximum retry attempts (default: 3)

### Programmatic Usage
```javascript
import { EmbeddingGenerator } from './src/embeddings/generator';

const generator = new EmbeddingGenerator({
  apiKey: process.env.COHERE_API_KEY,
  model: 'embed-english-v3.0',
  batchSize: 64
});

const chunks = [/* Module 01 output */];
const results = await generator.generateEmbeddings(chunks);
```

## Output Format

The service produces a JSON file containing an array of embedding records:

```json
[
  {
    "chunk_id": "unique-identifier-from-module01",
    "embedding": [0.123, -0.456, 0.789, /* ... more numbers ... */],
    "text": "original content text preserved",
    "metadata": { /* original metadata preserved */ },
    "embedding_model": "embed-english-v3.0",
    "embedding_dimension": 1024
  }
]
```

## Monitoring

- Check logs in `/backend/logs/embeddings-generation.log`
- Monitor processing progress via console output
- Verify output file integrity after completion