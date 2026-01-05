# Quickstart Guide: Book Content Extraction & Structuring

## Overview
This module processes book content from Markdown files in the `/chapters` directory, transforming them into clean, structured chunks suitable for a RAG pipeline.

## Prerequisites
- Access to the project directory containing `/chapters/**/*` structure
- Markdown parsing library (recommended: established library like marked, markdown-it, or similar)
- Text processing capabilities for cleaning and chunking

## Setup
1. Ensure the project directory has the expected structure:
   ```
   /project-root
   └── /chapters
       ├── /chapter-01
       │   ├── intro.md
       │   └── section1.md
       ├── /chapter-02
       │   └── content.md
       └── ...
   ```

2. Install required dependencies for Markdown parsing and text processing

## Usage
1. Run the processing module with the project directory as input
2. The module will:
   - Discover all Markdown files in `/chapters/**/*`
   - Process each file through cleaning and chunking
   - Attach required metadata to each chunk
   - Output structured JSON with all content chunks

## Key Components
- **File Discovery**: Finds all Markdown files in the chapters directory
- **Content Cleaning**: Removes navigation/UI elements while preserving semantic content
- **Chunking Engine**: Segments content into 300-500 word logical sections
- **Metadata Attachment**: Adds required fields to each chunk
- **Output Generator**: Creates the final JSON structure

## Configuration Options
- Input directory path
- Target chunk size range (default: 300-500 words)
- Output format options

## Output Format
The module produces JSON with an array of ContentChunk objects, each containing:
- `chunk_id`: globally unique identifier
- `text`: cleaned content
- `chapter_number`: chapter identifier
- `title`: chapter title
- `section_heading`: current section (if applicable)
- `source_file`: relative path to source
- `source_url`: URL-friendly path
- `order_index`: reading order position