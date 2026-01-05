from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import time

from src.models.request_models import QueryRequest
from src.models.response_models import (
    QueryResponse,
    DocumentChunk,
    HealthCheckResponse
)
from src.services.retrieval_service import RetrievalService
from src.api.dependencies import get_retrieval_service, get_cohere_client, get_qdrant_client
from src.utils.logging import get_logger, log_api_call
from src.utils.metrics import increment_api_call_counter, increment_retrieval_counter, record_retrieval_duration

router = APIRouter()


@router.post("/retrieve", response_model=QueryResponse)
async def retrieve_documents(
    request: QueryRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
):
    """
    Retrieve relevant document chunks for a query
    Processes a user query, generates embeddings, performs similarity search, and returns filtered results
    """
    logger = get_logger("api.retrieve")
    start_time = time.time()

    logger.info(f"Received retrieval request for query of length {len(request.query)}", extra={
        "event": "api_request_start",
        "endpoint": "/v1/retrieve",
        "method": "POST",
        "query_length": len(request.query),
        "top_k": request.top_k,
        "score_threshold": request.score_threshold
    })

    try:
        # Call the retrieval service to get results
        results = await retrieval_service.retrieve_documents(
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            filters=request.filters
        )

        processing_time = time.time() - start_time

        # Convert service results to API response format
        document_chunks = []
        for result in results:
            # result should be a RetrievedDocument object based on our service implementation
            chunk = DocumentChunk(
                id=result.id,
                text=result.payload.get('text', '') if isinstance(result.payload, dict) else str(result.payload),
                score=result.score,
                metadata=result.payload if isinstance(result.payload, dict) else {},
                source=result.payload.get('source', '') if isinstance(result.payload, dict) else ''
            )
            document_chunks.append(chunk)

        response = QueryResponse(
            query=request.query,
            results=document_chunks,
            total_results=len(document_chunks),
            processing_time=processing_time
        )

        logger.info(f"Retrieval request completed successfully with {len(document_chunks)} results", extra={
            "event": "api_request_success",
            "results_count": len(document_chunks),
            "processing_time": processing_time
        })

        # Record metrics
        increment_api_call_counter("/v1/retrieve", "POST", 200)
        increment_retrieval_counter(success=True)
        record_retrieval_duration(processing_time)

        # Log the API call using the utility function
        log_api_call(
            logger,
            "/v1/retrieve",
            "POST",
            processing_time,
            200
        )

        return response
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Retrieval request failed: {str(e)}", extra={
            "event": "api_request_error",
            "error_type": type(e).__name__,
            "processing_time": processing_time
        })

        # Record metrics for failed request
        increment_api_call_counter("/v1/retrieve", "POST", 500)
        increment_retrieval_counter(success=False)

        # Log the API call failure using the utility function
        log_api_call(
            logger,
            "/v1/retrieve",
            "POST",
            processing_time,
            500
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving documents: {str(e)}"
        )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    cohere_client = Depends(get_cohere_client),
    qdrant_client = Depends(get_qdrant_client)
):
    """
    Health check endpoint that verifies the service and its dependencies
    """
    logger = get_logger("api.health")

    logger.info("Health check requested", extra={
        "event": "health_check_start",
        "endpoint": "/v1/health",
        "method": "GET"
    })

    start_time = time.time()
    dependencies_status = {
        "cohere_api": False,
        "qdrant_db": False
    }

    # Check Cohere API connectivity
    try:
        # Make a lightweight API call to test Cohere connectivity
        await cohere_client.generate_embeddings(["health check"])
        dependencies_status["cohere_api"] = True
        logger.debug("Cohere API health check passed", extra={
            "event": "dependency_health",
            "dependency": "cohere_api",
            "status": "healthy"
        })
    except Exception as e:
        logger.warning(f"Cohere API health check failed: {str(e)}", extra={
            "event": "dependency_health",
            "dependency": "cohere_api",
            "status": "unhealthy",
            "error": str(e)
        })
        dependencies_status["cohere_api"] = False

    # Check Qdrant connectivity
    try:
        # Attempt to connect to Qdrant and verify collection exists
        # For now, we'll try to get collection info to test connectivity
        collection_info = await qdrant_client.client.get_collection(qdrant_client.collection_name)
        dependencies_status["qdrant_db"] = True
        logger.debug("Qdrant DB health check passed", extra={
            "event": "dependency_health",
            "dependency": "qdrant_db",
            "status": "healthy",
            "collection": qdrant_client.collection_name
        })
    except Exception as e:
        logger.warning(f"Qdrant DB health check failed: {str(e)}", extra={
            "event": "dependency_health",
            "dependency": "qdrant_db",
            "status": "unhealthy",
            "error": str(e)
        })
        dependencies_status["qdrant_db"] = False

    # Determine overall status
    overall_status = "healthy" if all(dependencies_status.values()) else "unhealthy"
    processing_time = time.time() - start_time

    logger.info(f"Health check completed with status: {overall_status}", extra={
        "event": "health_check_complete",
        "overall_status": overall_status,
        "processing_time": processing_time
    })

    # Record metrics
    increment_api_call_counter("/v1/health", "GET", 200)

    # Log the API call using the utility function
    log_api_call(
        logger,
        "/v1/health",
        "GET",
        processing_time,
        200
    )

    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.now(),
        dependencies=dependencies_status
    )