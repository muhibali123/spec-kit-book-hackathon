import pytest
import logging
from unittest.mock import patch, MagicMock
from src.utils.logging import (
    setup_logging,
    get_logger,
    log_api_call,
    log_retrieval_request,
    log_error
)


class TestLogging:
    """Unit tests for logging utilities"""

    def test_setup_logging_basic(self):
        """Test basic logging setup"""
        logger = setup_logging()
        assert logger is not None
        assert logger.name == "retrieval_service"
        assert logger.level == logging.INFO

    def test_setup_logging_with_debug_level(self):
        """Test logging setup with DEBUG level"""
        import logging
        # Clear the logger's handlers to reset it for this test
        test_logger = logging.getLogger("retrieval_service")
        test_logger.handlers.clear()

        # Now test our logging setup function
        result_logger = setup_logging(log_level="DEBUG")
        assert result_logger.level == logging.DEBUG

    def test_setup_logging_with_json_format(self):
        """Test logging setup with JSON format"""
        logger = setup_logging(json_format=True)
        assert logger is not None

    def test_setup_logging_with_standard_format(self):
        """Test logging setup with standard format"""
        logger = setup_logging(json_format=False)
        assert logger is not None

    def test_get_logger(self):
        """Test getting a logger instance"""
        logger = get_logger()
        assert logger is not None
        assert logger.name == "retrieval_service"

        custom_logger = get_logger("custom")
        assert custom_logger.name == "custom"

    def test_log_api_call(self, caplog):
        """Test logging of API calls"""
        logger = get_logger("test_api_call")

        with caplog.at_level(logging.INFO):
            log_api_call(
                logger,
                endpoint="/v1/retrieve",
                method="POST",
                duration=0.123,
                status_code=200,
                user_id="test_user"
            )

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "API call completed" in record.message
        assert record.levelno == logging.INFO

    def test_log_api_call_with_metadata(self, caplog):
        """Test logging of API calls with additional metadata"""
        logger = get_logger("test_api_call_meta")

        with caplog.at_level(logging.INFO):
            log_api_call(
                logger,
                endpoint="/v1/retrieve",
                method="POST",
                duration=0.456,
                status_code=200,
                metadata={"query_length": 50, "top_k": 5}
            )

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "API call completed" in record.message

    def test_log_retrieval_request(self, caplog):
        """Test logging of retrieval requests"""
        logger = get_logger("test_retrieval")

        with caplog.at_level(logging.INFO):
            log_retrieval_request(
                logger,
                query="test query",
                top_k=5,
                score_threshold=0.5,
                duration=0.789,
                results_count=3
            )

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "Document retrieval completed" in record.message
        assert record.levelno == logging.INFO

    def test_log_retrieval_request_with_metadata(self, caplog):
        """Test logging of retrieval requests with additional metadata"""
        logger = get_logger("test_retrieval_meta")

        with caplog.at_level(logging.INFO):
            log_retrieval_request(
                logger,
                query="another test query",
                top_k=10,
                score_threshold=0.7,
                duration=1.234,
                results_count=7,
                metadata={"filters_applied": True, "original_search_results": 20}
            )

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "Document retrieval completed" in record.message

    def test_log_error(self, caplog):
        """Test logging of errors"""
        logger = get_logger("test_error")

        with caplog.at_level(logging.ERROR):
            log_error(
                logger,
                error_type="ValidationError",
                error_message="Invalid query parameter",
                endpoint="/v1/retrieve"
            )

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "Error occurred" in record.message
        assert record.levelno == logging.ERROR

    def test_log_error_with_metadata(self, caplog):
        """Test logging of errors with additional metadata"""
        logger = get_logger("test_error_meta")

        with caplog.at_level(logging.ERROR):
            log_error(
                logger,
                error_type="CohereAPIError",
                error_message="API key invalid",
                metadata={"retry_count": 3, "api_endpoint": "embed"}
            )

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "Error occurred" in record.message

    def test_log_api_call_without_optional_params(self, caplog):
        """Test logging of API calls without optional parameters"""
        logger = get_logger("test_api_call_minimal")

        with caplog.at_level(logging.INFO):
            log_api_call(
                logger,
                endpoint="/v1/health",
                method="GET",
                duration=0.012,
                status_code=200
            )

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "API call completed" in record.message

    def test_logger_reuse_prevention(self):
        """Test that setup_logging doesn't add duplicate handlers"""
        # First call
        logger1 = setup_logging()
        initial_handler_count = len(logger1.handlers)

        # Second call should not add more handlers
        logger2 = setup_logging()

        assert len(logger2.handlers) == initial_handler_count
        assert logger1.handlers == logger2.handlers