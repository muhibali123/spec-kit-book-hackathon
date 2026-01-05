"""
Command-line interface for the Qdrant ingestion module.
"""
import argparse
import sys
import os
from pathlib import Path

# Add the backend/src directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qdrant_ingestion.index import main_ingestion_workflow
from src.qdrant_ingestion.config.qdrant_config import load_qdrant_config


def main():
    """
    Main entry point for the command-line interface for Qdrant ingestion.
    """
    parser = argparse.ArgumentParser(
        description="Ingest embeddings into Qdrant vector database"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input JSON file containing embeddings"
    )

    parser.add_argument(
        "--config",
        help="Path to configuration file (optional)"
    )

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file does not exist: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"Starting Qdrant ingestion from {args.input}")

        # Load configuration
        config = load_qdrant_config()
        print(f"Target collection: {config.collection_name}")

        # Run the ingestion workflow
        result = main_ingestion_workflow(args.input, args.config)

        print(f"Ingestion completed successfully")
        print(f"Successful records: {result.get('successful_count', 0)}")
        print(f"Failed records: {result.get('failed_count', 0)}")

        # Print metrics if available
        if 'metrics' in result:
            metrics = result['metrics']
            print(f"Total duration: {metrics.get('total_duration_ms', 0):.2f}ms")
            print(f"Records per second: {metrics.get('records_per_second', 0):.2f}")
            print(f"Success rate: {metrics.get('success_rate', 0):.2f}%")

    except Exception as e:
        print(f"Error during Qdrant ingestion: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()