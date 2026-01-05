# Implementation Plan: Book Content Extraction & Structuring

**Feature**: 1-book-content-extraction
**Created**: 2025-12-13
**Status**: Draft
**Plan Stage**: Implementation Plan

## Technical Context

This module implements the Book Content Extraction & Structuring functionality as specified. The system will transform raw Markdown chapter files from the `/chapters` directory into clean, structured, and chunked data suitable for a RAG pipeline.

**Key Technologies**: Markdown parsing, text processing, JSON serialization
**Input**: Markdown files in `/chapters/**/*` directory structure
**Output**: Structured JSON data with content chunks and metadata
**Constraints**: Must not generate embeddings, use vector databases, call LLMs, or implement retrieval logic

## Architecture Decision Records (ADRs)

### ADR-001: Content Processing Pipeline Architecture
- **Decision**: Implement a sequential pipeline architecture with distinct phases for discovery, cleaning, chunking, and metadata attachment
- **Rationale**: Provides clear separation of concerns, testability, and maintainability
- **Status**: Pending

### ADR-002: Markdown Parsing Technology
- **Decision**: Use established Markdown parsing libraries to handle complex formatting
- **Rationale**: Ensures proper handling of edge cases and maintains semantic meaning
- **Status**: Pending

## Data Model

### ContentChunk Entity
- `chunk_id`: globally unique identifier (string)
- `text`: cleaned content chunk (string)
- `chapter_number`: identifier for the chapter (string, e.g., "chapter-03")
- `title`: chapter or document title (string)
- `section_heading`: current section heading if available (string, optional)
- `source_file`: relative path to source file (string)
- `source_url`: URL-friendly path for frontend reference (string)
- `order_index`: index to preserve reading order (integer)

### ChapterData Entity
- `chapter_id`: unique identifier for the chapter (string)
- `title`: chapter title (string)
- `path`: path to chapter directory (string)
- `files`: list of markdown files in the chapter (array of strings)
- `order`: position in the book sequence (integer)

### ProcessedBook Entity
- `chapters`: array of ChapterData entities
- `chunks`: array of ContentChunk entities in reading order
- `metadata`: processing metadata (object)

## System Architecture

### Processing Pipeline
```
[File Discovery] → [Content Reading] → [Cleaning] → [Chunking] → [Metadata Attachment] → [Output Generation]
```

1. **File Discovery Module**: Discovers chapter folders and Markdown files in `/chapters/**/*`
2. **Content Reading Module**: Reads and orders files based on directory structure
3. **Cleaning Module**: Removes navigation/UI elements and processes Markdown syntax
4. **Chunking Module**: Segments content into logical units of 300-500 words
5. **Metadata Module**: Attaches required metadata to each chunk
6. **Output Module**: Generates structured JSON output

## API Contracts

### Processing Interface
- **Function**: `processBookContent(inputDirectory: string, outputFormat: string): ProcessedBook`
- **Input**: Path to the directory containing `/chapters` subdirectory
- **Output**: ProcessedBook object with structured content chunks
- **Error Handling**: Detailed error reporting for malformed files or processing failures

### Chunk Generation Interface
- **Function**: `generateChunks(content: string, metadata: object): ContentChunk[]`
- **Input**: Raw content string and associated metadata
- **Output**: Array of ContentChunk objects
- **Responsibility**: Apply chunking rules and generate appropriate metadata

## Implementation Phases

### Phase 1: File Discovery and Reading
**Objective**: Implement discovery and reading of Markdown files from the `/chapters` directory structure.

**Tasks**:
1. Traverse `/chapters/**/*` to identify all chapter directories
2. Identify Markdown files within each chapter directory
3. Establish proper ordering based on directory naming conventions (e.g., chapter-01, chapter-02)
4. Read content from each Markdown file while preserving file metadata

**Deliverables**:
- File discovery utility
- Content reading module
- Chapter ordering mechanism

### Phase 2: Content Cleaning
**Objective**: Implement cleaning of raw Markdown content according to specified rules.

**Tasks**:
1. Remove navigation, UI, and layout-related text elements
2. Process Markdown syntax to preserve semantic meaning
3. Extract headings for use as metadata only
4. Preserve code blocks, tables, and other meaningful content

**Deliverables**:
- Content cleaning module
- Markdown processing utilities
- Semantic preservation mechanisms

### Phase 3: Content Chunking
**Objective**: Implement logical segmentation of content into chunks of 300-500 words.

**Tasks**:
1. Identify logical section breaks based on headings and paragraph structure
2. Implement chunking algorithm that respects sentence boundaries
3. Ensure chunks are self-contained and meaningful
4. Handle edge cases like large sections without headings

**Deliverables**:
- Chunking algorithm
- Boundary detection utilities
- Chunk validation mechanisms

### Phase 4: Metadata Attachment
**Objective**: Attach required metadata to each content chunk.

**Tasks**:
1. Generate globally unique chunk IDs
2. Extract and attach chapter numbers, titles, and section headings
3. Generate source file paths and URL-friendly references
4. Assign order indices to preserve reading sequence

**Deliverables**:
- Metadata generation module
- ID generation utilities
- Path processing utilities

### Phase 5: Output Generation and Validation
**Objective**: Generate final structured output and validate against requirements.

**Tasks**:
1. Serialize processed chunks to JSON format
2. Validate output against schema requirements
3. Implement deterministic processing for consistent results
4. Generate processing reports and metrics

**Deliverables**:
- Output generation module
- Validation utilities
- Processing reports

## Security Considerations

- Input validation: Validate file paths to prevent directory traversal attacks
- Content sanitization: Ensure no malicious content is preserved during cleaning
- Output validation: Verify generated content meets security requirements

## Performance Requirements

- Process a typical book (10 chapters with ~1000 words each) in under 30 seconds
- Maintain consistent performance across varying content structures
- Efficient memory usage during processing of large files

## Quality Assurance

### Testing Strategy
- Unit tests for each processing module
- Integration tests for the complete pipeline
- Validation tests for output format compliance
- Edge case testing for various content structures

### Validation Checks
- 100% of required metadata fields present in output chunks
- Average chunk size between 300-500 words
- No meaningful content loss during processing
- Deterministic output across multiple runs

## Deployment and Operations

### Configuration
- Input directory path specification
- Output format options (JSON structure)
- Processing options (chunk size ranges, cleaning rules)

### Monitoring
- Processing time metrics
- File processing success/failure rates
- Output quality metrics
- Error logging and reporting

## Risk Analysis

### Technical Risks
- Complex Markdown syntax may not parse correctly
- Large files may cause memory issues
- Inconsistent chapter structures may affect chunking quality

### Mitigation Strategies
- Use robust Markdown parsing libraries
- Implement streaming processing for large files
- Develop flexible chunking algorithms that handle various structures