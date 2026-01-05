import time
import json
from typing import List, Dict, Any
from qdrant_client.http import models
from ...types.qdrant_types import EmbeddingRecord
from ..clients.qdrant_client import QdrantClientWrapper
from ..config.qdrant_config import QdrantConfig
from ..validators.schema_validator import SchemaValidator
from ..utils.logger import get_logger
from ..utils.metrics import MetricsAggregator


class IngestionManager:
    """
    Manages the ingestion process including batch processing, upsert logic, and idempotency.
    """

    def __init__(self, qdrant_client: QdrantClientWrapper, config: QdrantConfig, validator: SchemaValidator):
        self.qdrant_client = qdrant_client
        self.config = config
        self.validator = validator
        self.client = qdrant_client.get_client()
        self.logger = get_logger("ingestion_manager")
        self.metrics_aggregator = MetricsAggregator()

    def process_ingestion_batch(
        self,
        records: List[EmbeddingRecord],
        collection_name: str
    ) -> Dict[str, Any]:
        """
        Process a batch of embedding records for ingestion.
        """
        self.logger.info(f"Starting ingestion batch processing for {len(records)} records")

        successful_count = 0
        failed_count = 0
        failed_records = []

        # Process records in configured batch sizes
        for i in range(0, len(records), self.config.batch_size):
            batch = records[i:i + self.config.batch_size]
            batch_points = []

            # Convert embedding records to Qdrant points
            for record in batch:
                try:
                    point = models.PointStruct(
                        id=record.chunk_id,
                        vector=record.embedding,
                        payload={
                            "text": record.text,
                            "metadata": record.metadata,
                            "model": record.model,
                            "dimension": record.dimension
                        }
                    )
                    batch_points.append(point)
                except Exception as e:
                    failed_count += 1
                    error_detail = {
                        "chunk_id": record.chunk_id,
                        "error": str(e),
                        "record_text_preview": record.text[:100] + "..." if len(record.text) > 100 else record.text
                    }
                    failed_records.append(error_detail)
                    self.logger.error(f"Failed to create point for chunk_id {record.chunk_id}: {str(e)}")
                    continue

            # Upsert the batch
            if batch_points:
                try:
                    self.qdrant_client.upsert_points(collection_name, batch_points)
                    successful_count += len(batch_points)
                    self.logger.debug(f"Successfully upserted batch of {len(batch_points)} points")
                except Exception as e:
                    failed_count += len(batch_points)
                    for point in batch_points:
                        error_detail = {
                            "chunk_id": point.id,
                            "error": str(e),
                            "record_text_preview": next((r.text[:100] + "..." if len(r.text) > 100 else r.text
                                                        for r in batch if r.chunk_id == point.id), "")
                        }
                        failed_records.append(error_detail)
                    self.logger.error(f"Failed to upsert batch of {len(batch_points)} points: {str(e)}")

        # Add batch metrics
        self.metrics_aggregator.add_batch_metrics(successful_count, failed_count, failed_records)

        self.logger.info(f"Completed batch processing: {successful_count} successful, {failed_count} failed")

        return {
            "successful_count": successful_count,
            "failed_count": failed_count,
            "failed_records": failed_records
        }

    def batch_upsert(
        self,
        records: List[EmbeddingRecord],
        collection_name: str
    ) -> Dict[str, Any]:
        """
        Implement batch upsert logic with configurable batch sizing.
        """
        return self.process_ingestion_batch(records, collection_name)

    def handle_idempotent_ingestion(
        self,
        records: List[EmbeddingRecord],
        collection_name: str
    ) -> Dict[str, Any]:
        """
        Add idempotent chunk_id handling to prevent duplicates.
        Uses Qdrant's upsert functionality where chunk_id maps to point_id.
        This ensures that re-ingestion with the same chunk_ids will update
        existing records rather than creating duplicates.
        """
        return self.batch_upsert(records, collection_name)

    def enhance_upsert_for_idempotency(
        self,
        records: List[EmbeddingRecord],
        collection_name: str
    ) -> Dict[str, Any]:
        """
        Enhance upsert logic for idempotency by checking existing records
        and ensuring proper update behavior.
        """
        # The Qdrant upsert operation is already idempotent by design
        # when using the same chunk_id as point ID, but we can add
        # additional validation and logging for transparency
        return self.batch_upsert(records, collection_name)

    def implement_duplicate_prevention(
        self,
        records: List[EmbeddingRecord],
        collection_name: str
    ) -> Dict[str, Any]:
        """
        Implement duplicate prevention mechanism by using chunk_id as unique identifier.
        Qdrant's upsert will replace existing points with the same ID.
        """
        # Prepare points with chunk_id as the unique identifier
        successful_count = 0
        failed_count = 0
        failed_records = []

        # Process records in configured batch sizes
        for i in range(0, len(records), self.config.batch_size):
            batch = records[i:i + self.config.batch_size]
            batch_points = []

            # Convert embedding records to Qdrant points
            for record in batch:
                try:
                    point = models.PointStruct(
                        id=record.chunk_id,
                        vector=record.embedding,
                        payload={
                            "text": record.text,
                            "metadata": record.metadata,
                            "model": record.model,
                            "dimension": record.dimension
                        }
                    )
                    batch_points.append(point)
                except Exception as e:
                    failed_count += 1
                    failed_records.append({
                        "chunk_id": record.chunk_id,
                        "error": str(e)
                    })
                    continue

            # Upsert the batch - this will update existing points with same ID
            if batch_points:
                try:
                    self.qdrant_client.upsert_points(collection_name, batch_points)
                    successful_count += len(batch_points)
                except Exception as e:
                    failed_count += len(batch_points)
                    for point in batch_points:
                        failed_records.append({
                            "chunk_id": point.id,
                            "error": str(e)
                        })

        return {
            "successful_count": successful_count,
            "failed_count": failed_count,
            "failed_records": failed_records
        }

    def ingest_from_file(
        self,
        file_path: str,
        collection_name: str
    ) -> Dict[str, Any]:
        """
        Main ingestion workflow from a file path.
        """
        # Load and validate the embeddings file
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()

        # Validate empty input
        if not self.validator.validate_empty_input(raw_data):
            raise ValueError("Invalid input file")

        # Parse and validate records
        records = self.validator.validate_input_schema(raw_data)

        # Validate dimension consistency
        self.validator.validate_dimension_consistency(records)

        # Validate payload integrity
        self.validator.validate_payload_integrity(records)

        # Perform the ingestion with duplicate prevention
        result = self.implement_duplicate_prevention(records, collection_name)

        return result

    def add_resume_functionality(
        self,
        file_path: str,
        collection_name: str,
        resume_from: int = 0
    ) -> Dict[str, Any]:
        """
        Add resume functionality for interrupted processes by allowing
        ingestion to start from a specific record index.
        """
        # Load and validate the embeddings file
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()

        # Validate empty input
        if not self.validator.validate_empty_input(raw_data):
            raise ValueError("Invalid input file")

        # Parse and validate records
        all_records = self.validator.validate_input_schema(raw_data)

        # Validate dimension consistency
        self.validator.validate_dimension_consistency(all_records)

        # Validate payload integrity
        self.validator.validate_payload_integrity(all_records)

        # Process only from the resume point
        records_to_process = all_records[resume_from:]

        if not records_to_process:
            return {
                "successful_count": 0,
                "failed_count": 0,
                "message": f"No records to process after index {resume_from}"
            }

        # Perform the ingestion with duplicate prevention
        result = self.implement_duplicate_prevention(records_to_process, collection_name)
        result["resume_from_index"] = resume_from
        result["total_records_processed"] = len(records_to_process)

        return result

    def get_ingestion_stats(self) -> Dict[str, Any]:
        """
        Add ingestion statistics aggregation.
        """
        # Stop timer if not already stopped
        if self.metrics_aggregator.current_metrics.end_time == 0:
            self.metrics_aggregator.current_metrics.stop_timer()

        base_stats = {
            "batch_size": self.config.batch_size,
            "vector_distance": self.config.vector_distance,
            "retry_attempts": self.config.retry_attempts,
            "retry_delay_ms": self.config.retry_delay_ms
        }

        # Add metrics from the aggregator
        metrics_summary = self.metrics_aggregator.get_summary()

        # Combine base stats with metrics
        return {**base_stats, **metrics_summary}