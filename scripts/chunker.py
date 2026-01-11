"""
Chunking module for the Book Content Extraction & Structuring module.

This module handles segmenting content into logical units of 300-500 words
while respecting sentence boundaries and maintaining context.
"""

import re
from typing import List, Tuple
from .content_cleaner import extract_headings


def chunk_content(content: str, target_min_words: int = 300, target_max_words: int = 500, respect_headings: bool = True) -> List[str]:
    """
    Chunk content into logical units of target_min_words to target_max_words.

    Args:
        content: Content to chunk
        target_min_words: Minimum target words per chunk
        target_max_words: Maximum target words per chunk
        respect_headings: Whether to respect heading boundaries when chunking

    Returns:
        List of content chunks
    """
    if not content.strip():
        return []

    if respect_headings:
        # Split content by headings to create logical sections
        sections = split_by_headings(content)

        chunks = []
        for section in sections:
            section_chunks = chunk_section(section, target_min_words, target_max_words)
            chunks.extend(section_chunks)

        return chunks
    else:
        # Use simple word-based chunking
        return chunk_by_words(content, target_min_words, target_max_words)




def chunk_by_headings_hierarchy(content: str, target_min_words: int = 300, target_max_words: int = 500) -> List[str]:
    """
    Enhanced chunking that respects heading hierarchy (H1, H2, H3).

    Args:
        content: Content to chunk
        target_min_words: Minimum target words per chunk
        target_max_words: Maximum target words per chunk

    Returns:
        List of content chunks respecting heading hierarchy
    """
    if not content.strip():
        return []

    # Split by all headings
    sections = split_by_headings_with_hierarchy(content)

    chunks = []
    for section in sections:
        section_chunks = chunk_section(section, target_min_words, target_max_words)
        chunks.extend(section_chunks)

    return chunks


def split_by_headings_with_hierarchy(content: str) -> List[str]:
    """
    Split content by headings while preserving hierarchical context.

    Args:
        content: Content to split

    Returns:
        List of content sections respecting hierarchy
    """
    lines = content.split('\n')
    sections = []
    current_section = []
    current_heading_level = 0
    current_heading = ""

    for line in lines:
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            heading_level = len(match.group(1))
            heading_text = match.group(2).strip()

            # If we have a previous section and this is a new top-level heading
            if current_section and heading_level <= current_heading_level:
                sections.append('\n'.join(current_section))
                current_section = [line]
                current_heading_level = heading_level
            else:
                # For subheadings, add to current section
                current_section.append(line)
                if heading_level < current_heading_level:
                    current_heading_level = heading_level
        else:
            current_section.append(line)

    # Add the last section
    if current_section:
        sections.append('\n'.join(current_section))

    return sections


def split_by_headings(content: str) -> List[str]:
    """
    Split content by headings to create logical sections.

    Args:
        content: Content to split

    Returns:
        List of content sections
    """
    # Find all headings and their positions
    heading_pattern = r'^(#{1,6})\s+(.+)$'
    lines = content.split('\n')

    sections = []
    current_section = []
    current_heading = ""

    for line in lines:
        match = re.match(heading_pattern, line)
        if match:
            # If we have a previous section, save it
            if current_section:
                sections.append('\n'.join(current_section))
            # Start new section with heading
            current_section = [line]
        else:
            current_section.append(line)

    # Add the last section
    if current_section:
        sections.append('\n'.join(current_section))

    return sections


def chunk_section(section: str, target_min_words: int, target_max_words: int) -> List[str]:
    """
    Chunk a single section into smaller pieces.

    Args:
        section: Section to chunk
        target_min_words: Minimum target words per chunk
        target_max_words: Maximum target words per chunk

    Returns:
        List of section chunks
    """
    if not section.strip():
        return []

    # If the section is already within the target range, return as is
    word_count = len(section.split())
    if word_count <= target_max_words:
        return [section]

    # Split the section into paragraphs
    paragraphs = re.split(r'\n\s*\n', section)
    chunks = []
    current_chunk = []
    current_word_count = 0

    for paragraph in paragraphs:
        paragraph_word_count = len(paragraph.split())

        # If adding this paragraph would exceed max words
        if current_word_count + paragraph_word_count > target_max_words and current_chunk:
            # Finalize current chunk if it meets minimum requirement
            if current_word_count >= target_min_words:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_word_count = paragraph_word_count
            else:
                # If current chunk doesn't meet minimum, try to find a sentence boundary
                chunk_text = '\n\n'.join(current_chunk)
                sub_chunks = chunk_by_sentences(chunk_text, target_min_words, target_max_words)
                chunks.extend(sub_chunks)
                current_chunk = [paragraph]
                current_word_count = paragraph_word_count
        else:
            current_chunk.append(paragraph)
            current_word_count += paragraph_word_count

    # Handle remaining content in current chunk
    if current_chunk:
        chunk_text = '\n\n'.join(current_chunk)
        if len(chunk_text.split()) <= target_max_words:
            chunks.append(chunk_text)
        else:
            # If still too large, split by sentences
            sub_chunks = chunk_by_sentences(chunk_text, target_min_words, target_max_words)
            chunks.extend(sub_chunks)

    return chunks


