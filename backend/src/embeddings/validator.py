"""
Input and output validation logic for the embeddings generation module.
"""
import json
import hashlib
from typing import List, Dict, Any, Union
from src.types.embeddings import InputChunk, EmbeddingRecord
import logging
import copy


class ValidationError(Exception):
    """
    Custom exception for validation errors.
    """
    pass


def deep_compare(obj1: Any, obj2: Any) -> bool:
    """
    Perform a deep comparison between two objects to check if they are equivalent.

    Args:
        obj1: First object to compare
        obj2: Second object to compare

    Returns:
        bool: True if objects are equivalent, False otherwise
    """
    if type(obj1) != type(obj2):
        return False

    if isinstance(obj1, (str, int, float, bool, type(None))):
        return obj1 == obj2

    elif isinstance(obj1, (list, tuple)):
        if len(obj1) != len(obj2):
            return False
        for item1, item2 in zip(obj1, obj2):
            if not deep_compare(item1, item2):
                return False
        return True

    elif isinstance(obj1, dict):
        if set(obj1.keys()) != set(obj2.keys()):
            return False
        for key in obj1.keys():
            if not deep_compare(obj1[key], obj2[key]):
                return False
        return True

    else:
        # For other types, use direct comparison
        return obj1 == obj2


class Validator:
    """
    Provides validation functionality for input and output data.
    """

    @staticmethod
    def validate_input_chunks(chunks: List[Dict[str, Any]]) -> List[InputChunk]:
        """
        Validate input chunks from Module 01.

        Args:
            chunks: List of chunk dictionaries from Module 01

        Returns:
            List[InputChunk]: Validated and typed input chunks

        Raises:
            ValidationError: If any chunk fails validation
        """
        validated_chunks = []

        if not isinstance(chunks, list):
            raise ValidationError("Input must be a list of chunks")

        for i, chunk_data in enumerate(chunks):
            try:
                # Validate basic structure
                if not isinstance(chunk_data, dict):
                    raise ValidationError(f"Chunk at index {i} is not a dictionary")

                if "chunk_id" not in chunk_data:
                    raise ValidationError(f"Chunk at index {i} missing required 'chunk_id' field")

                if "text" not in chunk_data:
                    raise ValidationError(f"Chunk at index {i} missing required 'text' field")

                if "metadata" not in chunk_data:
                    raise ValidationError(f"Chunk at index {i} missing required 'metadata' field")

                # Validate field types
                if not isinstance(chunk_data["chunk_id"], str) or not chunk_data["chunk_id"].strip():
                    raise ValidationError(f"Chunk at index {i} has invalid or empty 'chunk_id'")

                if not isinstance(chunk_data["text"], str) or not chunk_data["text"].strip():
                    raise ValidationError(f"Chunk at index {i} has invalid or empty 'text'")

                if not isinstance(chunk_data["metadata"], dict):
                    raise ValidationError(f"Chunk at index {i} has invalid 'metadata' - must be a dictionary")

                # Create and validate InputChunk instance
                input_chunk = InputChunk(
                    chunk_id=chunk_data["chunk_id"],
                    text=chunk_data["text"],
                    metadata=chunk_data["metadata"]
                )

                validated_chunks.append(input_chunk)

            except Exception as e:
                raise ValidationError(f"Validation error for chunk at index {i}: {str(e)}")

        return validated_chunks

    @staticmethod
    def validate_embedding_record(record: EmbeddingRecord) -> bool:
        """
        Validate an embedding record.

        Args:
            record: The embedding record to validate

        Returns:
            bool: True if valid, raises ValidationError if invalid
        """
        # Validate basic structure
        if not isinstance(record, EmbeddingRecord):
            raise ValidationError("Record is not an EmbeddingRecord instance")

        # Validate chunk_id
        if not record.chunk_id or not isinstance(record.chunk_id, str):
            raise ValidationError(f"Invalid chunk_id: {record.chunk_id}")

        # Validate embedding
        if not isinstance(record.embedding, list):
            raise ValidationError(f"Embedding must be a list, got {type(record.embedding)}")

        if len(record.embedding) == 0:
            raise ValidationError("Embedding cannot be empty")

        for i, value in enumerate(record.embedding):
            if not isinstance(value, (int, float)):
                raise ValidationError(f"Embedding[{i}] must be a number, got {type(value)}")

        # Validate text preservation
        if not record.text or not isinstance(record.text, str):
            raise ValidationError(f"Invalid text: {record.text}")

        # Validate metadata preservation
        if not isinstance(record.metadata, dict):
            raise ValidationError(f"Invalid metadata: {record.metadata}")

        # Validate model
        if not record.embedding_model or not isinstance(record.embedding_model, str):
            raise ValidationError(f"Invalid embedding_model: {record.embedding_model}")

        # Validate dimension
        if not isinstance(record.embedding_dimension, int) or record.embedding_dimension <= 0:
            raise ValidationError(f"Invalid embedding_dimension: {record.embedding_dimension}")

        # Check that embedding dimension matches actual length
        if len(record.embedding) != record.embedding_dimension:
            raise ValidationError(
                f"Embedding length ({len(record.embedding)}) does not match embedding_dimension ({record.embedding_dimension})"
            )

        return True

    @staticmethod
    def validate_output_records(records: List[EmbeddingRecord]) -> bool:
        """
        Validate a list of embedding records.

        Args:
            records: List of embedding records to validate

        Returns:
            bool: True if all records are valid
        """
        if not isinstance(records, list):
            raise ValidationError("Output must be a list of embedding records")

        for i, record in enumerate(records):
            try:
                Validator.validate_embedding_record(record)
            except ValidationError as e:
                raise ValidationError(f"Validation error for record at index {i}: {str(e)}")

        return True

    @staticmethod
    def validate_json_format(json_data: Union[str, Dict, List]) -> bool:
        """
        Validate that the input is valid JSON.

        Args:
            json_data: JSON data to validate

        Returns:
            bool: True if valid JSON format
        """
        try:
            if isinstance(json_data, str):
                parsed = json.loads(json_data)
            else:
                parsed = json_data

            # Check if it's a list of chunks
            if not isinstance(parsed, list):
                raise ValidationError("JSON must be a list of chunks")

            return True
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format: {str(e)}")

    @staticmethod
    def calculate_checksum(data: Union[str, Dict, List, InputChunk, EmbeddingRecord]) -> str:
        """
        Calculate a checksum for data to verify integrity.

        Args:
            data: Data to calculate checksum for

        Returns:
            str: SHA-256 checksum of the data
        """
        if isinstance(data, (InputChunk, EmbeddingRecord)):
            # Convert to dict for consistent hashing
            data_str = json.dumps(data.model_dump(), sort_keys=True, default=str)
        elif isinstance(data, (dict, list)):
            # Sort keys for consistent hashing
            data_str = json.dumps(data, sort_keys=True, default=str)
        elif isinstance(data, str):
            data_str = data
        else:
            # Convert other types to string
            data_str = str(data)

        # Calculate SHA-256 hash
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_checksum(data: Union[str, Dict, List, InputChunk, EmbeddingRecord], expected_checksum: str) -> bool:
        """
        Verify that the data matches the expected checksum.

        Args:
            data: Data to verify
            expected_checksum: Expected checksum

        Returns:
            bool: True if checksum matches, False otherwise
        """
        actual_checksum = Validator.calculate_checksum(data)
        return actual_checksum == expected_checksum

    @staticmethod
    def validate_text_integrity(original_chunks: List[InputChunk], generated_records: List[EmbeddingRecord]) -> bool:
        """
        Validate that the original text is preserved in the generated records using checksums.

        Args:
            original_chunks: Original input chunks
            generated_records: Generated embedding records

        Returns:
            bool: True if text integrity is preserved
        """
        if len(original_chunks) != len(generated_records):
            return False

        # Create a mapping from chunk_id to original chunk for comparison
        original_map = {chunk.chunk_id: chunk for chunk in original_chunks}

        for record in generated_records:
            original_chunk = original_map.get(record.chunk_id)
            if not original_chunk:
                return False

            # Compare text using checksums
            original_checksum = Validator.calculate_checksum(original_chunk.text)
            record_checksum = Validator.calculate_checksum(record.text)

            if original_checksum != record_checksum:
                return False

        return True

    @staticmethod
    def validate_metadata_integrity(original_chunks: List[InputChunk], generated_records: List[EmbeddingRecord]) -> bool:
        """
        Validate that the original metadata is preserved in the generated records using checksums.

        Args:
            original_chunks: Original input chunks
            generated_records: Generated embedding records

        Returns:
            bool: True if metadata integrity is preserved
        """
        if len(original_chunks) != len(generated_records):
            return False

        # Create a mapping from chunk_id to original chunk for comparison
        original_map = {chunk.chunk_id: chunk for chunk in original_chunks}

        for record in generated_records:
            original_chunk = original_map.get(record.chunk_id)
            if not original_chunk:
                return False

            # Compare metadata using checksums
            original_checksum = Validator.calculate_checksum(original_chunk.metadata)
            record_checksum = Validator.calculate_checksum(record.metadata)

            if original_checksum != record_checksum:
                return False

        return True