"""
Utility functions for the Book Content Extraction & Structuring module.

This module contains helper functions for path validation, security checks,
and other common operations used throughout the processing pipeline.
"""

import os
import re
from pathlib import Path
from typing import List, Optional


def validate_path_security(input_path: str, allowed_directories: List[str]) -> bool:
    """
    Validate that the input path is safe and within allowed directories.

    Args:
        input_path: The path to validate
        allowed_directories: List of allowed base directories

    Returns:
        True if path is safe, False otherwise
    """
    # Convert to Path object for easier manipulation
    path = Path(input_path).resolve()

    # Check for directory traversal attempts
    if '..' in path.parts or path.is_reserved():
        return False

    # Check if path is within allowed directories
    path_str = str(path)
    for allowed_dir in allowed_directories:
        if path_str.startswith(os.path.abspath(allowed_dir)):
            return True

    return False


def is_valid_markdown_file(file_path: str) -> bool:
    """
    Check if a file is a valid markdown file.

    Args:
        file_path: Path to the file to check

    Returns:
        True if file is a valid markdown file, False otherwise
    """
    valid_extensions = {'.md', '.markdown', '.mdx'}
    return Path(file_path).suffix.lower() in valid_extensions


def extract_chapter_number(directory_name: str) -> Optional[str]:
    """
    Extract chapter number from directory name using pattern like 'chapter-01'.

    Args:
        directory_name: Name of the directory

    Returns:
        Chapter number string if found, None otherwise
    """
    # Look for patterns like 'chapter-01', 'Chapter-02', 'CHAPTER-03', etc.
    match = re.search(r'(?:chapter|ch|c)-?(\d+)', directory_name.lower())
    if match:
        return f"chapter-{match.group(1).zfill(2)}"
    return None


def sanitize_filename_for_url(filename: str) -> str:
    """
    Convert a filename to a URL-friendly format.

    Args:
        filename: Original filename

    Returns:
        URL-friendly version of the filename
    """
    # Remove file extension and convert to lowercase
    name = Path(filename).stem.lower()
    # Replace spaces and special characters with hyphens
    name = re.sub(r'[^a-z0-9-]', '-', name)
    # Remove multiple consecutive hyphens
    name = re.sub(r'-+', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    return name


def generate_chunk_id(chapter_id: str, file_path: str, chunk_index: int) -> str:
    """
    Generate a globally unique chunk ID based on chapter, file, and chunk position.

    Args:
        chapter_id: ID of the chapter
        file_path: Path to the source file
        chunk_index: Index of the chunk within the file

    Returns:
        Unique chunk ID
    """
    import hashlib

    # Create a hash based on chapter, file, and chunk index
    identifier = f"{chapter_id}_{file_path}_{chunk_index}"
    hash_obj = hashlib.md5(identifier.encode())
    hash_hex = hash_obj.hexdigest()[:8]  # Use first 8 characters of hash

    return f"{chapter_id}_{hash_hex}_{chunk_index:04d}"