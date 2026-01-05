import pytest
from src.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_query_request():
    return {
        "query": "What are the benefits of renewable energy?",
        "top_k": 5,
        "score_threshold": 0.5,
        "filters": None,
        "include_metadata": True
    }


@pytest.fixture
def sample_document_chunk():
    return {
        "id": "doc_123_chunk_456",
        "text": "Renewable energy sources like solar and wind provide clean electricity without greenhouse gas emissions during operation.",
        "score": 0.89,
        "metadata": {
            "source": "renewable_energy_benefits.pdf",
            "page": 12,
            "section": "environmental_impact"
        },
        "source": "renewable_energy_benefits.pdf"
    }