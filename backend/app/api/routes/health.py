from fastapi import APIRouter, Depends
from typing import Dict
from datetime import datetime
from app.services.database import get_db
from app.services.cache import get_redis
from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict:
    """Overall system health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/db")
async def db_health(db: AsyncIOMotorClient = Depends(get_db)) -> Dict:
    """MongoDB health check"""
    try:
        # Ping MongoDB
        await db.admin.command('ping')
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "connected": True,
                "latency_ms": 0  # You could implement actual latency measurement
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/health/cache")
async def cache_health(redis: Redis = Depends(get_redis)) -> Dict:
    """Redis health check"""
    try:
        # Ping Redis
        redis.ping()
        info = redis.info()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "connected": True,
                "used_memory": info["used_memory_human"],
                "connected_clients": info["connected_clients"],
                "uptime_days": info["uptime_in_days"]
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/health/agents")
async def agents_health() -> Dict:
    """Agent system health check"""
    # This could be expanded to actually check agent availability
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": {
            "router": "available",
            "flight_booking": "available",
            "hotel_booking": "available",
            "car_rental": "available",
            "excursion": "available",
            "sensitive_workflow": "available"
        }
    } 