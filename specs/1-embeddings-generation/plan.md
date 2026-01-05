# Implementation Plan: Embeddings Generation (Cohere)

**Feature**: 1-embeddings-generation
**Created**: 2025-12-14
**Status**: Draft
**Branch**: 1-embeddings-generation

## Technical Context

This module converts structured book content chunks from Module 01 into vector embeddings using the Cohere Embeddings API. The system follows a clean, production-quality backend design with separation of concerns and proper error handling.

**Key Technologies**:
- Cohere Embeddings API
- Environment-based configuration
- Batch processing for efficiency
- Deterministic and auditable processes

**Unknowns**:
- None (all previously identified unknowns resolved in research phase)

## Constitution Check

Based on `.specify/memory/constitution.md`, this plan aligns with:
- Clean architecture principles
- Separation of concerns
- Production-quality backend design
- Environment-based configuration
- Error handling and observability

## Gates

- [x] Scope alignment: Module handles only embedding generation, no database storage or retrieval
- [x] Architecture: Clean separation of concerns with proper layers
- [x] Security: Environment-based configuration for API keys
- [x] Quality: Deterministic and auditable processes
- [x] Performance: Batch processing for efficiency

## Phase 0: Research

### Research Tasks

1. **Cohere Embedding Model Selection**:
   - Research: Determine optimal Cohere embedding model for book content
   - Rationale: Need to select model that balances quality and cost for text content
   - Alternatives: `embed-english-v3.0`, `embed-multilingual-v3.0`, etc.

2. **Batch Processing Strategy**:
   - Research: Optimal batch size for Cohere API calls
   - Rationale: Balance efficiency with API rate limits
   - Alternatives: Different batch sizes (10, 50, 100, etc.)

3. **API Rate Limit Handling**:
   - Research: Cohere API rate limits and best practices
   - Rationale: Ensure reliable processing without hitting limits
   - Alternatives: Different retry strategies

## Phase 1: Design

### Data Model

#### Input Chunk Entity
- `chunk_id`: string (unique identifier from Module 01)
- `text`: string (original content text, preserved unchanged)
- `metadata`: object (arbitrary metadata from Module 01)

#### Embedding Record Entity
- `chunk_id`: string (matches input)
- `embedding`: number[] (numerical vector from Cohere API)
- `text`: string (original content text, unchanged)
- `metadata`: object (preserved from input)
- `embedding_model`: string (model name used for generation)
- `embedding_dimension`: number (dimensionality of the embedding)

### Processing Flow

1. **Input Validation**: Validate JSON structure from Module 01
2. **Batch Preparation**: Group chunks into optimal batches for API calls
3. **Embedding Generation**: Call Cohere API for each batch
4. **Result Assembly**: Combine embeddings with original data
5. **Output Validation**: Ensure all required fields are present
6. **Export**: Save results in format ready for Module 03

### API Contracts

#### Embedding Generation Service
- **Input**: JSON array of content chunks
- **Output**: JSON array of embedding records
- **Processing**: Transform text → vector embeddings via Cohere API

## Phase 2: Implementation Strategy

### Folder Structure
```
/backend/
├── src/
│   ├── embeddings/
│   │   ├── index.ts                 # Main entry point
│   │   ├── generator.ts            # Core embedding logic
│   │   ├── batch-processor.ts      # Batch handling
│   │   ├── cohere-client.ts        # Cohere API integration
│   │   ├── validator.ts            # Input/output validation
│   │   └── logger.ts               # Logging utilities
│   ├── config/
│   │   └── environment.ts          # Environment configuration
│   ├── types/
│   │   └── embeddings.ts           # Type definitions
│   └── utils/
│       ├── retry.ts                # Retry logic
│       └── file-handler.ts         # File I/O utilities
├── .env.example
└── package.json
```

### Configuration Strategy

#### Environment Variables
- `COHERE_API_KEY`: API key for Cohere service (required)
- `COHERE_MODEL`: Embedding model to use (default: 'embed-english-v3.0')
- `BATCH_SIZE`: Number of chunks per API call (default: 96)
- `MAX_RETRIES`: Maximum retry attempts for failed API calls (default: 3)
- `RETRY_DELAY`: Base delay in ms for retry backoff (default: 1000)

### Embedding Generation Strategy

#### Batch Processing
- Group content chunks into batches of optimal size (≤ 96 items per Cohere's limits)
- Preserve original order to maintain chunk_id → embedding mapping
- Process batches in parallel while respecting rate limits
- Handle partial failures by retrying failed chunks individually

#### Model Consistency
- Use single, configurable model for all embeddings in a run
- Record model name in output for consistency verification
- Record dimension count for downstream validation

### Error Handling & Reliability

#### API Failure Handling
- Implement exponential backoff for rate limit errors
- Retry failed batches with increasing delays
- Log failed chunk IDs for audit trail
- Continue processing other batches during partial failures

#### Validation
- Validate input structure before processing
- Verify output completeness after embedding
- Ensure all chunk IDs are preserved
- Confirm metadata integrity

### Success Criteria

#### Measurable Outcomes
- 100% of input chunks produce valid embedding records
- Process completes within expected time bounds (1000 chunks/hour)
- All original text and metadata preserved unchanged
- API error rate < 5% during normal operation
- Deterministic results when processing same input twice