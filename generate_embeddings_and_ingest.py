#!/usr/bin/env python3
"""
Script to generate embeddings from input chunks and ingest them into Qdrant.
"""
import asyncio
import json
import os
from pathlib import Path

# Add the backend directory to the path so we can import modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

from src.embeddings.generator import EmbeddingGenerator
from src.embeddings.validator import Validator
from src.utils.file_handler import FileHandler


async def main():
    print("Starting embedding generation and ingestion process...")

    # Load input file
    input_file_path = os.path.join(os.path.dirname(__file__), 'input_chunks_for_embeddings.json')
    output_file_path = os.path.join(os.path.dirname(__file__), 'embeddings_output.json')

    print(f"Reading input from: {input_file_path}")

    # Read input file
    chunk_dicts = FileHandler.read_json_file(input_file_path)

    # Validate and convert to InputChunk objects
    chunks = Validator.validate_input_chunks(chunk_dicts)

    print(f"Found {len(chunks)} chunks to process")

    # Initialize embedding generator
    generator = EmbeddingGenerator(
        api_key=os.getenv('COHERE_API_KEY'),
        model=os.getenv('COHERE_MODEL', 'embed-multilingual-v2.0')
    )

    print("Generating embeddings...")
    result = generator.generate_embeddings_from_chunks(chunks)

    print(f"Generated {len(result.results)} embeddings successfully")
    print(f"Failed: {result.summary['failed']}")
    print(f"Processing time: {result.summary['processing_time_ms']}ms")

    # Prepare output data in the format expected by the Qdrant ingestion
    output_data = [
        {
            "chunk_id": record.chunk_id,
            "embedding": record.embedding,
            "text": record.text,
            "metadata": record.metadata,
            "model": record.embedding_model,
            "dimension": record.embedding_dimension
        }
        for record in result.results
    ]

    # Write embeddings to output file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Embeddings saved to: {output_file_path}")

    # Now run the Qdrant ingestion
    print("Starting Qdrant ingestion...")

    # Import and run the ingestion
    from backend.src.qdrant_ingestion.index import main_ingestion_workflow

    ingestion_result = main_ingestion_workflow(output_file_path)
    print(f"Ingestion completed: {ingestion_result}")

    print("Process completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())