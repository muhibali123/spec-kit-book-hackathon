"""
Main processing module for the Book Content Extraction & Structuring module.

This module implements the main processing interface function that orchestrates
the entire content extraction and structuring pipeline.
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from .data_models import ContentChunk, ChapterData, ProcessedBook
from .file_discovery import discover_chapters
from .content_reader import read_markdown_file, get_file_title
from .content_cleaner import clean_markdown_content
from .chunker import chunk_content
from .metadata_attacher import attach_metadata_to_chunks, update_global_order_indices
from .validation import run_comprehensive_validation
from .logging_config import setup_logging, log_processing_event


def processBookContent(inputDirectory: str, outputFormat: str = "json") -> ProcessedBook:
    """
    Main processing function that transforms raw Markdown chapter files into structured data chunks.

    Args:
        inputDirectory: Path to the directory containing /chapters subdirectory
        outputFormat: Format for output (currently only supports "json")

    Returns:
        ProcessedBook object with structured content chunks
    """
    # Set up logging
    logger = setup_logging()
    start_time = time.time()

    log_processing_event(logger, "info", "Starting book content processing", input_dir=inputDirectory)

    # Validate input directory
    if not os.path.exists(inputDirectory):
        log_processing_event(logger, "error", "Input directory does not exist", input_dir=inputDirectory)
        raise FileNotFoundError(f"Input directory does not exist: {inputDirectory}")

    # Construct chapters directory path
    chapters_dir = os.path.join(inputDirectory, "chapters")
    if not os.path.exists(chapters_dir):
        log_processing_event(logger, "error", "Chapters directory does not exist", chapters_dir=chapters_dir)
        raise FileNotFoundError(f"Chapters directory does not exist: {chapters_dir}")

    # Discover chapters
    log_processing_event(logger, "info", "Discovering chapters", chapters_dir=chapters_dir)
    chapters = discover_chapters(chapters_dir)

    # Process all chapters and collect chunks
    all_chunks = []
    processed_chapters = []

    for chapter in chapters:
        log_processing_event(logger, "info", "Processing chapter", chapter_id=chapter.chapter_id)
        # Process each file in the chapter
        chapter_chunks = []

        for file_path in chapter.files:
            log_processing_event(logger, "debug", "Processing file", file_path=file_path)
            # Read content from file
            raw_content = read_markdown_file(file_path)

            # Clean content
            cleaned_content = clean_markdown_content(raw_content)

            # Chunk content
            content_chunks = chunk_content(cleaned_content)

            # Attach metadata to chunks
            file_chunks = attach_metadata_to_chunks(
                content_chunks,
                chapter,
                file_path,
                inputDirectory
            )

            chapter_chunks.extend(file_chunks)

        # Update order indices for all chunks in this chapter
        # (Will be updated globally later)
        processed_chapters.append(chapter)
        all_chunks.extend(chapter_chunks)

    # Update global order indices for all chunks
    all_chunks = update_global_order_indices(all_chunks)

    # Calculate processing metrics
    processing_time = time.time() - start_time
    total_words = sum(len(chunk.text.split()) for chunk in all_chunks)

    log_processing_event(logger, "info", "Processing completed",
                        total_chunks=len(all_chunks), total_words=total_words,
                        processing_time_ms=int(processing_time * 1000))

    # Create metadata
    metadata = {
        "processed_at": datetime.now().isoformat(),
        "total_chunks": len(all_chunks),
        "total_words": total_words,
        "processing_time_ms": int(processing_time * 1000)
    }

    # Create ProcessedBook object
    processed_book = ProcessedBook(
        chapters=processed_chapters,
        chunks=all_chunks,
        metadata=metadata
    )

    # Perform validation to ensure output meets requirements
    validation_results = run_comprehensive_validation(all_chunks)

    # If validation fails, log warnings but still return the processed book
    if not validation_results.get('overall_valid', True):
        log_processing_event(logger, "warning", "Validation issues detected", validation_results=validation_results)

    return processed_book


def generateChunks(content: str, metadata: Dict[str, Any]) -> List[ContentChunk]:
    """
    Generate content chunks from raw content with associated metadata.

    Args:
        content: Raw content string to chunk
        metadata: Metadata dictionary containing chapter info, etc.

    Returns:
        Array of ContentChunk objects
    """
    # Clean content
    cleaned_content = clean_markdown_content(content)

    # Chunk content
    content_chunks = chunk_content(cleaned_content)

    # This function would need more context to properly create ContentChunk objects
    # since it lacks specific chapter/file information
    # For now, return empty list as this is primarily used internally
    # The main processing happens in processBookContent
    raise NotImplementedError("This function requires more context about the source file and chapter. Use processBookContent instead.")


def save_processed_book(processed_book: ProcessedBook, output_path: str, output_format: str = "json"):
    """
    Save the processed book to a file in the specified format.

    Args:
        processed_book: ProcessedBook object to save
        output_path: Path to save the output file
        output_format: Format for output ("json" supported)
    """
    if output_format.lower() == "json":
        # Convert ProcessedBook to dictionary for JSON serialization
        output_data = {
            "chapters": [
                {
                    "chapter_id": chapter.chapter_id,
                    "title": chapter.title,
                    "path": chapter.path,
                    "files": chapter.files,
                    "order": chapter.order
                }
                for chapter in processed_book.chapters
            ],
            "chunks": [
                {
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "chapter_number": chunk.chapter_number,
                    "title": chunk.title,
                    "section_heading": chunk.section_heading,
                    "source_file": chunk.source_file,
                    "source_url": chunk.source_url,
                    "order_index": chunk.order_index
                }
                for chunk in processed_book.chunks
            ],
            "metadata": processed_book.metadata
        }

        # Write to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def run_processing_pipeline(input_directory: str, output_path: str = None):
    """
    Run the complete processing pipeline from input to output.

    Args:
        input_directory: Directory containing the /chapters folder
        output_path: Optional path to save the output (defaults to processed_book.json)
    """
    if output_path is None:
        output_path = "processed_book.json"

    # Process the book content
    processed_book = processBookContent(input_directory)

    # Save the processed book
    save_processed_book(processed_book, output_path)

    print(f"Processing completed successfully!")
    print(f"Total chunks generated: {processed_book.metadata['total_chunks']}")
    print(f"Total words processed: {processed_book.metadata['total_words']}")
    print(f"Processing time: {processed_book.metadata['processing_time_ms']}ms")
    print(f"Output saved to: {output_path}")

    return processed_book