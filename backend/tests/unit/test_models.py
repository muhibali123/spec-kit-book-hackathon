import pytest
from datetime import datetime
from src.models.request_models import QueryRequest
from src.models.response_models import AnswerResponse, Citation, HealthCheckResponse, ErrorResponse
from src.models.data_models import ContextChunk, RetrievedContext, GeneratedAnswer, ConversationTurn, ConversationContext


class TestQueryRequest:
    def test_query_request_valid(self):
        """Test that QueryRequest validates correctly with valid data"""
        data = {
            "query": "What are the benefits of renewable energy?",
            "top_k": 5,
            "score_threshold": 0.7,
            "filters": {"source_type": "research_paper"},
        }
        request = QueryRequest(**data)

        assert request.query == "What are the benefits of renewable energy?"
        assert request.top_k == 5
        assert request.score_threshold == 0.7
        assert request.filters == {"source_type": "research_paper"}

    def test_query_request_defaults(self):
        """Test QueryRequest with default values"""
        data = {"query": "Test query"}
        request = QueryRequest(**data)

        assert request.top_k == 5  # default
        assert request.score_threshold == 0.5  # default

    def test_query_request_query_validation(self):
        """Test QueryRequest query validation"""
        # Test empty query
        with pytest.raises(ValueError):
            QueryRequest(query="")

        # Test query too long
        with pytest.raises(ValueError):
            QueryRequest(query="a" * 1001)

    def test_query_request_top_k_validation(self):
        """Test QueryRequest top_k validation"""
        with pytest.raises(ValueError):
            QueryRequest(query="test", top_k=0)  # min is 1

        with pytest.raises(ValueError):
            QueryRequest(query="test", top_k=21)  # max is 20

    def test_query_request_score_threshold_validation(self):
        """Test QueryRequest score_threshold validation"""
        with pytest.raises(ValueError):
            QueryRequest(query="test", score_threshold=-0.1)  # min is 0.0

        with pytest.raises(ValueError):
            QueryRequest(query="test", score_threshold=1.1)  # max is 1.0


class TestCitation:
    def test_citation_valid(self):
        """Test that Citation validates correctly with valid data"""
        data = {
            "source_id": "doc_123",
            "source_title": "Research Paper Title",
            "excerpt": "Sample excerpt text from the document",
            "page_number": 5,
            "section_reference": "Section 2.3",
            "relevance_score": 0.85
        }
        citation = Citation(**data)

        assert citation.source_id == "doc_123"
        assert citation.source_title == "Research Paper Title"
        assert citation.excerpt == "Sample excerpt text from the document"
        assert citation.page_number == 5
        assert citation.section_reference == "Section 2.3"
        assert citation.relevance_score == 0.85

    def test_citation_optional_fields(self):
        """Test Citation with optional fields omitted"""
        data = {
            "source_id": "doc_123",
            "source_title": "Research Paper Title",
            "excerpt": "Sample excerpt text",
            "relevance_score": 0.85
        }
        citation = Citation(**data)

        assert citation.source_id == "doc_123"
        assert citation.source_title == "Research Paper Title"
        assert citation.excerpt == "Sample excerpt text"
        assert citation.page_number is None
        assert citation.section_reference is None
        assert citation.relevance_score == 0.85

    def test_citation_relevance_score_validation(self):
        """Test Citation relevance_score validation"""
        with pytest.raises(ValueError):
            Citation(
                source_id="doc_123",
                source_title="Test",
                excerpt="Test",
                relevance_score=-0.1  # min is 0.0
            )

        with pytest.raises(ValueError):
            Citation(
                source_id="doc_123",
                source_title="Test",
                excerpt="Test",
                relevance_score=1.1  # max is 1.0
            )


