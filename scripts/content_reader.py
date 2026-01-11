"""
Content reading module for the Book Content Extraction & Structuring module.

This module handles reading Markdown files while preserving file metadata.
"""

from pathlib import Path
from typing import List


def read_markdown_file(file_path: str) -> str:
    """
    Read the content of a markdown file.

    Args:
        file_path: Path to the markdown file to read

    Returns:
        Content of the file as a string
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def read_multiple_markdown_files(file_paths: List[str]) -> List[str]:
    """
    Read the content of multiple markdown files.

    Args:
        file_paths: List of paths to markdown files to read

    Returns:
        List of file contents as strings
    """
    contents = []
    for file_path in file_paths:
        content = read_markdown_file(file_path)
        contents.append(content)
    return contents


def get_file_title(file_path: str) -> str:
    """
    Extract a title from the file path or content.

    Args:
        file_path: Path to the file

    Returns:
        Extracted title
    """
    # First try to get title from the first heading in the file
    try:
        content = read_markdown_file(file_path)
        lines = content.split('\n')
        for line in lines:
            # Look for markdown heading patterns
            if line.strip().startswith('# '):
                # Remove the heading marker and return the title
                return line.strip()[2:].strip()
            elif line.strip().startswith('## '):
                # If no main heading, use subheading
                return line.strip()[3:].strip()
    except Exception:
        pass

    # If no heading found in content, use the filename
    return Path(file_path).stem.replace('-', ' ').replace('_', ' ').title()