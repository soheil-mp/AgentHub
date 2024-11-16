import json
import logging
from typing import Any, Optional
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, client: AsyncRedis):
        self.client = client

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        try:
            serialized = json.dumps(value)
            if ttl:
                return await self.client.set(key, serialized, ex=ttl)
            return await self.client.set(key, serialized)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            result = await self.client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

# Create a singleton Redis client
redis_client = AsyncRedis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    encoding="utf-8",
    decode_responses=True
)

# Export the cache instance
cache = RedisCache(client=redis_client) 