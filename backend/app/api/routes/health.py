"""
Health check endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import HealthResponse
from app.services import weaviate_client, mistral_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint that verifies all services are operational.
    """
    try:
        services_status = {}

        # Check Weaviate connection
        try:
            doc_count = await weaviate_client.get_document_count()
            services_status["weaviate"] = f"healthy (documents: {doc_count})"
        except Exception as e:
            logger.error(f"Weaviate health check failed: {e}")
            services_status["weaviate"] = "unhealthy"

        # Check Mistral service
        try:
            mistral_healthy = await mistral_service.health_check()
            services_status["mistral"] = "healthy" if mistral_healthy else "unhealthy"
        except Exception as e:
            logger.error(f"Mistral health check failed: {e}")
            services_status["mistral"] = "unhealthy"

        # Determine overall status
        overall_status = "healthy" if all(
            status.startswith("healthy") for status in services_status.values()
        ) else "degraded"

        return HealthResponse(
            status=overall_status,
            version=settings.version,
            services=services_status
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint for container orchestration.
    """
    try:
        # Quick check of essential services
        weaviate_ready = weaviate_client.client is not None and weaviate_client.client.is_ready()
        mistral_ready = mistral_service.client is not None

        if weaviate_ready and mistral_ready:
            return {"status": "ready"}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint for container orchestration.
    """
    return {"status": "alive"}
