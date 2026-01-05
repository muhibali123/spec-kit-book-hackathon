# Retrieval & Context Filtering Service - CLI

Command-line interface for the Retrieval & Context Filtering Service.

## Usage

### Query for Documents

```bash
# Basic query
python -m src.cli query "What are renewable energy sources?"

# Query with specific parameters
python -m src.cli query "machine learning" --top-k 10 --score-threshold 0.7

# Query with metadata filters (JSON format)
python -m src.cli query "climate change" --filters '{"author": "Smith", "year": 2023}'

# Output in JSON format
python -m src.cli query "renewable energy" --output-format json
```

### Check Service Health

```bash
python -m src.cli health
```

### Quickstart Guide

```bash
python -m src.cli quickstart
```

## Configuration

The CLI uses the same configuration as the web service, reading from environment variables or a `.env` file:

- `COHERE_API_KEY`: Your Cohere API key
- `QDRANT_HOST`: Qdrant host (default: localhost)
- `QDRANT_PORT`: Qdrant port (default: 6333)
- `QDRANT_COLLECTION`: Qdrant collection name (default: documents)

## Commands

### `query`
Query the retrieval service for relevant documents.

**Options:**
- `--top-k`: Number of top results to return (default: 5)
- `--score-threshold`: Minimum relevance score threshold (default: 0.5)
- `--filters`: JSON filters for metadata (e.g., `'{"author": "Smith"}'`)
- `--output-format`: Output format (text or json, default: text)
- `--log-level`: Logging level (default: INFO)

### `health`
Check the health of service dependencies.

### `quickstart`
Show a quickstart guide with usage examples.

## Examples

```bash
# Find top 3 documents about renewable energy with high relevance
python -m src.cli query "solar and wind power benefits" --top-k 3 --score-threshold 0.8

# Search with author filter
python -m src.cli query "machine learning algorithms" --filters '{"author": "Johnson"}'

# Get structured JSON output for programmatic use
python -m src.cli query "climate science" --top-k 5 --output-format json
```