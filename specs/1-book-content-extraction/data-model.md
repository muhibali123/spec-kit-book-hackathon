# Data Model: Book Content Extraction & Structuring

## Entity: ContentChunk
**Description**: Represents a segment of processed book content with cleaned text and associated metadata

**Fields**:
- `chunk_id`: string (globally unique identifier)
  - Validation: Must be unique across all chunks in the system
  - Generation: Hash-based with chapter and position identifiers
- `text`: string (cleaned content chunk)
  - Validation: Must not be empty, must preserve semantic meaning
  - Constraints: Should be between 300-500 words (with flexibility for sentence boundaries)
- `chapter_number`: string (e.g., "chapter-03")
  - Validation: Must match the chapter directory naming convention
- `title`: string (chapter or document title)
  - Validation: Must not be empty
- `section_heading`: string (optional, current section heading)
  - Validation: May be null/empty if no heading applies
- `source_file`: string (relative path to source file)
  - Validation: Must be a valid relative path within the project
- `source_url`: string (URL-friendly path for frontend reference)
  - Validation: Must be URL-safe and follow standard URL conventions
- `order_index`: integer (position to preserve reading order)
  - Validation: Must be unique within the book and sequential

## Entity: ChapterData
**Description**: Represents an individual chapter with its structural hierarchy and content organization

**Fields**:
- `chapter_id`: string (unique identifier for the chapter)
  - Validation: Must be unique within the book
  - Generation: Based on directory name
- `title`: string (chapter title)
  - Validation: Must not be empty
- `path`: string (path to chapter directory)
  - Validation: Must be a valid directory path
- `files`: array of strings (list of markdown files in the chapter)
  - Validation: Each entry must be a valid file path
- `order`: integer (position in the book sequence)
  - Validation: Must be unique and sequential across chapters

## Entity: ProcessedBook
**Description**: Represents the complete processed book content as a collection of ContentChunks in the correct reading order

**Fields**:
- `chapters`: array of ChapterData entities
  - Validation: Must maintain proper ordering
- `chunks`: array of ContentChunk entities in reading order
  - Validation: Must be ordered by order_index, all required fields present
- `metadata`: object (processing metadata)
  - Sub-fields:
    - `processed_at`: ISO date string (when processing was completed)
    - `total_chunks`: integer (total number of chunks generated)
    - `total_words`: integer (total word count across all chunks)
    - `processing_time_ms`: integer (time taken to process in milliseconds)

## Relationships
- One ProcessedBook contains many ChapterData entities (1 to many)
- One ChapterData contains many ContentChunk entities (1 to many)
- All ContentChunk entities belong to one ProcessedBook (many to 1)

## Validation Rules from Requirements
- Each ContentChunk must have all required metadata fields present (FR-007)
- ContentChunk text must not be empty and must preserve semantic meaning (FR-011)
- Chunk IDs must be globally unique (FR-006)
- Chunks must be ordered correctly to preserve reading sequence (FR-007)
- Output must be deterministic (FR-009)
- All Markdown files in /chapters/**/* must be processed (FR-001)

## State Transitions
- ContentChunk: [CREATED] → [CLEANED] → [CHUNKED] → [METADATA_ATTACHED] → [VALIDATED]
- ChapterData: [DISCOVERED] → [READ] → [PROCESSED] → [ORDERED]
- ProcessedBook: [INITIALIZED] → [PROCESSING] → [COMPLETED] → [VALIDATED]