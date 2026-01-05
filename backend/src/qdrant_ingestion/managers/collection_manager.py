from typing import Optional
from qdrant_client.http import models
from ..clients.qdrant_client import QdrantClientWrapper
from ..config.qdrant_config import QdrantConfig


class CollectionManager:
    """
    Manages Qdrant collection operations including creation, validation, and configuration.
    """

    def __init__(self, qdrant_client: QdrantClientWrapper, config: QdrantConfig):
        self.qdrant_client = qdrant_client
        self.config = config

    def ensure_collection_exists(
        self,
        vector_size: int,
        distance: str = "Cosine"
    ) -> bool:
        """
        Ensures the collection exists with the correct configuration.
        Creates it if it doesn't exist, validates it if it does.
        """
        collection_name = self.config.collection_name

        if self.qdrant_client.collection_exists(collection_name):
            # Validate existing collection
            self.validate_collection_configuration(collection_name, vector_size, distance)
            print(f"Collection '{collection_name}' exists and is properly configured")
            return True
        else:
            # Create collection
            self.create_collection(collection_name, vector_size, distance)
            print(f"Collection '{collection_name}' created successfully")
            return True

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists in Qdrant.
        """
        return self.qdrant_client.collection_exists(collection_name)

    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "Cosine"
    ) -> bool:
        """
        Create a collection in Qdrant with specified parameters.
        """
        return self.qdrant_client.create_collection(
            collection_name=collection_name,
            vector_size=vector_size,
            distance=distance
        )

    def validate_collection_configuration(
        self,
        collection_name: str,
        expected_vector_size: int,
        expected_distance: str = "Cosine"
    ) -> bool:
        """
        Validate that an existing collection has the expected configuration.
        """
        return self.qdrant_client.validate_collection(
            collection_name=collection_name,
            expected_vector_size=expected_vector_size,
            expected_distance=expected_distance
        )

    def get_collection_info(self, collection_name: str) -> Optional[dict]:
        """
        Get detailed information about a collection.
        """
        try:
            collection_info = self.qdrant_client.get_client().get_collection(collection_name)
            return {
                "name": collection_info.config.params.vectors.size,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
                "point_count": collection_info.point_count,
                "indexed_vector_count": collection_info.indexed_vector_count
            }
        except Exception:
            return None