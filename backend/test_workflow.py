"""
Test script to validate the complete embeddings generation workflow.
"""
import json
import tempfile
import os
from pathlib import Path

# Add the backend/src directory to the path so we can import modules
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.embeddings.generator import EmbeddingGenerator
from src.embeddings.validator import Validator
from src.types.embeddings import InputChunk
from src.config.environment import config


def create_sample_input_file(file_path: str):
    """
    Create a sample input file for testing.

    Args:
        file_path: Path where the sample input file should be created
    """
    sample_chunks = [
        {
            "chunk_id": "chunk-001",
            "text": "This is the first sample chunk of text for embedding generation.",
            "metadata": {
                "chapter_number": 1,
                "title": "Introduction",
                "section_heading": "Getting Started"
            }
        },
        {
            "chunk_id": "chunk-002",
            "text": "This is the second sample chunk with different content to test the embedding process.",
            "metadata": {
                "chapter_number": 1,
                "title": "Introduction",
                "section_heading": "Basic Concepts"
            }
        },
        {
            "chunk_id": "chunk-003",
            "text": "Finally, this third chunk tests the processing of the last item in our sample data.",
            "metadata": {
                "chapter_number": 1,
                "title": "Introduction",
                "section_heading": "Conclusion"
            }
        }
    ]

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(sample_chunks, f, indent=2)


def test_complete_workflow():
    """
    Test the complete embeddings generation workflow.
    """
    print("Starting complete workflow test...")

    # Create temporary files for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
        input_path = input_file.name

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as output_file:
        output_path = output_file.name

    try:
        # Create sample input
        create_sample_input_file(input_path)
        print(f"✓ Created sample input file: {input_path}")

        # Initialize the generator
        generator = EmbeddingGenerator()
        print("✓ Initialized embedding generator")

        # Generate embeddings
        print("✓ Starting embedding generation...")
        result = generator.generate_embeddings_from_file(input_path, output_path)

        print(f"✓ Generated embeddings for {len(result.results)} chunks")
        print(f"✓ Process summary: {result.summary}")

        # Verify the output file was created
        assert os.path.exists(output_path), "Output file was not created"
        print("✓ Output file was created successfully")

        # Read and validate the output
        with open(output_path, 'r', encoding='utf-8') as f:
            output_data = json.load(f)

        assert 'results' in output_data, "Output missing 'results' field"
        assert 'summary' in output_data, "Output missing 'summary' field"
        assert 'process_id' in output_data, "Output missing 'process_id' field"
        print("✓ Output file has correct structure")

        # Validate the results
        assert len(output_data['results']) == 3, f"Expected 3 results, got {len(output_data['results'])}"
        print("✓ Correct number of results generated")

        # Check that all required fields are present in each result
        for i, record in enumerate(output_data['results']):
            required_fields = ['chunk_id', 'embedding', 'text', 'metadata', 'embedding_model', 'embedding_dimension']
            for field in required_fields:
                assert field in record, f"Result {i} missing required field: {field}"

            # Verify embedding is a list of numbers
            assert isinstance(record['embedding'], list), f"Result {i} embedding is not a list"
            assert len(record['embedding']) > 0, f"Result {i} embedding is empty"
            assert all(isinstance(val, (int, float)) for val in record['embedding']), f"Result {i} embedding contains non-numeric values"

            # Verify dimensions match
            assert len(record['embedding']) == record['embedding_dimension'], f"Result {i} embedding length doesn't match dimension"

        print("✓ All results have correct structure and data types")

        # Verify text and metadata preservation
        input_chunks = json.load(open(input_path, 'r', encoding='utf-8'))
        input_map = {chunk['chunk_id']: chunk for chunk in input_chunks}

        for record in output_data['results']:
            original = input_map[record['chunk_id']]
            assert record['text'] == original['text'], f"Text not preserved for chunk {record['chunk_id']}"
            assert record['metadata'] == original['metadata'], f"Metadata not preserved for chunk {record['chunk_id']}"

        print("✓ Original text and metadata preserved correctly")

        # Verify model consistency
        first_model = output_data['results'][0]['embedding_model']
        for record in output_data['results']:
            assert record['embedding_model'] == first_model, "Model is not consistent across records"

        print("✓ Embedding model is consistent across all records")

        # Validate using the Validator
        validated_results = Validator.validate_output_records([
            record for record in output_data['results']
        ])
        assert validated_results, "Output validation failed"
        print("✓ Output validation passed")

        # Check summary statistics
        summary = output_data['summary']
        assert summary['total_chunks'] == 3, "Incorrect total chunks in summary"
        assert summary['successful'] == 3, "Incorrect successful count in summary"
        assert summary['failed'] == 0, "Incorrect failed count in summary"
        assert summary['model_used'] == config.cohere_model, "Incorrect model in summary"

        print("✓ Summary statistics are correct")

        print("\n✓ All tests passed! The complete workflow is working correctly.")
        print(f"✓ Processed {summary['total_chunks']} chunks successfully")
        print(f"✓ Total processing time: {summary['processing_time_ms']}ms")

    finally:
        # Clean up temporary files
        if os.path.exists(input_path):
            os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)
        print(f"✓ Cleaned up temporary files")


if __name__ == "__main__":
    if not config.cohere_api_key:
        print("Error: COHERE_API_KEY environment variable is not set", file=sys.stderr)
        print("Please set the API key before running this test", file=sys.stderr)
        sys.exit(1)

    test_complete_workflow()