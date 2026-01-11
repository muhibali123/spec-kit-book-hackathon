"""
File discovery module for the Book Content Extraction & Structuring module.

This module handles discovering chapter folders and Markdown files in the /chapters directory.
"""

import os
from pathlib import Path
from typing import List, Dict
from .data_models import ChapterData
from .utils import is_valid_markdown_file, extract_chapter_number


def discover_chapters(chapters_dir: str) -> List[ChapterData]:
    """
    Discover all chapter directories and their markdown files in the chapters directory.

    Args:
        chapters_dir: Path to the chapters directory

    Returns:
        List of ChapterData objects with discovered chapters
    """
    chapters = []

    # Ensure the chapters directory exists
    if not os.path.exists(chapters_dir):
        raise FileNotFoundError(f"Chapters directory does not exist: {chapters_dir}")

    # Get all subdirectories in the chapters directory
    chapter_dirs = [d for d in os.listdir(chapters_dir)
                   if os.path.isdir(os.path.join(chapters_dir, d))]

    # Sort directories to ensure consistent ordering
    chapter_dirs.sort()

    for i, dir_name in enumerate(chapter_dirs):
        dir_path = os.path.join(chapters_dir, dir_name)

        # Find all markdown files in the chapter directory
        markdown_files = []
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path) and is_valid_markdown_file(file_name):
                markdown_files.append(file_path)

        # Sort files to ensure consistent ordering
        markdown_files.sort()

        # Extract chapter number from directory name
        chapter_number = extract_chapter_number(dir_name)
        if not chapter_number:
            chapter_number = f"chapter-{(i+1):02d}"  # Default to numeric if no pattern found

        # Create ChapterData object
        chapter_data = ChapterData(
            chapter_id=chapter_number,
            title=dir_name.replace('-', ' ').title(),  # Convert directory name to title
            path=dir_path,
            files=markdown_files,
            order=i
        )

        chapters.append(chapter_data)

    # Sort chapters by order to ensure proper sequence
    chapters.sort(key=lambda x: x.order)

    return chapters


def get_markdown_files_in_chapters(chapters_dir: str) -> List[str]:
    """
    Get all markdown files in all chapter directories.

    Args:
        chapters_dir: Path to the chapters directory

    Returns:
        List of paths to all markdown files found
    """
    all_markdown_files = []
    chapters = discover_chapters(chapters_dir)

    for chapter in chapters:
        all_markdown_files.extend(chapter.files)

    return all_markdown_files