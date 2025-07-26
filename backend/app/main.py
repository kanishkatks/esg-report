"""
FastAPI main application for RAG Chatbot.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services import weaviate_client, mistral_service
from app.api.routes import chat, documents, search, health

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting RAG Chatbot API...")

    # Initialize services
    weaviate_connected = await weaviate_client.connect()
    if not weaviate_connected:
        logger.error("Failed to connect to Weaviate")
        raise RuntimeError("Weaviate connection failed")

    mistral_initialized = await mistral_service.initialize()
    if not mistral_initialized:
        logger.error("Failed to initialize Mistral service")
        raise RuntimeError("Mistral initialization failed")

    logger.info("All services initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down RAG Chatbot API...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="A Retrieval-Augmented Generation (RAG) chatbot API using Mistral AI and Weaviate",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Chatbot API",
        "version": settings.version,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