class TestAnswerResponse:
    def test_answer_response_valid(self):
        """Test that AnswerResponse validates correctly"""
        citation_data = {
            "source_id": "doc_123",
            "source_title": "Research Paper",
            "excerpt": "Sample excerpt",
            "relevance_score": 0.85
        }

        data = {
            "query": "Test query",
            "answer": "This is the generated answer",
            "citations": [Citation(**citation_data)],
            "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
            "confidence_score": 0.92,
            "processing_time": 0.5
        }

        response = AnswerResponse(**data)

        assert response.query == "Test query"
        assert response.answer == "This is the generated answer"
        assert len(response.citations) == 1
        assert response.conversation_id == "123e4567-e89b-12d3-a456-426614174000"
        assert response.confidence_score == 0.92
        assert response.processing_time == 0.5

    def test_answer_response_defaults(self):
        """Test AnswerResponse with optional fields omitted"""
        citation_data = {
            "source_id": "doc_123",
            "source_title": "Research Paper",
            "excerpt": "Sample excerpt",
            "relevance_score": 0.85
        }

        data = {
            "query": "Test query",
            "answer": "This is the generated answer",
            "citations": [Citation(**citation_data)],
            "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
            "processing_time": 0.5
        }

        response = AnswerResponse(**data)

        assert response.confidence_score is None


class TestHealthCheckResponse:
    def test_health_check_response_valid(self):
        """Test that HealthCheckResponse validates correctly"""
        data = {
            "status": "healthy",
            "timestamp": datetime.now(),
            "dependencies": {"openai_api": True, "retrieval_service": True}
        }

        response = HealthCheckResponse(**data)

        assert response.status == "healthy"
        assert response.dependencies == {"openai_api": True, "retrieval_service": True}


class TestErrorResponse:
    def test_error_response_valid(self):
        """Test that ErrorResponse validates correctly"""
        data = {
            "error": "Something went wrong",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.now()
        }

        response = ErrorResponse(**data)

        assert response.error == "Something went wrong"
        assert response.error_code == "INTERNAL_ERROR"


class TestContextChunk:
    def test_context_chunk_valid(self):
        """Test that ContextChunk validates correctly"""
        data = {
            "chunk_id": "chunk_123",
            "content": "Sample content from the document",
            "source_document": "document.pdf",
            "source_section": "Section 2.1",
            "metadata": {"page": 5, "chapter": "Introduction"},
            "relevance_score": 0.85
        }

        chunk = ContextChunk(**data)

        assert chunk.chunk_id == "chunk_123"
        assert chunk.content == "Sample content from the document"
        assert chunk.source_document == "document.pdf"
        assert chunk.source_section == "Section 2.1"
        assert chunk.metadata == {"page": 5, "chapter": "Introduction"}
        assert chunk.relevance_score == 0.85

    def test_context_chunk_optional_fields(self):
        """Test ContextChunk with optional fields omitted"""
        data = {
            "chunk_id": "chunk_123",
            "content": "Sample content",
            "source_document": "document.pdf",
            "relevance_score": 0.85
        }

        chunk = ContextChunk(**data)

        assert chunk.source_section is None
        assert chunk.metadata is None

    def test_context_chunk_content_length_validation(self):
        """Test ContextChunk content length validation"""
        with pytest.raises(ValueError):
            ContextChunk(
                chunk_id="chunk_123",
                content="a" * 10001,  # exceeds max length of 10000
                source_document="doc.pdf",
                relevance_score=0.8
            )

    def test_context_chunk_relevance_score_validation(self):
        """Test ContextChunk relevance_score validation"""
        with pytest.raises(ValueError):
            ContextChunk(
                chunk_id="chunk_123",
                content="test",
                source_document="doc.pdf",
                relevance_score=-0.1  # min is 0.0
            )

        with pytest.raises(ValueError):
            ContextChunk(
                chunk_id="chunk_123",
                content="test",
                source_document="doc.pdf",
                relevance_score=1.1  # max is 1.0
            )


class TestRetrievedContext:
    def test_retrieved_context_valid(self):
        """Test that RetrievedContext validates correctly"""
        chunk_data = {
            "chunk_id": "chunk_123",
            "content": "Sample content",
            "source_document": "doc.pdf",
            "relevance_score": 0.85
        }

        data = {
            "context_chunks": [ContextChunk(**chunk_data)],
            "relevance_scores": [0.85],
            "metadata": {"search_time": 0.2}
        }

        context = RetrievedContext(**data)

        assert len(context.context_chunks) == 1
        assert context.relevance_scores == [0.85]
        assert context.metadata == {"search_time": 0.2}


