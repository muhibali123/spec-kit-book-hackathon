"""
Batch processing logic for the embeddings generation module.
"""
from typing import List, Dict, Any
from src.types.embeddings import InputChunk
from src.config.environment import config
import logging


class BatchProcessorError(Exception):
    """
    Custom exception for batch processing errors.
    """
    pass


class BatchProcessor:
    """
    Handles the batching of input chunks for efficient Cohere API calls.
    """

    def __init__(self, batch_size: int = None):
        """
        Initialize the batch processor.

        Args:
            batch_size: Maximum number of chunks per batch (uses config if not provided)
        """
        self.batch_size = batch_size or config.batch_size

        # Cohere API has a limit on the number of texts per request
        # The actual limit is 96, but we'll use the configured value or 64 as default
        if self.batch_size > 96:
            logging.warning(f"Batch size {self.batch_size} exceeds Cohere's recommended limit of 96. Using 96.")
            self.batch_size = 96

    def create_batches(self, chunks: List[InputChunk]) -> List[List[InputChunk]]:
        """
        Create batches of input chunks.

        Args:
            chunks: List of input chunks to batch

        Returns:
            List of batches, where each batch is a list of InputChunk objects
        """
        if not chunks:
            return []

        batches = []
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            batches.append(batch)

        return batches

    def extract_texts_from_batch(self, batch: List[InputChunk]) -> List[str]:
        """
        Extract text content from a batch of input chunks.

        Args:
            batch: Batch of input chunks

        Returns:
            List of text strings from the chunks
        """
        return [chunk.text for chunk in batch]

    def validate_batch(self, batch: List[InputChunk]) -> bool:
        """
        Validate a batch of input chunks.

        Args:
            batch: Batch of input chunks to validate

        Returns:
            bool: True if the batch is valid
        """
        if not isinstance(batch, list):
            raise BatchProcessorError("Batch must be a list")

        if len(batch) == 0:
            raise BatchProcessorError("Batch cannot be empty")

        if len(batch) > self.batch_size:
            raise BatchProcessorError(f"Batch size {len(batch)} exceeds maximum {self.batch_size}")

        # Validate each chunk in the batch
        for i, chunk in enumerate(batch):
            if not isinstance(chunk, InputChunk):
                raise BatchProcessorError(f"Item at index {i} is not an InputChunk")

            if not chunk.text or not chunk.text.strip():
                raise BatchProcessorError(f"Chunk at index {i} has empty text")

        return True

    def preserve_order_mapping(self, chunks: List[InputChunk]) -> Dict[int, str]:
        """
        Create a mapping to preserve the original order of chunks after processing.

        Args:
            chunks: List of input chunks

        Returns:
            Dictionary mapping index to chunk_id to maintain order
        """
        return {i: chunk.chunk_id for i, chunk in enumerate(chunks)}

    def create_batch_with_original_indices(self, chunks: List[InputChunk]) -> List[tuple]:
        """
        Create a batch with original indices to preserve order after processing.

        Args:
            chunks: List of input chunks

        Returns:
            List of tuples (index, chunk) to maintain original order
        """
        return [(i, chunk) for i, chunk in enumerate(chunks)]