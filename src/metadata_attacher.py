"""
Metadata attachment module for the Book Content Extraction & Structuring module.

This module handles attaching required metadata to each content chunk.
"""

import hashlib
from pathlib import Path
from typing import List, Optional
from .data_models import ContentChunk
from .utils import sanitize_filename_for_url, generate_chunk_id
from .chunker import get_section_heading


def attach_metadata_to_chunks(
    chunks: List[str],
    chapter_data: 'ChapterData',  # Forward reference as ChapterData is imported in main module
    source_file: str,
    base_path: str,
    section_headings: List[str] = None
) -> List[ContentChunk]:
    """
    Attach required metadata to each content chunk.

    Args:
        chunks: List of content chunks to attach metadata to
        chapter_data: Chapter data containing chapter information
        source_file: Path to the source file
        base_path: Base path for relative path calculations
        section_headings: Optional list of section headings for context

    Returns:
        List of ContentChunk objects with attached metadata
    """
    content_chunks = []

    for i, chunk_text in enumerate(chunks):
        # Generate unique chunk ID
        chunk_id = generate_chunk_id(chapter_data.chapter_id, source_file, i)

        # Extract section heading from the chunk content
        section_heading = get_section_heading(chunk_text)
        if not section_heading and section_headings and i < len(section_headings):
            section_heading = section_headings[i]
        elif not section_heading:
            section_heading = None

        # Create relative path for source_file
        source_path = Path(source_file)
        try:
            relative_path = source_path.relative_to(base_path)
        except ValueError:
            relative_path = source_path

        # Create URL-friendly path
        source_url = sanitize_filename_for_url(str(relative_path))

        # Create ContentChunk object
        content_chunk = ContentChunk(
            chunk_id=chunk_id,
            text=chunk_text,
            chapter_number=chapter_data.chapter_id,
            title=chapter_data.title,
            section_heading=section_heading,
            source_file=str(relative_path),
            source_url=source_url,
            order_index=i  # This will be updated globally later
        )

        content_chunks.append(content_chunk)

    return content_chunks


def update_global_order_indices(chunks: List[ContentChunk]) -> List[ContentChunk]:
    """
    Update the order indices to reflect the global position across all chunks.

    Args:
        chunks: List of ContentChunk objects

    Returns:
        List of ContentChunk objects with updated order indices
    """
    # Sort chunks by their original order and chapter to maintain proper sequence
    sorted_chunks = sorted(chunks, key=lambda x: (x.chapter_number, x.order_index))

    # Update order indices to be globally sequential
    for i, chunk in enumerate(sorted_chunks):
        chunk.order_index = i

    return sorted_chunks