class TestGeneratedAnswer:
    def test_generated_answer_valid(self):
        """Test that GeneratedAnswer validates correctly"""
        data = {
            "answer_id": "answer_123",
            "answer_text": "This is the generated answer text",
            "confidence_score": 0.92,
            "citations": [{"source": "doc.pdf", "text": "relevant excerpt"}],
            "metadata": {"model": "gpt-4", "tokens_used": 150},
            "timestamp": datetime.now()
        }

        answer = GeneratedAnswer(**data)

        assert answer.answer_id == "answer_123"
        assert answer.answer_text == "This is the generated answer text"
        assert answer.confidence_score == 0.92
        assert answer.citations == [{"source": "doc.pdf", "text": "relevant excerpt"}]
        assert answer.metadata == {"model": "gpt-4", "tokens_used": 150}

    def test_generated_answer_optional_fields(self):
        """Test GeneratedAnswer with optional fields omitted"""
        data = {
            "answer_id": "answer_123",
            "answer_text": "This is the generated answer text",
            "citations": [],
            "timestamp": datetime.now()
        }

        answer = GeneratedAnswer(**data)

        assert answer.confidence_score is None
        assert answer.metadata is None

    def test_generated_answer_citations_max_items(self):
        """Test GeneratedAnswer citations max items validation"""
        data = {
            "answer_id": "answer_123",
            "answer_text": "Test answer",
            "citations": [{"source": f"doc_{i}", "text": f"excerpt {i}"} for i in range(21)],  # More than max 20
            "timestamp": datetime.now()
        }

        with pytest.raises(ValueError):
            GeneratedAnswer(**data)

    def test_generated_answer_confidence_score_validation(self):
        """Test GeneratedAnswer confidence_score validation"""
        with pytest.raises(ValueError):
            GeneratedAnswer(
                answer_id="answer_123",
                answer_text="Test answer",
                citations=[],
                confidence_score=-0.1,  # min is 0.0
                timestamp=datetime.now()
            )

        with pytest.raises(ValueError):
            GeneratedAnswer(
                answer_id="answer_123",
                answer_text="Test answer",
                citations=[],
                confidence_score=1.1,  # max is 1.0
                timestamp=datetime.now()
            )


class TestConversationTurn:
    def test_conversation_turn_valid(self):
        """Test that ConversationTurn validates correctly"""
        data = {
            "turn_id": "turn_123",
            "user_query": "What is the weather today?",
            "system_response": "The weather is sunny with a high of 75°F.",
            "timestamp": datetime.now(),
            "context_summary": "User asked about weather"
        }

        turn = ConversationTurn(**data)

        assert turn.turn_id == "turn_123"
        assert turn.user_query == "What is the weather today?"
        assert turn.system_response == "The weather is sunny with a high of 75°F."
        assert turn.context_summary == "User asked about weather"

    def test_conversation_turn_optional_fields(self):
        """Test ConversationTurn with optional fields omitted"""
        data = {
            "turn_id": "turn_123",
            "user_query": "Test query",
            "system_response": "Test response",
            "timestamp": datetime.now()
        }

        turn = ConversationTurn(**data)

        assert turn.context_summary is None


class TestConversationContext:
    def test_conversation_context_valid(self):
        """Test that ConversationContext validates correctly"""
        turn_data = {
            "turn_id": "turn_123",
            "user_query": "Test query",
            "system_response": "Test response",
            "timestamp": datetime.now()
        }

        data = {
            "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
            "turns": [ConversationTurn(**turn_data)],
            "metadata": {"user_preferences": {"tone": "formal"}},
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "is_active": True
        }

        context = ConversationContext(**data)

        assert context.conversation_id == "123e4567-e89b-12d3-a456-426614174000"
        assert len(context.turns) == 1
        assert context.metadata == {"user_preferences": {"tone": "formal"}}
        assert context.is_active is True

    def test_conversation_context_max_turns(self):
        """Test ConversationContext max turns validation"""
        turn_data = {
            "turn_id": "turn_123",
            "user_query": "Test query",
            "system_response": "Test response",
            "timestamp": datetime.now()
        }

        data = {
            "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
            "turns": [ConversationTurn(**turn_data) for _ in range(26)],  # More than max 25
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        }

        with pytest.raises(ValueError):
            ConversationContext(**data)