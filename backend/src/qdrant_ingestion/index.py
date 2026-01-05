"""
Main entry point for the Qdrant ingestion module.
"""
import argparse
import sys
import os
from typing import Dict, Any, List
import json
from .config.qdrant_config import load_qdrant_config
from .clients.qdrant_client import QdrantClientWrapper
from .managers.collection_manager import CollectionManager
from .managers.ingestion_manager import IngestionManager
from .validators.schema_validator import SchemaValidator


def validate_qdrant_connection(qdrant_client: QdrantClientWrapper) -> bool:
    """
    Add connection validation to Qdrant Cloud.
    """
    try:
        # Test the connection by trying to list collections
        qdrant_client.get_client().get_collections()
        print("Qdrant connection validated successfully")
        return True
    except Exception as e:
        print(f"Qdrant connection validation failed: {str(e)}")
        return False


def main_ingestion_workflow(file_path: str, config_path: str = None) -> Dict[str, Any]:
    """
    Create main ingestion workflow function with enhanced error handling and reporting.
    """
    from .utils.logger import get_logger
    from .utils.metrics import MetricsAggregator

    logger = get_logger("main_ingestion")
    logger.info(f"Starting ingestion workflow for file: {file_path}")

    # Load configuration
    config = load_qdrant_config()
    logger.info(f"Configuration loaded for collection: {config.collection_name}")

    # Initialize components
    qdrant_client = QdrantClientWrapper(config)

    # Add connection validation to Qdrant Cloud
    if not validate_qdrant_connection(qdrant_client):
        error_msg = "Cannot proceed without valid Qdrant connection"
        logger.error(error_msg)
        raise Exception(error_msg)

    collection_manager = CollectionManager(qdrant_client, config)
    validator = SchemaValidator()
    ingestion_manager = IngestionManager(qdrant_client, config, validator)

    try:
        # Integrate collection management with ingestion workflow
        # First, determine the vector dimension from the input file
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()

        if not validator.validate_empty_input(raw_data):
            error_msg = "Invalid input file"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Parse and validate records to get dimension
        records = validator.validate_input_schema(raw_data)

        if not records:
            logger.info("No records found in input file. Nothing to process.")
            return {
                "status": "success",
                "message": "No records to process",
                "processed_count": 0
            }

        # Validate dimension consistency
        validator.validate_dimension_consistency(records)

        # Validate payload integrity
        validator.validate_payload_integrity(records)

        # Ensure collection exists with correct configuration
        first_record_dimension = records[0].dimension
        collection_manager.ensure_collection_exists(
            vector_size=first_record_dimension,
            distance=config.vector_distance
        )

        # Start metrics tracking
        ingestion_manager.metrics_aggregator.start_ingestion()

        # Perform the ingestion
        result = ingestion_manager.ingest_from_file(file_path, config.collection_name)

        # Get final metrics
        final_metrics = ingestion_manager.get_ingestion_stats()

        # Close client when done
        qdrant_client.close()

        logger.info(f"Ingestion completed. Successful: {result['successful_count']}, Failed: {result['failed_count']}")

        # Combine results with metrics
        result["metrics"] = final_metrics
        result["status"] = "completed"

        return result

    except Exception as e:
        logger.error(f"Error during ingestion workflow: {str(e)}")
        # Close client in case of error
        qdrant_client.close()
        raise


def main():
    """
    Main function to run the Qdrant ingestion process with command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Qdrant Vector Database Ingestion")
    parser.add_argument("--input", required=True, help="Path to the input JSON file containing embeddings")
    parser.add_argument("--config", help="Path to configuration file (optional)")

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file does not exist: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        result = main_ingestion_workflow(args.input, args.config)
        print(f"Ingestion workflow completed successfully: {result}")
    except Exception as e:
        print(f"Error during ingestion: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()