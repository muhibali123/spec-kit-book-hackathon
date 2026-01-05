# Data Model: Embeddings Generation (Cohere)

**Feature**: 1-embeddings-generation
**Created**: 2025-12-14

## Input Chunk Entity

**Description**: Represents a content chunk from Module 01

**Fields**:
- `chunk_id` (string): Unique identifier for the chunk, preserved throughout the process
- `text` (string): Original content text that must remain unchanged
- `metadata` (object): Arbitrary metadata structure from Module 01 containing fields like:
  - `chapter_number` (number, optional): Chapter identifier
  - `title` (string, optional): Section title
  - `section_heading` (string, optional): Section heading
  - Additional arbitrary fields as provided by Module 01

**Validation Rules**:
- `chunk_id` must be non-empty string
- `text` must be non-empty string
- `metadata` must be a valid JSON object (can be empty)

## Embedding Record Entity

**Description**: Represents a content chunk with its generated embedding vector

**Fields**:
- `chunk_id` (string): Matches the input chunk_id exactly
- `embedding` (number[]): Numerical vector from Cohere API, dimensions vary by model
- `text` (string): Original content text, preserved unchanged from input
- `metadata` (object): Preserved exactly from input chunk
- `embedding_model` (string): Name of the Cohere model used (e.g., 'embed-english-v3.0')
- `embedding_dimension` (number): Dimension count of the embedding vector

**Validation Rules**:
- `chunk_id` must match input exactly
- `embedding` must be a non-empty array of numbers
- `text` must match input exactly (integrity check)
- `metadata` must match input exactly (integrity check)
- `embedding_model` must be a valid Cohere model identifier
- `embedding_dimension` must match actual embedding array length

## Processing State Entity

**Description**: Tracks the state of embedding generation process

**Fields**:
- `process_id` (string): Unique identifier for the embedding process
- `input_count` (number): Total number of input chunks
- `processed_count` (number): Number of chunks successfully processed
- `failed_count` (number): Number of chunks that failed processing
- `start_time` (string): ISO timestamp when process started
- `end_time` (string): ISO timestamp when process completed
- `status` (string): Current status ('running', 'completed', 'failed')

**Validation Rules**:
- `input_count` must be >= 0
- `processed_count` + `failed_count` <= `input_count`
- `status` must be one of allowed values