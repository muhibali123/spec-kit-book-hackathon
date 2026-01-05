import pytest
from src.utils.exceptions import (
    CohereAPIError,
    QdrantAPIError,
    ValidationError,
    ServiceError,
    ExternalServiceError,
    ConfigurationError,
    ProcessingError
)


class TestExceptions:
    """Unit tests for custom exception classes"""

    def test_cohere_api_error(self):
        """Test CohereAPIError can be raised and caught"""
        with pytest.raises(CohereAPIError):
            raise CohereAPIError("Test Cohere API error")

        # Test with message
        try:
            raise CohereAPIError("Test error message")
        except CohereAPIError as e:
            assert str(e) == "Test error message"

    def test_qdrant_api_error(self):
        """Test QdrantAPIError can be raised and caught"""
        with pytest.raises(QdrantAPIError):
            raise QdrantAPIError("Test Qdrant API error")

        # Test with message
        try:
            raise QdrantAPIError("Test error message")
        except QdrantAPIError as e:
            assert str(e) == "Test error message"

    def test_validation_error(self):
        """Test ValidationError can be raised and caught"""
        with pytest.raises(ValidationError):
            raise ValidationError("Test validation error")

        # Test with message
        try:
            raise ValidationError("Test validation message")
        except ValidationError as e:
            assert str(e) == "Test validation message"

    def test_service_error(self):
        """Test ServiceError can be raised and caught"""
        with pytest.raises(ServiceError):
            raise ServiceError("Test service error")

        # Test with message
        try:
            raise ServiceError("Test service message")
        except ServiceError as e:
            assert str(e) == "Test service message"

    def test_external_service_error(self):
        """Test ExternalServiceError can be raised and caught"""
        with pytest.raises(ExternalServiceError):
            raise ExternalServiceError("Test external service error")

        # Test with message
        try:
            raise ExternalServiceError("Test external service message")
        except ExternalServiceError as e:
            assert str(e) == "Test external service message"

    def test_configuration_error(self):
        """Test ConfigurationError can be raised and caught"""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Test configuration error")

        # Test with message
        try:
            raise ConfigurationError("Test configuration message")
        except ConfigurationError as e:
            assert str(e) == "Test configuration message"

    def test_processing_error(self):
        """Test ProcessingError can be raised and caught"""
        with pytest.raises(ProcessingError):
            raise ProcessingError("Test processing error")

        # Test with message
        try:
            raise ProcessingError("Test processing message")
        except ProcessingError as e:
            assert str(e) == "Test processing message"

    def test_exception_inheritance(self):
        """Test that custom exceptions inherit from base Exception class"""
        assert issubclass(CohereAPIError, Exception)
        assert issubclass(QdrantAPIError, Exception)
        assert issubclass(ValidationError, Exception)
        assert issubclass(ServiceError, Exception)
        assert issubclass(ExternalServiceError, Exception)
        assert issubclass(ConfigurationError, Exception)
        assert issubclass(ProcessingError, Exception)