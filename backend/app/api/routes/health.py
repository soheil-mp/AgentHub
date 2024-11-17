from fastapi import APIRouter, HTTPException
from app.services.cache import cache

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """Check if the service and its dependencies are healthy."""
    try:
        # Check Redis connection
        if cache and cache.client:
            await cache.client.ping()
        else:
            raise HTTPException(status_code=503, detail="Cache not available")
        
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e)) 