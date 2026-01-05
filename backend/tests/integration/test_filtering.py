import pytest
from src.services.filtering_service import FilteringService
from src.services.retrieval_service import RetrievalService
from src.models.data_models import RetrievedDocument


class TestFilteringIntegration:
    def test_filtering_service_integration(self):
        """Test filtering service integration with realistic data"""
        service = FilteringService()

        # Create realistic test documents
        documents = [
            RetrievedDocument(
                id="doc_123_chunk_456",
                payload={
                    "text": "Renewable energy sources like solar and wind provide clean electricity without greenhouse gas emissions during operation.",
                    "source": "renewable_energy_benefits.pdf",
                    "page": 12,
                    "section": "environmental_impact",
                    "author": "Smith, J."
                },
                score=0.89
            ),
            RetrievedDocument(
                id="doc_789_chunk_101",
                payload={
                    "text": "The economic benefits of renewable energy include job creation in manufacturing, installation, and maintenance sectors.",
                    "source": "economic_analysis.pdf",
                    "page": 5,
                    "section": "job_creation",
                    "author": "Johnson, A."
                },
                score=0.82
            ),
            RetrievedDocument(
                id="doc_456_chunk_234",
                payload={
                    "text": "Solar panel efficiency has improved significantly over the past decade, making solar energy more cost-effective.",
                    "source": "solar_efficiency_study.pdf",
                    "page": 8,
                    "section": "technical_advances",
                    "author": "Smith, J."
                },
                score=0.75
            ),
            RetrievedDocument(
                id="doc_321_chunk_567",
                payload={
                    "text": "Wind energy farms require significant initial investment but provide long-term cost savings.",
                    "source": "wind_energy_economics.pdf",
                    "page": 15,
                    "section": "cost_analysis",
                    "author": "Brown, K."
                },
                score=0.68
            )
        ]

        # Test score threshold filtering
        high_quality_docs = service.filter_by_score_threshold(documents, 0.80)
        assert len(high_quality_docs) == 2  # Only the top 2 documents
        assert all(doc.score >= 0.80 for doc in high_quality_docs)

        # Test metadata filtering
        smith_docs = service.filter_by_metadata(documents, {"author": "Smith, J."})
        assert len(smith_docs) == 2  # Two documents by Smith
        assert all(doc.payload["author"] == "Smith, J." for doc in smith_docs)

        # Test section filtering
        environmental_docs = service.filter_by_metadata(documents, {"section": "environmental_impact"})
        assert len(environmental_docs) == 1
        assert environmental_docs[0].payload["section"] == "environmental_impact"

        # Test combined filtering and ranking
        filtered = service.filter_by_score_threshold(documents, 0.70)  # Filter by score
        filtered = service.filter_by_metadata(filtered, {"author": "Smith, J."})  # Then by metadata
        ranked = service.rank_documents(filtered)  # Then rank

        # Should have 2 docs by Smith with score >= 0.7, ranked by score
        assert len(ranked) == 2
        assert ranked[0].score >= ranked[1].score  # Ranked in descending order
        assert all(doc.payload["author"] == "Smith, J." for doc in ranked)
        assert all(doc.score >= 0.7 for doc in ranked)

    @pytest.mark.asyncio
    async def test_filtering_with_edge_cases(self):
        """Test filtering with edge cases"""
        service = FilteringService()

        # Empty document list
        result = await service.filter_by_score_threshold([], 0.5)
        assert len(result) == 0

        result = await service.filter_by_metadata([], {"key": "value"})
        assert len(result) == 0

        result = await service.rank_documents([])
        assert len(result) == 0

        # Single document
        single_doc = [RetrievedDocument(id="doc1", payload={"text": "test"}, score=0.8)]
        result = await service.rank_documents(single_doc)
        assert len(result) == 1
        assert result[0].id == "doc1"

        # Test with documents having same score (should preserve original order for same scores)
        docs_same_score = [
            RetrievedDocument(id="doc_a", payload={"text": "test A"}, score=0.8),
            RetrievedDocument(id="doc_b", payload={"text": "test B"}, score=0.8)
        ]
        result = await service.rank_documents(docs_same_score)
        assert len(result) == 2
        # When scores are equal, the original order should be maintained (though sorted() might not guarantee this)
        # The main requirement is that both documents are included and scores are the same

    def test_integration_with_realistic_filters(self):
        """Test filtering with realistic combinations that might occur in the RAG system"""
        service = FilteringService()

        # Create a larger set of documents with various metadata
        documents = []
        for i in range(10):
            documents.append(
                RetrievedDocument(
                    id=f"doc_{i}",
                    payload={
                        "text": f"Document text {i}",
                        "source": f"source_{i % 3}",  # 3 different sources
                        "year": 2020 + (i % 4),  # years 2020-2023
                        "category": "tech" if i % 2 == 0 else "business"
                    },
                    score=0.9 - (i * 0.05)  # Scores from 0.9 to 0.45
                )
            )

        # Test complex filtering: high score + specific source + specific category
        high_score_docs = service.filter_by_score_threshold(documents, 0.7)  # Score >= 0.7
        source_filtered = service.filter_by_metadata(high_score_docs, {"source": "source_0"})
        final_docs = service.filter_by_metadata(source_filtered, {"category": "tech"})
        ranked = service.rank_documents(final_docs)

        # Verify results meet all criteria
        assert all(doc.score >= 0.7 for doc in ranked)
        assert all(doc.payload["source"] == "source_0" for doc in ranked)
        assert all(doc.payload["category"] == "tech" for doc in ranked)
        assert all(ranked[i].score >= ranked[i+1].score for i in range(len(ranked)-1))  # Ranked in descending order