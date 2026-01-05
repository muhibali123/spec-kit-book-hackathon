"""
Custom exception classes for the retrieval service
"""


class CohereAPIError(Exception):
    """Exception raised when Cohere API calls fail"""
    pass


class QdrantAPIError(Exception):
    """Exception raised when Qdrant API calls fail"""
    pass


class ValidationError(Exception):
    """Exception raised for validation errors"""
    pass


class ServiceError(Exception):
    """General exception for service-level errors"""
    pass


class ExternalServiceError(Exception):
    """Exception raised when external services are unavailable"""
    pass


class ConfigurationError(Exception):
    """Exception raised when there are configuration issues"""
    pass


class ProcessingError(Exception):
    """Exception raised when there are processing errors"""
    pass