"""
CLI interface for the retrieval service
Provides command-line tools for interacting with the service
"""
import asyncio
import json
import argparse
import sys
from typing import Dict, Any
from pathlib import Path

from src.services.retrieval_service import RetrievalService
from src.services.filtering_service import FilteringService
from src.clients.cohere_client import CohereClient
from src.clients.qdrant_client import QdrantClient
from src.config.settings import settings
from src.utils.logging import setup_logging


def create_retrieval_service() -> RetrievalService:
    """Create a retrieval service instance with configured clients"""
    cohere_client = CohereClient(
        api_key=settings.cohere_api_key,
        model=settings.cohere_model
    )
    qdrant_client = QdrantClient(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        collection_name=settings.qdrant_collection
    )
    filtering_service = FilteringService()

    return RetrievalService(
        cohere_client=cohere_client,
        qdrant_client=qdrant_client,
        filtering_service=filtering_service
    )


async def query_documents(args):
    """Handle the query command"""
    setup_logging(log_level=args.log_level, json_format=False)

    service = create_retrieval_service()

    try:
        results = await service.retrieve_documents(
            query=args.query,
            top_k=args.top_k,
            score_threshold=args.score_threshold,
            filters=args.filters
        )

        if args.output_format == "json":
            output = {
                "query": args.query,
                "results": [
                    {
                        "id": result.id,
                        "score": result.score,
                        "payload": result.payload
                    } for result in results
                ],
                "total_results": len(results)
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"Query: {args.query}")
            print(f"Found {len(results)} results:")
            print("-" * 50)
            for i, result in enumerate(results, 1):
                print(f"{i}. ID: {result.id}")
                print(f"   Score: {result.score}")
                print(f"   Text: {result.payload.get('text', '')[:100]}...")
                print()

    except Exception as e:
        print(f"Error retrieving documents: {str(e)}", file=sys.stderr)
        return 1

    return 0


def health_check(args):
    """Handle the health check command"""
    setup_logging(log_level=args.log_level, json_format=False)

    print("Health check not implemented in CLI yet - this would check service dependencies")
    # In a real implementation, we would check if Cohere and Qdrant are accessible
    return 0


def quickstart(args):
    """Handle the quickstart command - demonstrates basic usage"""
    setup_logging(log_level=args.log_level, json_format=False)

    print("Quickstart - Retrieval & Context Filtering Service")
    print("=" * 50)
    print("This service provides document retrieval and context filtering capabilities.")
    print()
    print("Example usage:")
    print("  python -m src.cli query --query 'What are renewable energy sources?' --top-k 3")
    print()
    print("Configuration:")
    print(f"  Cohere model: {settings.cohere_model}")
    print(f"  Qdrant host: {settings.qdrant_host}:{settings.qdrant_port}")
    print(f"  Collection: {settings.qdrant_collection}")
    print()
    print("For more information, use --help with any command.")


def setup_parser():
    """Set up the argument parser"""
    parser = argparse.ArgumentParser(
        description="CLI for Retrieval & Context Filtering Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query for documents
  python -m src.cli query --query "What are renewable energy sources?" --top-k 5

  # Query with filters
  python -m src.cli query --query "machine learning" --filters '{"author": "Smith"}'

  # Check service health
  python -m src.cli health

  # Show quickstart guide
  python -m src.cli quickstart
        """
    )

    # Set up subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query for relevant documents")
    query_parser.add_argument("query", help="The query string to search for")
    query_parser.add_argument("--top-k", type=int, default=5, help="Number of top results to return (default: 5)")
    query_parser.add_argument("--score-threshold", type=float, default=0.5, help="Minimum relevance score threshold (default: 0.5)")
    query_parser.add_argument("--filters", type=json.loads, default=None, help="JSON filters for metadata (e.g., '{\"author\": \"Smith\"}')")
    query_parser.add_argument("--output-format", choices=["text", "json"], default="text", help="Output format (default: text)")
    query_parser.add_argument("--log-level", default="INFO", help="Logging level (default: INFO)")

    # Health command
    health_parser = subparsers.add_parser("health", help="Check service health")
    health_parser.add_argument("--log-level", default="INFO", help="Logging level (default: INFO)")

    # Quickstart command
    quickstart_parser = subparsers.add_parser("quickstart", help="Show quickstart guide")
    quickstart_parser.add_argument("--log-level", default="INFO", help="Logging level (default: INFO)")

    return parser


def main():
    """Main CLI entry point"""
    import sys

    parser = setup_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Set up logging
    setup_logging(log_level=getattr(args, 'log_level', 'INFO'), json_format=False)

    if args.command == "query":
        return asyncio.run(query_documents(args))
    elif args.command == "health":
        return health_check(args)
    elif args.command == "quickstart":
        return quickstart(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())