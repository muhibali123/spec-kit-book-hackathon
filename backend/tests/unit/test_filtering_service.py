import pytest
from src.services.filtering_service import FilteringService
from src.models.data_models import RetrievedDocument


class TestFilteringService:
    def test_filtering_service_initialization(self):
        """Test that FilteringService initializes correctly"""
        service = FilteringService()

        assert service is not None

    @pytest.mark.asyncio
    async def test_filter_by_score_threshold(self):
        """Test filtering documents by score threshold"""
        service = FilteringService()

        # Create test documents
        documents = [
            RetrievedDocument(id="doc1", payload={"text": "test1"}, score=0.9),
            RetrievedDocument(id="doc2", payload={"text": "test2"}, score=0.6),
            RetrievedDocument(id="doc3", payload={"text": "test3"}, score=0.4),
            RetrievedDocument(id="doc4", payload={"text": "test4"}, score=0.8)
        ]

        # Filter with threshold 0.7
        filtered = await service.filter_by_score_threshold(documents, 0.7)

        assert len(filtered) == 2  # Only doc1 (0.9) and doc4 (0.8) should pass
        scores = [doc.score for doc in filtered]
        assert 0.9 in scores
        assert 0.8 in scores
        assert 0.6 not in scores
        assert 0.4 not in scores

    @pytest.mark.asyncio
    async def test_filter_by_score_threshold_edge_cases(self):
        """Test filtering with edge case thresholds"""
        service = FilteringService()

        documents = [
            RetrievedDocument(id="doc1", payload={"text": "test1"}, score=0.5),
            RetrievedDocument(id="doc2", payload={"text": "test2"}, score=0.5),
            RetrievedDocument(id="doc3", payload={"text": "test3"}, score=0.49)
        ]

        # Test with exact threshold (should include equal values)
        filtered = await service.filter_by_score_threshold(documents, 0.5)
        assert len(filtered) == 2  # doc1 and doc2 have score=0.5, equal to threshold
        assert all(doc.score >= 0.5 for doc in filtered)

        # Test with high threshold (should return empty list)
        filtered = await service.filter_by_score_threshold(documents, 0.99)
        assert len(filtered) == 0

        # Test with low threshold (should return all documents)
        filtered = await service.filter_by_score_threshold(documents, 0.1)
        assert len(filtered) == 3

    @pytest.mark.asyncio
    async def test_filter_by_metadata(self):
        """Test filtering documents by metadata"""
        service = FilteringService()

        # Create test documents with various metadata
        documents = [
            RetrievedDocument(id="doc1", payload={"text": "test1", "source": "A", "category": "tech"}, score=0.9),
            RetrievedDocument(id="doc2", payload={"text": "test2", "source": "B", "category": "business"}, score=0.8),
            RetrievedDocument(id="doc3", payload={"text": "test3", "source": "A", "category": "tech"}, score=0.7),
            RetrievedDocument(id="doc4", payload={"text": "test4", "source": "C", "category": "science"}, score=0.6)
        ]

        # Filter by single metadata field
        filtered = await service.filter_by_metadata(documents, {"source": "A"})
        assert len(filtered) == 2  # doc1 and doc3 have source="A"
        assert all(doc.payload["source"] == "A" for doc in filtered)

        # Filter by another metadata field
        filtered = await service.filter_by_metadata(documents, {"category": "tech"})
        assert len(filtered) == 2  # doc1 and doc3 have category="tech"
        assert all(doc.payload["category"] == "tech" for doc in filtered)

    @pytest.mark.asyncio
    async def test_filter_by_multiple_metadata(self):
        """Test filtering documents by multiple metadata fields"""
        service = FilteringService()

        documents = [
            RetrievedDocument(id="doc1", payload={"text": "test1", "source": "A", "category": "tech", "year": 2023}, score=0.9),
            RetrievedDocument(id="doc2", payload={"text": "test2", "source": "A", "category": "business", "year": 2023}, score=0.8),
            RetrievedDocument(id="doc3", payload={"text": "test3", "source": "A", "category": "tech", "year": 2022}, score=0.7),
            RetrievedDocument(id="doc4", payload={"text": "test4", "source": "B", "category": "tech", "year": 2023}, score=0.6)
        ]

        # Filter by multiple fields
        filters = {"source": "A", "category": "tech", "year": 2023}
        filtered = await service.filter_by_metadata(documents, filters)
        assert len(filtered) == 1  # Only doc1 matches all criteria
        assert filtered[0].id == "doc1"

    @pytest.mark.asyncio
    async def test_filter_by_metadata_with_none(self):
        """Test filtering with None filters (should return all documents)"""
        service = FilteringService()

        documents = [
            RetrievedDocument(id="doc1", payload={"text": "test1"}, score=0.9),
            RetrievedDocument(id="doc2", payload={"text": "test2"}, score=0.8)
        ]

        # Filter with None (should return all)
        filtered = await service.filter_by_metadata(documents, None)
        assert len(filtered) == 2
        assert filtered[0].id == "doc1"
        assert filtered[1].id == "doc2"

        # Filter with empty dict (should return all)
        filtered = await service.filter_by_metadata(documents, {})
        assert len(filtered) == 2

    @pytest.mark.asyncio
    async def test_rank_documents(self):
        """Test ranking documents by score (highest first)"""
        service = FilteringService()

        documents = [
            RetrievedDocument(id="doc1", payload={"text": "test1"}, score=0.6),
            RetrievedDocument(id="doc2", payload={"text": "test2"}, score=0.9),
            RetrievedDocument(id="doc3", payload={"text": "test3"}, score=0.4),
            RetrievedDocument(id="doc4", payload={"text": "test4"}, score=0.8)
        ]

        ranked = await service.rank_documents(documents)

        assert len(ranked) == 4
        # Check that scores are in descending order
        scores = [doc.score for doc in ranked]
        assert scores == [0.9, 0.8, 0.6, 0.4]
        assert ranked[0].id == "doc2"  # highest score
        assert ranked[3].id == "doc3"  # lowest score

    @pytest.mark.asyncio
    async def test_rank_documents_empty_list(self):
        """Test ranking with empty list"""
        service = FilteringService()

        ranked = await service.rank_documents([])
        assert len(ranked) == 0

    @pytest.mark.asyncio
    async def test_rank_documents_single_document(self):
        """Test ranking with single document"""
        service = FilteringService()

        documents = [RetrievedDocument(id="doc1", payload={"text": "test1"}, score=0.7)]
        ranked = await service.rank_documents(documents)

        assert len(ranked) == 1
        assert ranked[0].id == "doc1"
        assert ranked[0].score == 0.7

    @pytest.mark.asyncio
    async def test_combined_filtering_and_ranking(self):
        """Test combining filtering and ranking operations"""
        service = FilteringService()

        documents = [
            RetrievedDocument(id="doc1", payload={"text": "test1", "source": "A"}, score=0.4),
            RetrievedDocument(id="doc2", payload={"text": "test2", "source": "B"}, score=0.9),
            RetrievedDocument(id="doc3", payload={"text": "test3", "source": "A"}, score=0.7),
            RetrievedDocument(id="doc4", payload={"text": "test4", "source": "A"}, score=0.6)
        ]

        # First filter by source, then by score threshold, then rank
        filtered_by_source = await service.filter_by_metadata(documents, {"source": "A"})
        assert len(filtered_by_source) == 3

        filtered_by_score = await service.filter_by_score_threshold(filtered_by_source, 0.5)
        assert len(filtered_by_score) == 2  # Only doc3 (0.7) and doc4 (0.6) have score >= 0.5

        ranked = await service.rank_documents(filtered_by_score)
        assert len(ranked) == 2
        # Should be ordered by score: doc3 (0.7) then doc4 (0.6)
        assert ranked[0].id == "doc3"  # highest score among filtered
        assert ranked[1].id == "doc4"  # lower score among filtered
        assert ranked[0].score > ranked[1].score