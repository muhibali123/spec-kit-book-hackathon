"""
Integration test for the Book Content Extraction & Structuring module.

This module validates end-to-end functionality of the processing pipeline.
"""

import os
import tempfile
import json
from pathlib import Path
from .main_processor import processBookContent, save_processed_book


def create_test_chapters_structure(base_dir: str):
    """
    Create a test chapters directory structure with sample markdown files.

    Args:
        base_dir: Base directory to create the test structure in
    """
    chapters_dir = os.path.join(base_dir, "chapters")
    os.makedirs(chapters_dir, exist_ok=True)

    # Create test chapter directories
    chapter1_dir = os.path.join(chapters_dir, "chapter-01")
    chapter2_dir = os.path.join(chapters_dir, "chapter-02")
    os.makedirs(chapter1_dir, exist_ok=True)
    os.makedirs(chapter2_dir, exist_ok=True)

    # Create sample markdown files
    chapter1_content = """# Introduction to AI

This is the introduction chapter about artificial intelligence.

## What is AI?

Artificial Intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as a study of "intelligent agents".

## History of AI

The field of AI research was born at a Dartmouth College workshop in 1956. AI research has gone through periods of optimism followed by periods of limited progress, known as "AI winters".

### Early Development

The first AI programs were written in the late 1950s by John McCarthy and others.
"""

    chapter2_content = """# Machine Learning Basics

Machine learning is a subset of artificial intelligence that focuses on algorithms.

## Supervised Learning

Supervised learning is the machine learning task of learning a function that maps an input to an output based on example input-output pairs.

## Unsupervised Learning

Unsupervised learning is a type of machine learning that looks for previously undetected patterns in a dataset without pre-existing labels.

### Clustering

Clustering is the task of dividing the population or data points into a number of groups such that data points in the same groups are more similar to other data points in the same group than those in other groups.
"""

    # Write sample files
    with open(os.path.join(chapter1_dir, "intro.md"), "w", encoding="utf-8") as f:
        f.write(chapter1_content)

    with open(os.path.join(chapter1_dir, "history.md"), "w", encoding="utf-8") as f:
        f.write("# AI History\n\nDetailed history of artificial intelligence development.")

    with open(os.path.join(chapter2_dir, "basics.md"), "w", encoding="utf-8") as f:
        f.write(chapter2_content)


def run_integration_test():
    """
    Run the integration test to validate end-to-end functionality.
    """
    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Running integration test in: {temp_dir}")

        # Create test chapters structure
        create_test_chapters_structure(temp_dir)

        # Process the book content
        try:
            processed_book = processBookContent(temp_dir)

            # Validate the results
            assert len(processed_book.chapters) == 2, f"Expected 2 chapters, got {len(processed_book.chapters)}"
            assert len(processed_book.chunks) > 0, "Expected at least one chunk"
            assert processed_book.metadata["total_chunks"] > 0, "Expected non-zero total chunks"
            assert processed_book.metadata["total_words"] > 0, "Expected non-zero total words"
            assert processed_book.metadata["processing_time_ms"] > 0, "Expected non-zero processing time"

            # Validate that all chunks have required fields
            for chunk in processed_book.chunks:
                assert chunk.chunk_id, "Chunk ID is required"
                assert chunk.text, "Chunk text is required"
                assert chunk.chapter_number, "Chapter number is required"
                assert chunk.title, "Title is required"
                assert chunk.source_file, "Source file is required"
                assert chunk.source_url, "Source URL is required"
                assert isinstance(chunk.order_index, int), "Order index must be an integer"

            print(f"✓ Integration test passed!")
            print(f"  - Processed {len(processed_book.chapters)} chapters")
            print(f"  - Generated {len(processed_book.chunks)} chunks")
            print(f"  - Total words: {processed_book.metadata['total_words']}")
            print(f"  - Processing time: {processed_book.metadata['processing_time_ms']}ms")

            # Save the processed book to verify output generation
            output_path = os.path.join(temp_dir, "test_output.json")
            save_processed_book(processed_book, output_path)

            # Verify the output file exists and is valid JSON
            assert os.path.exists(output_path), "Output file should exist"

            with open(output_path, 'r', encoding='utf-8') as f:
                output_data = json.load(f)

            assert "chapters" in output_data, "Output should contain chapters"
            assert "chunks" in output_data, "Output should contain chunks"
            assert "metadata" in output_data, "Output should contain metadata"

            print(f"✓ Output validation passed!")
            print(f"  - Output saved to: {output_path}")

            return True

        except Exception as e:
            print(f"✗ Integration test failed: {str(e)}")
            return False


if __name__ == "__main__":
    success = run_integration_test()
    if success:
        print("\n🎉 All integration tests passed!")
    else:
        print("\n❌ Integration tests failed!")
        exit(1)