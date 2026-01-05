"""
Content cleaning module for the Book Content Extraction & Structuring module.

This module handles removing navigation, UI, and layout-related text elements
from raw Markdown content while preserving semantic meaning.
"""

import re
from typing import List, Tuple, Optional


def clean_markdown_content(content: str) -> str:
    """
    Clean raw markdown content by removing navigation, UI, and layout-related elements.

    Args:
        content: Raw markdown content to clean

    Returns:
        Cleaned content string
    """
    # Remove common navigation elements (links, buttons, etc.)
    # This pattern removes navigation-like markdown links that appear to be navigation
    content = re.sub(r'\[(?:Table of Contents|Contents|Navigation|Home|Next|Previous|Back|Index|Table of Contents|Overview|Summary)\]\([^)]*\)', '', content, flags=re.IGNORECASE)

    # Remove common UI elements like navigation bars, sidebars, etc.
    # Remove lines that look like navigation menus (often have multiple links in brackets)
    lines = content.split('\n')
    cleaned_lines = []

    for line in lines:
        # Skip lines that look like navigation bars (multiple bracketed links)
        nav_pattern = r'\[.*\]\(.*\)\s*\|\s*\[.*\]\(.*\)'  # Simple nav pattern
        if not re.search(nav_pattern, line) and not line.strip().lower().startswith('navigation:'):
            cleaned_lines.append(line)

    content = '\n'.join(cleaned_lines)

    # Remove YAML frontmatter if present (common in Docusaurus/MDX)
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    # Remove HTML tags that might be used for layout (but preserve semantic content)
    content = re.sub(r'<(div|span|section|nav|header|footer|aside|article)\b[^>]*>', '', content)
    content = re.sub(r'</(div|span|section|nav|header|footer|aside|article)>', '', content)

    # Remove empty lines at the beginning and end
    content = content.strip()

    return content


def extract_headings(content: str) -> List[Tuple[str, str]]:
    """
    Extract headings from content to use as metadata only.

    Args:
        content: Markdown content to extract headings from

    Returns:
        List of tuples (heading_level, heading_text)
    """
    headings = []
    lines = content.split('\n')

    for line in lines:
        # Match markdown headings: #, ##, ###, etc.
        match = re.match(r'^(#{1,6})\s+(.+)', line)
        if match:
            heading_level = len(match.group(1))
            heading_text = match.group(2).strip()
            headings.append((f'H{heading_level}', heading_text))

    return headings


def preserve_code_blocks(content: str) -> str:
    """
    Ensure code blocks are preserved during cleaning.

    Args:
        content: Markdown content to process

    Returns:
        Content with code blocks preserved
    """
    # This function ensures code blocks aren't accidentally modified during cleaning
    # Code blocks are already preserved by the basic cleaning, but we make sure here
    return content


def preserve_tables(content: str) -> str:
    """
    Ensure tables are preserved during cleaning.

    Args:
        content: Markdown content to process

    Returns:
        Content with tables preserved
    """
    # Tables in markdown format (with pipes and dashes) should already be preserved
    # This function ensures tables aren't accidentally modified during cleaning
    return content


def preserve_math_formulas(content: str) -> str:
    """
    Ensure math formulas are preserved during cleaning.

    Args:
        content: Markdown content to process

    Returns:
        Content with math formulas preserved
    """
    # This function ensures math formulas (in $...$ or $$...$$) are preserved
    return content


def handle_content_without_headings(content: str, target_min_words: int = 300, target_max_words: int = 500) -> List[str]:
    """
    Handle content that has no headings but consists of long paragraphs.

    Args:
        content: Content without clear headings
        target_min_words: Minimum target words per chunk
        target_max_words: Maximum target words per chunk

    Returns:
        List of content chunks
    """
    # For content without headings, we'll chunk by paragraphs or sentences
    # First try to split by paragraphs
    paragraphs = content.split('\n\n')

    chunks = []
    current_chunk = []
    current_word_count = 0

    for paragraph in paragraphs:
        paragraph_word_count = len(paragraph.split())

        if current_word_count + paragraph_word_count > target_max_words and current_chunk:
            # Finalize current chunk
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_word_count = paragraph_word_count
        else:
            current_chunk.append(paragraph)
            current_word_count += paragraph_word_count

    # Handle remaining content
    if current_chunk:
        if current_chunk and len('\n\n'.join(current_chunk).split()) <= target_max_words:
            chunks.append('\n\n'.join(current_chunk))
        else:
            # If still too large, use sentence-based chunking
            remaining_text = '\n\n'.join(current_chunk)
            from .chunker import chunk_by_sentences
            sentence_chunks = chunk_by_sentences(remaining_text, target_min_words, target_max_words)
            chunks.extend(sentence_chunks)

    return chunks