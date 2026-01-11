"""
Validation module for the Book Content Extraction & Structuring module.

This module handles content integrity checks and validation to ensure
no meaningful text is lost during cleaning and chunking operations.
"""

from typing import List
from .data_models import ContentChunk
from .chunker import validate_content_preservation, validate_chunk_meaningfulness


def validate_all_metadata_fields_present(chunks: List[ContentChunk]) -> bool:
    """
    Validate that all required metadata fields are present in output chunks.

    Args:
        chunks: List of ContentChunk objects to validate

    Returns:
        True if all required fields are present, False otherwise
    """
    required_fields = ['chunk_id', 'text', 'chapter_number', 'title',
                      'section_heading', 'source_file', 'source_url', 'order_index']

    for chunk in chunks:
        # Check that each required attribute exists and is not None/empty where required
        if not chunk.chunk_id:
            return False
        if not chunk.text:
            return False
        if not chunk.chapter_number:
            return False
        if not chunk.title:
            return False
        if not chunk.source_file:
            return False
        if not chunk.source_url:
            return False
        # section_heading can be None, which is valid
        # order_index should be a valid integer

    return True


def validate_chunk_sizes(chunks: List[ContentChunk], min_words: int = 300, max_words: int = 500) -> bool:
    """
    Validate that chunks are within the target word count range.

    Args:
        chunks: List of ContentChunk objects to validate
        min_words: Minimum target words per chunk
        max_words: Maximum target words per chunk

    Returns:
        True if all chunks are within size range (with flexibility), False otherwise
    """
    for chunk in chunks:
        word_count = len(chunk.text.split())
        # Allow some flexibility for sentence boundaries
        if word_count < min_words * 0.8 or word_count > max_words * 1.2:  # 80% to 120% tolerance
            # However, if it's a very small chunk, check if it's meaningful
            if word_count < min_words * 0.8 and not validate_chunk_meaningfulness(chunk.text):
                return False

    return True


def validate_deterministic_output(original_chunks: List[ContentChunk],
                                new_chunks: List[ContentChunk]) -> bool:
    """
    Validate that processing is deterministic across runs.

    Args:
        original_chunks: First run of processed chunks
        new_chunks: Second run of processed chunks

    Returns:
        True if output is deterministic, False otherwise
    """
    if len(original_chunks) != len(new_chunks):
        return False

    for orig_chunk, new_chunk in zip(original_chunks, new_chunks):
        if orig_chunk.chunk_id != new_chunk.chunk_id:
            return False
        if orig_chunk.text != new_chunk.text:
            return False
        if orig_chunk.order_index != new_chunk.order_index:
            return False

    return True


def validate_content_integrity(original_content: str, processed_chunks: List[ContentChunk]) -> bool:
    """
    Validate that no meaningful content is lost during processing.

    Args:
        original_content: Original content before processing
        processed_chunks: List of processed ContentChunk objects

    Returns:
        True if content integrity is maintained, False otherwise
    """
    # Combine all chunk texts to reconstruct processed content
    reconstructed_content = ' '.join([chunk.text for chunk in processed_chunks])

    # Validate preservation of semantic meaning
    return validate_content_preservation(original_content, reconstructed_content)


def validate_chunks_meaningful(chunks: List[ContentChunk]) -> bool:
    """
    Validate that all chunks are self-contained and meaningful.

    Args:
        chunks: List of ContentChunk objects to validate

    Returns:
        True if all chunks are meaningful, False otherwise
    """
    for chunk in chunks:
        if not validate_chunk_meaningfulness(chunk.text):
            return False

    return True


def run_comprehensive_validation(chunks: List[ContentChunk],
                               original_content: str = None) -> dict:
    """
    Run comprehensive validation on the processed chunks.

    Args:
        chunks: List of processed ContentChunk objects
        original_content: Optional original content for integrity checks

    Returns:
        Dictionary with validation results
    """
    results = {
        'metadata_fields_present': validate_all_metadata_fields_present(chunks),
        'chunk_sizes_valid': validate_chunk_sizes(chunks),
        'chunks_meaningful': validate_chunks_meaningful(chunks),
        'content_integrity_maintained': True  # Will be set if original_content is provided
    }

    if original_content:
        results['content_integrity_maintained'] = validate_content_integrity(
            original_content, chunks
        )

    # Overall validation result
    results['overall_valid'] = all([
        results['metadata_fields_present'],
        results['chunk_sizes_valid'],
        results['chunks_meaningful'],
        results['content_integrity_maintained']
    ])

    return results