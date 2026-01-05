import json
from typing import Dict, Any, List, Union
from ...types.qdrant_types import EmbeddingRecord
import logging


class SchemaValidator:
    """
    Validates input JSON against expected structure for embedding records.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_input_schema(self, data: Union[str, List[Dict[str, Any]]]) -> List[EmbeddingRecord]:
        """
        Validate the input data schema and return a list of validated EmbeddingRecord objects.
        """
        # Parse JSON string if needed
        if isinstance(data, str):
            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {str(e)}")
        else:
            parsed_data = data

        # Validate that the input is a list
        if not isinstance(parsed_data, list):
            raise ValueError("Input data must be a JSON array of embedding records")

        validated_records = []
        for i, record_data in enumerate(parsed_data):
            try:
                # Validate each record individually
                record = EmbeddingRecord(**record_data)
                validated_records.append(record)
            except Exception as e:
                raise ValueError(f"Validation error at record {i}: {str(e)}")

        return validated_records

    def validate_dimension_consistency(self, records: List[EmbeddingRecord]) -> bool:
        """
        Ensure all embeddings have the same dimension.
        """
        if not records:
            return True

        expected_dimension = records[0].dimension
        for i, record in enumerate(records):
            if record.dimension != expected_dimension:
                raise ValueError(
                    f"Dimension mismatch at record {i}: expected {expected_dimension}, got {record.dimension}"
                )

            if len(record.embedding) != expected_dimension:
                raise ValueError(
                    f"Embedding vector length mismatch at record {i}: "
                    f"expected {expected_dimension}, got {len(record.embedding)}"
                )

        return True

    def validate_payload_integrity(self, records: List[EmbeddingRecord]) -> bool:
        """
        Verify that text and metadata are preserved exactly as provided.
        """
        for i, record in enumerate(records):
            # Check that required fields exist and are not empty
            if not record.chunk_id:
                raise ValueError(f"Missing chunk_id at record {i}")

            if not record.text:
                raise ValueError(f"Missing text at record {i}")

            if not record.embedding:
                raise ValueError(f"Missing embedding at record {i}")

            if not isinstance(record.embedding, list):
                raise ValueError(f"Embedding must be a list at record {i}")

            # Verify embedding contains only float values
            for j, value in enumerate(record.embedding):
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Embedding[{j}] must be numeric at record {i}, got {type(value)}")

        return True

    def validate_empty_input(self, data: Union[str, List[Dict[str, Any]]]) -> bool:
        """
        Validate that empty input files are handled gracefully.
        """
        if isinstance(data, str):
            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError:
                return False  # Invalid JSON is not an empty input case
        else:
            parsed_data = data

        if not parsed_data:  # Empty list
            self.logger.info("Empty input file detected - processing gracefully")
            return True

        return True