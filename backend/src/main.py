from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.api.v1.router import router as v1_router
from src.config.settings import settings
from src.utils.logging import setup_logging

# Set up logging
setup_logging(log_level=settings.log_level, json_format=settings.log_json_format)

# Create FastAPI app
app = FastAPI(
    title="RAG Agent & Answer Generation Service",
    description="Service that generates grounded, context-aware answers using OpenAI Agent SDK and retrieved context",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, configure this properly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(v1_router, prefix="/v1")

@app.get("/")
async def root():
    return {"message": "RAG Agent & Answer Generation Service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )