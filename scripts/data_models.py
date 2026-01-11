"""
Data models for the Book Content Extraction & Structuring module.

This module defines the core data structures that will be used throughout the
content extraction and processing pipeline.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class ContentChunk:
    """
    Represents a segment of processed book content with cleaned text and associated metadata.

    Attributes:
        chunk_id: globally unique identifier (string)
        text: cleaned content chunk (string)
        chapter_number: identifier for the chapter (string, e.g., "chapter-03")
        title: chapter or document title (string)
        section_heading: current section heading if available (string, optional)
        source_file: relative path to source file (string)
        source_url: URL-friendly path for frontend reference (string)
        order_index: index to preserve reading order (integer)
    """
    chunk_id: str
    text: str
    chapter_number: str
    title: str
    section_heading: Optional[str]
    source_file: str
    source_url: str
    order_index: int


@dataclass
class ChapterData:
    """
    Represents an individual chapter with its structural hierarchy and content organization.

    Attributes:
        chapter_id: unique identifier for the chapter (string)
        title: chapter title (string)
        path: path to chapter directory (string)
        files: list of markdown files in the chapter (array of strings)
        order: position in the book sequence (integer)
    """
    chapter_id: str
    title: str
    path: str
    files: List[str]
    order: int


@dataclass
class ProcessedBook:
    """
    Represents the complete processed book content as a collection of ContentChunks
    in the correct reading order.

    Attributes:
        chapters: array of ChapterData entities
        chunks: array of ContentChunk entities in reading order
        metadata: processing metadata (object)
    """
    chapters: List[ChapterData]
    chunks: List[ContentChunk]
    metadata: dict