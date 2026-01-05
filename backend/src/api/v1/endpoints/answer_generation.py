from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import time
import uuid

from src.models.request_models import QueryRequest
from src.models.response_models import AnswerResponse, QueryResponse, DocumentChunk, HealthCheckResponse
from src.services.agent_service import AgentService
from src.api.dependencies import get_agent_service
from src.utils.logging import get_logger, log_api_call
from src.utils.metrics import increment_api_call_counter

router = APIRouter()


@router.post("/answer", response_model=AnswerResponse)
async def generate_answer(
    request: QueryRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Generate a grounded answer based on the user's query and retrieved context
    Uses the RAG agent to process the query, retrieve relevant context, and generate an answer
    """
    logger = get_logger("api.answer")
    start_time = time.time()

    logger.info(f"Received answer generation request for query of length {len(request.query)}", extra={
        "event": "api_request_start",
        "endpoint": "/v1/answer",
        "method": "POST",
        "query_length": len(request.query),
        "top_k": request.top_k,
        "score_threshold": request.score_threshold
    })

    try:
        # Call the agent service to process the query
        answer_response = await agent_service.process_query(request)

        processing_time = time.time() - start_time

        logger.info(f"Answer generation request completed successfully", extra={
            "event": "api_request_success",
            "answer_length": len(answer_response.answer),
            "citations_count": len(answer_response.citations),
            "processing_time": processing_time
        })

        # Record metrics
        increment_api_call_counter("/v1/answer", "POST", 200)

        # Log the API call using the utility function
        log_api_call(
            logger,
            "/v1/answer",
            "POST",
            processing_time,
            200
        )

        return answer_response

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Answer generation request failed: {str(e)}", extra={
            "event": "api_request_error",
            "error_type": type(e).__name__,
            "processing_time": processing_time
        })

        # Record metrics for failed request
        increment_api_call_counter("/v1/answer", "POST", 500)

        # Log the API call failure using the utility function
        log_api_call(
            logger,
            "/v1/answer",
            "POST",
            processing_time,
            500
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating answer: {str(e)}"
        )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint for the answer generation service
    """
    logger = get_logger("api.health")

    logger.info("Health check requested", extra={
        "event": "health_check_start",
        "endpoint": "/v1/health",
        "method": "GET"
    })

    start_time = time.time()
    dependencies_status = {
        "llm_provider": True,  # Placeholder - would check actual LLM connectivity
        "retrieval_service": True  # Placeholder - would check retrieval service connectivity
    }

    # In a real implementation, we would check the actual health of dependencies
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