#!/usr/bin/env python3
"""
Script to convert processed content to the format expected by the embedding generator.
"""
import json
import sys
import os
from typing import List, Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.types.embeddings import InputChunk


def convert_processed_content_to_input_chunks(input_file: str, output_file: str):
    """
    Convert processed content JSON to the format expected by the embedding generator.

    Args:
        input_file: Path to the processed content JSON file
        output_file: Path where the converted chunks should be saved
    """
    # Load the processed content
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert chunks to InputChunk format
    input_chunks = []

    # Check if the data has the expected 'chunks' structure
    if 'chunks' in data:
        # Process the data in the expected format
        for chunk_data in data['chunks']:
            # Skip chunks that are just import statements or too short
            text = chunk_data['text'].strip()
            if len(text) < 20 or text.startswith('import '):
                continue

            # Create metadata from the chunk data
            metadata = {
                'chapter_number': chunk_data.get('chapter_number', ''),
                'title': chunk_data.get('title', ''),
                'section_heading': chunk_data.get('section_heading', ''),
                'source_file': chunk_data.get('source_file', ''),
                'source_url': chunk_data.get('source_url', ''),
                'order_index': chunk_data.get('order_index', 0),
                'original_chunk_id': chunk_data.get('chunk_id', '')
            }

            # Create InputChunk object with UUID for Qdrant compatibility
            import uuid
            input_chunk = InputChunk(
                chunk_id=str(uuid.uuid4()),
                text=chunk_data['text'],
                metadata=metadata
            )

            input_chunks.append(input_chunk.model_dump())
    else:
        # If it doesn't have the expected 'chunks' structure, try to process it differently
        # The processed_content.json has a 'chapters' structure instead
        print("Processing chapters structure...")
        for chapter in data.get('chapters', []):
            for i, file_path in enumerate(chapter.get('files', [])):
                # Create a chunk for each file
                try:
                    # Read the content of the file
                    with open(file_path, 'r', encoding='utf-8') as content_file:
                        content = content_file.read()

                    # Create a chunk_id as a UUID to be compatible with Qdrant
                    import uuid
                    chunk_id = str(uuid.uuid4())

                    # Create metadata
                    metadata = {
                        'chapter_id': chapter.get('chapter_id', ''),
                        'chapter_title': chapter.get('title', ''),
                        'chapter_order': chapter.get('order', 0),
                        'file_path': file_path,
                        'file_name': os.path.basename(file_path)
                    }

                    # Create InputChunk object
                    input_chunk = InputChunk(
                        chunk_id=chunk_id,
                        text=content,
                        metadata=metadata
                    )

                    input_chunks.append(input_chunk.model_dump())

                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    continue

    print(f"Converted content to {len(input_chunks)} input chunks")

    # Write the converted chunks to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(input_chunks, f, indent=2, ensure_ascii=False)

    print(f"Converted chunks saved to {output_file}")


if __name__ == "__main__":
    # Convert the processed content to the format expected by embedding generator
    convert_processed_content_to_input_chunks(
        input_file="processed_content.json",
        output_file="input_chunks_for_embeddings.json"
    )