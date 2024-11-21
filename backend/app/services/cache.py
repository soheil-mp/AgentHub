from typing import Optional, Any
from redis.asyncio import Redis
import json
import logging
from app.core.config import settings
 
logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, redis_client: Optional[Redis]):
        self.redis = redis_client
        self.ttl = settings.REDIS_TTL

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if not self.redis or not settings.REDIS_ENABLED:
                return None
                
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        try:
            if not self.redis or not settings.REDIS_ENABLED:
                return False
                
            serialized = json.dumps(value)
            await self.redis.set(
                key,
                serialized,
                ex=ttl or self.ttl
            )
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            if not self.redis or not settings.REDIS_ENABLED:
                return False
                
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    async def close(self):
        """Close Redis connection."""
        try:
            if self.redis:
                await self.redis.close()
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")

_cache: Optional[RedisCache] = None

async def get_cache() -> RedisCache:
    """Get or create Redis cache instance."""
    global _cache
    
    if _cache is None:
        try:
            if not settings.REDIS_ENABLED:
                logger.warning("Redis is disabled. Using no-op cache.")
                redis_client = None
            else:
                redis_client = Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD or None,
                    decode_responses=True
                )
                # Test connection
                await redis_client.ping()
                
            _cache = RedisCache(redis_client)
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.error(f"Error initializing Redis cache: {e}")
            # Create no-op cache instance if Redis fails
            _cache = RedisCache(None)
    
    return _cache

def get_redis() -> Redis:
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )
    try:
        yield redis
    finally:
        redis.close()