"""
Core embedding generation logic for the embeddings generation module.
"""
import time
import uuid
from typing import List, Dict, Any
from src.types.embeddings import InputChunk, EmbeddingRecord, ProcessingResult, ProcessSummary
from src.config.environment import config
from src.embeddings.cohere_client import CohereClient
from src.embeddings.batch_processor import BatchProcessor
from src.embeddings.validator import Validator
from src.embeddings.logger import logger
from src.utils.file_handler import FileHandler
from src.utils.retry import RetryHandler
from src.utils.circuit_breaker import CircuitBreaker, CircuitBreakerError
import logging


class EmbeddingGeneratorError(Exception):
    """
    Custom exception for embedding generation errors.
    """
    pass


class EmbeddingGenerator:
    """
    Core class for generating embeddings from input chunks.
    """

    def __init__(self, api_key: str = None, model: str = None, batch_size: int = None):
        """
        Initialize the embedding generator.

        Args:
            api_key: Cohere API key (uses config if not provided)
            model: Embedding model to use (uses config if not provided)
            batch_size: Batch size for API calls (uses config if not provided)
        """
        self.cohere_client = CohereClient(api_key=api_key, model=model or config.cohere_model)
        self.batch_processor = BatchProcessor(batch_size=batch_size or config.batch_size)
        self.model = model or config.cohere_model
        self.retry_handler = RetryHandler(
            max_retries=config.max_retries,
            base_delay=config.retry_delay / 1000.0,  # Convert to seconds
            allowed_exceptions=(Exception,)
        )

    def generate_embeddings_from_chunks(self, chunks: List[InputChunk]) -> ProcessingResult:
        """
        Generate embeddings for a list of input chunks.

        Args:
            chunks: List of input chunks to process

        Returns:
            ProcessingResult containing the embedding records and summary
        """
        start_time = time.time()
        process_id = str(uuid.uuid4())

        # Log process start
        logger.log_process_start(process_id, len(chunks))

        # Validate input
        if not chunks:
            raise EmbeddingGeneratorError("Input chunks list cannot be empty")

        # Initialize results
        results = []
        successful_count = 0
        failed_count = 0

        # Create batches
        batches = self.batch_processor.create_batches(chunks)

        # Process each batch
        for batch_idx, batch in enumerate(batches):
            batch_start_time = time.time()
            logging.info(f"Processing batch {batch_idx + 1}/{len(batches)} with {len(batch)} chunks")

            # Try to process the entire batch first
            batch_success = False
            try:
                # Extract texts from the batch
                texts = self.batch_processor.extract_texts_from_batch(batch)

                # Generate embeddings for the batch
                embeddings = self.cohere_client.generate_embeddings(texts)

                # Verify that we got the expected number of embeddings
                if len(embeddings) != len(batch):
                    raise EmbeddingGeneratorError(
                        f"Expected {len(batch)} embeddings, got {len(embeddings)}"
                    )

                # Create embedding records
                for i, (chunk, embedding) in enumerate(zip(batch, embeddings)):
                    embedding_record = EmbeddingRecord(
                        chunk_id=chunk.chunk_id,
                        embedding=embedding,
                        text=chunk.text,  # Preserve original text
                        metadata=chunk.metadata,  # Preserve original metadata
                        embedding_model=self.model,
                        embedding_dimension=len(embedding)
                    )

                    # Validate the embedding record
                    Validator.validate_embedding_record(embedding_record)

                    results.append(embedding_record)
                    successful_count += 1

                batch_success = True
                batch_duration = int((time.time() - batch_start_time) * 1000)

                # Log successful batch
                logger.log_batch_processed(
                    batch_id=f"{process_id}_batch_{batch_idx}",
                    total_chunks=len(batch),
                    successful=len(batch),
                    failed=0,
                    duration_ms=batch_duration
                )

            except Exception as e:
                logging.error(f"Failed to process batch {batch_idx + 1}: {str(e)}")

                # If the whole batch failed, try partial recovery by processing chunks individually
                logging.info(f"Attempting partial recovery for batch {batch_idx + 1}")

                for chunk_idx, chunk in enumerate(batch):
                    try:
                        # Process individual chunk with retry
                        embedding = self.retry_handler.execute_with_retry(
                            self.cohere_client.generate_embeddings,
                            [chunk.text]
                        )

                        # Extract the single embedding from the list
                        single_embedding = embedding[0]

                        embedding_record = EmbeddingRecord(
                            chunk_id=chunk.chunk_id,
                            embedding=single_embedding,
                            text=chunk.text,  # Preserve original text
                            metadata=chunk.metadata,  # Preserve original metadata
                            embedding_model=self.model,
                            embedding_dimension=len(single_embedding)
                        )

                        # Validate the embedding record
                        Validator.validate_embedding_record(embedding_record)

                        results.append(embedding_record)
                        successful_count += 1

                    except Exception as chunk_error:
                        logging.error(f"Failed to process individual chunk {chunk.chunk_id}: {str(chunk_error)}")
                        logger.log_chunk_failure(chunk.chunk_id, str(chunk_error))
                        failed_count += 1

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Create summary
        summary = {
            "total_chunks": len(chunks),
            "successful": successful_count,
            "failed": failed_count,
            "processing_time_ms": processing_time_ms,
            "model_used": self.model
        }

        # Log process completion
        logger.log_process_complete(
            process_id=process_id,
            successful=successful_count,
            failed=failed_count,
            duration_ms=processing_time_ms
        )

        # Create processing result
        result = ProcessingResult(
            process_id=process_id,
            results=results,
            summary=summary
        )

        # Validate the output records
        Validator.validate_output_records(result.results)

        return result

    def generate_embeddings_from_file(self, input_file_path: str, output_file_path: str) -> ProcessingResult:
        """
        Generate embeddings from an input file and save to an output file.

        Args:
            input_file_path: Path to the input JSON file with chunks
            output_file_path: Path where the output JSON with embeddings should be saved

        Returns:
            ProcessingResult containing the embedding records and summary
        """
        # Read input file
        chunk_dicts = FileHandler.read_json_file(input_file_path)

        # Validate and convert to InputChunk objects
        chunks = Validator.validate_input_chunks(chunk_dicts)

        # Generate embeddings
        result = self.generate_embeddings_from_chunks(chunks)

        # Prepare output data
        output_data = [
            {
                "chunk_id": record.chunk_id,
                "embedding": record.embedding,
                "text": record.text,
                "metadata": record.metadata,
                "embedding_model": record.embedding_model,
                "embedding_dimension": record.embedding_dimension
            }
            for record in result.results
        ]

        # Write output file
        output_with_summary = {
            "process_id": result.process_id,
            "results": output_data,
            "summary": result.summary
        }

        FileHandler.write_json_file(output_file_path, output_with_summary)

        return result

    def validate_model_consistency(self, results: List[EmbeddingRecord]) -> bool:
        """
        Validate that all embeddings were generated with the same model.

        Args:
            results: List of embedding records

        Returns:
            bool: True if all records use the same model
        """
        if not results:
            return True

        first_model = results[0].embedding_model
        for record in results:
            if record.embedding_model != first_model:
                return False

        return True

    def ensure_text_preservation(self, original_chunks: List[InputChunk],
                                generated_records: List[EmbeddingRecord]) -> bool:
        """
        Ensure that the original text is preserved in the generated records.

        Args:
            original_chunks: Original input chunks
            generated_records: Generated embedding records

        Returns:
            bool: True if text is preserved for all records
        """
        if len(original_chunks) != len(generated_records):
            return False

        # Create a mapping from chunk_id to original chunk for comparison
        original_map = {chunk.chunk_id: chunk for chunk in original_chunks}

        for record in generated_records:
            original_chunk = original_map.get(record.chunk_id)
            if not original_chunk:
                return False
            if original_chunk.text != record.text:
                return False

        return True

    def ensure_metadata_preservation(self, original_chunks: List[InputChunk],
                                   generated_records: List[EmbeddingRecord]) -> bool:
        """
        Ensure that the original metadata is preserved in the generated records.

        Args:
            original_chunks: Original input chunks
            generated_records: Generated embedding records

        Returns:
            bool: True if metadata is preserved for all records
        """
        if len(original_chunks) != len(generated_records):
            return False

        # Create a mapping from chunk_id to original chunk for comparison
        original_map = {chunk.chunk_id: chunk for chunk in original_chunks}

        for record in generated_records:
            original_chunk = original_map.get(record.chunk_id)
            if not original_chunk:
                return False
            if original_chunk.metadata != record.metadata:
                return False

        return True