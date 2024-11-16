from typing import AsyncGenerator
from fastapi import Depends
from redis.asyncio import Redis
from app.services.cache import RedisCache, cache
from app.services.state import StateManager
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

async def get_redis() -> AsyncGenerator[Redis, None]:
    """Dependency for Redis connection."""
    try:
        yield cache.client
    finally:
        await cache.client.aclose()

async def get_state_manager(
    user_id: str,
    redis: Redis = Depends(get_redis)
) -> AsyncGenerator[StateManager, None]:
    """Dependency for StateManager."""
    try:
        state_manager = StateManager(user_id=user_id, redis=redis)
        yield state_manager
    finally:
        await state_manager.cleanup() 