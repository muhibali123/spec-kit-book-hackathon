from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.utils.exceptions import (
    CohereAPIError,
    QdrantAPIError,
    ValidationError,
    ServiceError,
    ExternalServiceError,
    ConfigurationError,
    ProcessingError
)
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


async def cohere_api_error_handler(request: Request, exc: CohereAPIError):
    """Handle Cohere API errors"""
    logger.error(f"Cohere API Error: {str(exc)}", extra={"url": str(request.url)})
    return JSONResponse(
        status_code=502,
        content={
            "error": "Cohere API Error",
            "error_code": "COHERE_API_ERROR",
            "timestamp": datetime.now().isoformat(),
            "details": str(exc)
        }
    )


async def qdrant_api_error_handler(request: Request, exc: QdrantAPIError):
    """Handle Qdrant API errors"""
    logger.error(f"Qdrant API Error: {str(exc)}", extra={"url": str(request.url)})
    return JSONResponse(
        status_code=502,
        content={
            "error": "Qdrant API Error",
            "error_code": "QDRANT_API_ERROR",
            "timestamp": datetime.now().isoformat(),
            "details": str(exc)
        }
    )


async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation Error: {str(exc)}", extra={"url": str(request.url)})
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "error_code": "VALIDATION_ERROR",
            "timestamp": datetime.now().isoformat(),
            "details": str(exc)
        }
    )


async def service_error_handler(request: Request, exc: ServiceError):
    """Handle general service errors"""
    logger.error(f"Service Error: {str(exc)}", extra={"url": str(request.url)})
    return JSONResponse(
        status_code=500,
        content={
            "error": "Service Error",
            "error_code": "SERVICE_ERROR",
            "timestamp": datetime.now().isoformat(),
            "details": str(exc)
        }
    )


async def external_service_error_handler(request: Request, exc: ExternalServiceError):
    """Handle external service errors"""
    logger.error(f"External Service Error: {str(exc)}", extra={"url": str(request.url)})
    return JSONResponse(
        status_code=503,
        content={
            "error": "External Service Unavailable",
            "error_code": "EXTERNAL_SERVICE_ERROR",
            "timestamp": datetime.now().isoformat(),
            "details": str(exc)
        }
    )


async def configuration_error_handler(request: Request, exc: ConfigurationError):
    """Handle configuration errors"""
    logger.error(f"Configuration Error: {str(exc)}", extra={"url": str(request.url)})
    return JSONResponse(
        status_code=500,
        content={
            "error": "Configuration Error",
            "error_code": "CONFIGURATION_ERROR",
            "timestamp": datetime.now().isoformat(),
            "details": str(exc)
        }
    )


async def processing_error_handler(request: Request, exc: ProcessingError):
    """Handle processing errors"""
    logger.error(f"Processing Error: {str(exc)}", extra={"url": str(request.url)})
    return JSONResponse(
        status_code=500,
        content={
            "error": "Processing Error",
            "error_code": "PROCESSING_ERROR",
            "timestamp": datetime.now().isoformat(),
            "details": str(exc)
        }
    )


async def http_error_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP errors"""
    logger.warning(f"HTTP Error {exc.status_code}: {exc.detail}", extra={"url": str(request.url)})
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP {exc.status_code}",
            "error_code": f"HTTP_{exc.status_code}",
            "timestamp": datetime.now().isoformat(),
            "details": exc.detail
        }
    )


async def validation_error_handler_fastapi(request: Request, exc: RequestValidationError):
    """Handle FastAPI request validation errors"""
    logger.warning(f"Request Validation Error: {exc.errors()}", extra={"url": str(request.url)})
    return JSONResponse(
        status_code=422,
        content={
            "error": "Request Validation Error",
            "error_code": "REQUEST_VALIDATION_ERROR",
            "timestamp": datetime.now().isoformat(),
            "details": exc.errors()
        }
    )


async def general_error_handler(request: Request, exc: Exception):
    """Handle general unexpected errors"""
    logger.error(f"Unexpected Error: {str(exc)}", extra={"url": str(request.url), "exception_type": type(exc).__name__})
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.now().isoformat(),
            "details": "An unexpected error occurred"
        }
    )