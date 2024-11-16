from fastapi import APIRouter, Depends
from redis import Redis
from app.core.dependencies import get_redis
from app.core.config import get_settings
from datetime import datetime
import logging

router = APIRouter(prefix="/health", tags=["health"])
logger = logging.getLogger(__name__)

@router.get("/")
async def health_check(
    redis: Redis = Depends(get_redis),
    settings = Depends(get_settings)
):
    """Basic health check endpoint."""
    try:
        # Check Redis connection
        redis_status = await redis.ping()
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = False

    return {
        "status": "healthy" if redis_status else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "redis": "up" if redis_status else "down",
        },
        "version": settings.VERSION
    }

@router.get("/readiness")
async def readiness_check(
    redis: Redis = Depends(get_redis)
):
    """Readiness probe for Kubernetes."""
    try:
        # Verify Redis connection
        await redis.ping()
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not ready"} 