def chunk_by_sentences(text: str, target_min_words: int, target_max_words: int) -> List[str]:
    """
    Split text into chunks by sentences while respecting word count limits.

    Args:
        text: Text to chunk by sentences
        target_min_words: Minimum target words per chunk
        target_max_words: Maximum target words per chunk

    Returns:
        List of sentence-based chunks
    """
    # More sophisticated sentence splitting that handles abbreviations, etc.
    # This regex handles common sentence endings while avoiding breaking on abbreviations
    sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\!|\?)\s+'
    sentences = re.split(sentence_pattern, text)

    # Clean up sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) == 0:
        return []
    elif len(sentences) == 1:
        # If text doesn't contain sentence breaks, fall back to word-based chunking
        return chunk_by_words(text, target_min_words, target_max_words)

    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        sentence_word_count = len(sentence.split())

        # If adding this sentence would exceed max words
        if current_word_count + sentence_word_count > target_max_words and current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_word_count = len(chunk_text.split())

            # If current chunk meets minimum requirement, save it
            if chunk_word_count >= target_min_words:
                chunks.append(chunk_text)
                current_chunk = [sentence]
                current_word_count = sentence_word_count
            else:
                # Otherwise, try to make the best possible chunk
                if sentence_word_count <= target_max_words:
                    chunks.append(chunk_text + ' ' + sentence)
                    current_chunk = []
                    current_word_count = 0
                else:
                    # If sentence itself is too long, we need to force split it
                    if current_chunk:
                        chunks.append(chunk_text)
                    long_sentence_chunks = chunk_long_sentence(sentence, target_min_words, target_max_words)
                    chunks.extend(long_sentence_chunks)
                    current_chunk = []
                    current_word_count = 0
        else:
            current_chunk.append(sentence)
            current_word_count += sentence_word_count

    # Handle remaining content
    if current_chunk:
        chunk_text = ' '.join(current_chunk)
        if len(chunk_text.split()) >= target_min_words or not chunks:
            # Add to chunks if it meets minimum or if it's the only chunk
            chunks.append(chunk_text)
        else:
            # If the last chunk doesn't meet minimum and there are other chunks,
            # append it to the last chunk if it doesn't exceed max
            if chunks:  # Make sure chunks list is not empty
                last_chunk = chunks[-1]
                combined_word_count = len((last_chunk + ' ' + chunk_text).split())
                if combined_word_count <= target_max_words:
                    chunks[-1] = last_chunk + ' ' + chunk_text
                else:
                    chunks.append(chunk_text)
            else:
                chunks.append(chunk_text)

    return chunks


def validate_content_preservation(original: str, processed: str) -> bool:
    """
    Validate that semantic meaning is preserved during processing.

    Args:
        original: Original content
        processed: Processed content

    Returns:
        True if content integrity is maintained, False otherwise
    """
    # Basic validation: ensure no complete sentences are lost
    # This is a simplified check - in practice, you might want more sophisticated validation

    # Count words as a basic integrity check
    orig_words = len(original.split())
    proc_words = len(processed.split())

    # Allow for some cleaning (removing nav elements, etc.) but not major losses
    if orig_words > 0:
        loss_percentage = (orig_words - proc_words) / orig_words
        return loss_percentage < 0.1  # Allow up to 10% loss for cleaning

    return True


def validate_chunk_meaningfulness(chunk: str) -> bool:
    """
    Validate that a chunk is self-contained and meaningful.

    Args:
        chunk: Content chunk to validate

    Returns:
        True if chunk is meaningful, False otherwise
    """
    if not chunk.strip():
        return False

    # Check if chunk has enough content to be meaningful
    words = chunk.split()
    if len(words) < 10:  # Minimum 10 words for basic meaningfulness
        return False

    # Check if chunk appears to be cut off mid-sentence
    chunk = chunk.strip()
    if chunk.endswith(('.', '!', '?')):
        return True  # Ends with sentence punctuation, likely complete

    # If chunk doesn't end with punctuation, check if it seems like a complete thought
    # For now, we'll consider it valid if it has sufficient length
    return len(words) >= 30  # If it has 30+ words but no ending punctuation, assume it's a valid chunk

    # More sophisticated validation would check for complete thoughts,
    # but that requires more complex NLP processing


def chunk_by_words(text: str, target_min_words: int, target_max_words: int) -> List[str]:
    """
    Fallback method to chunk text by words when sentence boundaries aren't available.

    Args:
        text: Text to chunk by words
        target_min_words: Minimum target words per chunk
        target_max_words: Maximum target words per chunk

    Returns:
        List of word-based chunks
    """
    words = text.split()
    chunks = []

    i = 0
    while i < len(words):
        # Start with minimum words
        chunk_words = words[i:i + target_min_words]
        j = i + target_min_words

        # Add more words up to the maximum if available
        while j < min(i + target_max_words, len(words)):
            chunk_words.append(words[j])
            j += 1

        chunks.append(' '.join(chunk_words))
        i = j

    return chunks


def chunk_long_sentence(sentence: str, target_min_words: int, target_max_words: int) -> List[str]:
    """
    Handle sentences that are longer than the maximum chunk size.

    Args:
        sentence: Long sentence to chunk
        target_min_words: Minimum target words per chunk
        target_max_words: Maximum target words per chunk

    Returns:
        List of sentence fragments
    """
    # For very long sentences, we have to break them at word boundaries
    words = sentence.split()
    chunks = []

    i = 0
    while i < len(words):
        end_idx = min(i + target_max_words, len(words))
        chunk_words = words[i:end_idx]
        chunks.append(' '.join(chunk_words))
        i = end_idx

    return chunks


def get_section_heading(section: str) -> str:
    """
    Extract the heading from a section if it starts with a heading.

    Args:
        section: Section to extract heading from

    Returns:
        Heading text if found, empty string otherwise
    """
    lines = section.split('\n')
    for line in lines:
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            return match.group(2).strip()
    return ""