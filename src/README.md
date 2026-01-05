# Book Content Extraction & Structuring Module

This module implements Module 01 of a Retrieval-Augmented Generation (RAG) chatbot system for a Docusaurus-based book project. It transforms raw Markdown chapter files into clean, structured, and AI-friendly data ready for embedding generation.

## Overview

The module processes book content from the `/chapters` directory, extracting and structuring content according to the following requirements:

- Reads Markdown files from `/chapters/**/*` directory structure
- Cleans unnecessary or non-content elements
- Structures and chunks the book content
- Attaches meaningful metadata to each chunk
- Produces structured JSON output suitable for embedding pipelines

## Features

- **Content Discovery**: Automatically discovers chapter directories and Markdown files
- **Smart Cleaning**: Removes navigation, UI, and layout-related text elements
- **Intelligent Chunking**: Segments content into logical units (300-500 words) while respecting headings and sentence boundaries
- **Metadata Attachment**: Attaches required metadata including chunk_id, text, chapter_number, title, section_heading, source_file, source_url, and order_index
- **Validation**: Ensures all required fields are present and content integrity is maintained
- **Logging**: Comprehensive logging for error tracking and debugging

## Architecture

The module follows a sequential pipeline architecture:

```
[File Discovery] → [Content Reading] → [Cleaning] → [Chunking] → [Metadata Attachment] → [Output Generation]
```

## Usage

### Basic Usage

```python
from src.main_processor import processBookContent, save_processed_book

# Process book content from a directory containing /chapters
processed_book = processBookContent("/path/to/book/project")

# Save the processed output
save_processed_book(processed_book, "output.json")
```

## Module Structure

```
src/
├── data_models.py      # Data structures (ContentChunk, ChapterData, ProcessedBook)
├── utils.py            # Utility functions for path validation, ID generation, etc.
├── file_discovery.py   # Chapter and file discovery logic
├── content_reader.py   # File reading and title extraction
├── content_cleaner.py  # Content cleaning and sanitization
├── chunker.py          # Content chunking algorithms
├── metadata_attacher.py # Metadata attachment logic
├── validation.py       # Validation functions
├── logging_config.py   # Logging setup
├── main_processor.py   # Main processing interface
├── integration_test.py # End-to-end integration test
```

## Output Format

The module produces a structured JSON output containing:

- `chapters`: Array of chapter information
- `chunks`: Array of content chunks with metadata
- `metadata`: Processing statistics and metrics

Each content chunk contains:
- `chunk_id`: Globally unique identifier
- `text`: Cleaned content chunk
- `chapter_number`: Chapter identifier
- `title`: Chapter title
- `section_heading`: Section heading (if available)
- `source_file`: Relative path to source file
- `source_url`: URL-friendly path
- `order_index`: Position in reading order

## Validation

The module includes comprehensive validation:
- All required metadata fields are present
- Chunk sizes maintain 300-500 word target range
- Content integrity is preserved
- Chunks are self-contained and meaningful
- Output is deterministic across runs

## Testing

Run the integration test to validate end-to-end functionality:

```bash
python -m src.integration_test
```

## Constraints

- Reads book content ONLY from `/chapters/**/*`
- Does NOT generate embeddings
- Does NOT call any LLMs
- Does NOT integrate vector databases
- Does NOT implement retrieval or chatbot logic

## Quality Assurance

The implementation follows clean, readable, production-quality code standards with:
- Clear separation of concerns
- Logical function and class organization
- Concise inline comments where logic is non-obvious
- Deterministic and repeatable output
- Graceful handling of edge cases