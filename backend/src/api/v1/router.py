from fastapi import APIRouter
from .endpoints.retrieval import router as retrieval_router
from .endpoints.answer_generation import router as answer_router

# Create API router
router = APIRouter()

# Include all API endpoints
router.include_router(retrieval_router)
router.include_router(answer_router)  # No prefix since answer generation is the main functionality