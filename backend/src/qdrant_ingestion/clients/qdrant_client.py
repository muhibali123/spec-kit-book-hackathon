import time
import asyncio
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from ..config.qdrant_config import QdrantConfig
from ..utils.logger import get_logger
from ..utils.metrics import MetricsAggregator


class QdrantClientWrapper:
    """
    Wrapper class for Qdrant client with error handling and retry logic.
    """

    def __init__(self, config: QdrantConfig):
        self.config = config
        self.client = QdrantClient(
            url=config.url,
            api_key=config.api_key,
            prefer_grpc=False  # Using REST API for better compatibility
        )
        self.logger = get_logger("qdrant_client")
        self.metrics_aggregator = MetricsAggregator()

    def get_client(self) -> QdrantClient:
        """
        Get the Qdrant client instance.
        """
        return self.client

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists in Qdrant.
        """
        try:
            self.client.get_collection(collection_name)
            return True
        except UnexpectedResponse:
            return False
        except Exception:
            return False

    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "Cosine"
    ) -> bool:
        """
        Create a collection in Qdrant with specified parameters.
        """
        try:
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance[distance.upper()]
                ),
                # Enable payload indexing for efficient metadata queries
                optimizers_config=models.OptimizersConfigDiff(
                    memmap_threshold=20000,
                    indexing_threshold=20000,
                )
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to create collection: {str(e)}")

    def validate_collection(
        self,
        collection_name: str,
        expected_vector_size: int,
        expected_distance: str = "Cosine"
    ) -> bool:
        """
        Validate that an existing collection has the expected configuration.
        """
        try:
            collection_info = self.client.get_collection(collection_name)

            # Check vector size
            if collection_info.config.params.vectors.size != expected_vector_size:
                raise ValueError(
                    f"Collection vector size mismatch: expected {expected_vector_size}, "
                    f"got {collection_info.config.params.vectors.size}"
                )

            # Check distance metric
            expected_distance_enum = models.Distance[expected_distance.upper()]
            if collection_info.config.params.vectors.distance != expected_distance_enum:
                raise ValueError(
                    f"Collection distance metric mismatch: expected {expected_distance_enum}, "
                    f"got {collection_info.config.params.vectors.distance}"
                )

            return True
        except Exception as e:
            raise Exception(f"Collection validation failed: {str(e)}")

    def upsert_points(
        self,
        collection_name: str,
        points: List[models.PointStruct]
    ) -> bool:
        """
        Implement network failure handling with retries and exponential backoff strategy for API calls.
        """
        for attempt in range(self.config.retry_attempts + 1):
            try:
                self.logger.debug(f"Attempting to upsert {len(points)} points to collection '{collection_name}' (attempt {attempt + 1})")

                self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )

                self.logger.info(f"Successfully upserted {len(points)} points to collection '{collection_name}'")
                return True
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} to upsert points failed: {str(e)}")

                if attempt < self.config.retry_attempts:
                    # Exponential backoff with jitter to prevent thundering herd
                    base_delay = self.config.retry_delay_ms / 1000
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    jitter = min(delay, 1.0)  # Add small jitter to prevent synchronized retries
                    actual_delay = delay + (jitter * 0.1)  # Small random factor

                    self.logger.info(f"Retrying in {actual_delay:.2f}s...")
                    time.sleep(actual_delay)
                else:
                    error_msg = f"Failed to upsert {len(points)} points after {self.config.retry_attempts} attempts: {str(e)}"
                    self.logger.error(error_msg)
                    raise Exception(error_msg)

        return False

    def close(self):
        """
        Close the Qdrant client connection.
        """
        if hasattr(self.client, 'close'):
            self.client.close()