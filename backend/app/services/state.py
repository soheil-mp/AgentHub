from typing import Optional, Dict, Any
from app.services.cache import get_cache
import json
import logging

logger = logging.getLogger(__name__)

class StateManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._cache = None

    async def _get_cache(self):
        """Lazy initialization of cache connection."""
        if self._cache is None:
            self._cache = await get_cache()
        return self._cache

    def _get_key(self) -> str:
        """Generate cache key for user state."""
        return f"state:{self.user_id}"

    async def get_state(self) -> Optional[Dict[str, Any]]:
        """Get current state for user."""
        try:
            cache = await self._get_cache()
            state = await cache.get(self._get_key())
            return state
        except Exception as e:
            logger.error(f"Error getting state for user {self.user_id}: {e}")
            return None

    async def update_state(self, state: Dict[str, Any]) -> bool:
        """Update state for user."""
        try:
            cache = await self._get_cache()
            success = await cache.set(self._get_key(), state)
            return success
        except Exception as e:
            logger.error(f"Error updating state for user {self.user_id}: {e}")
            return False

    async def clear_state(self) -> bool:
        """Clear state for user."""
        try:
            cache = await self._get_cache()
            success = await cache.delete(self._get_key())
            return success
        except Exception as e:
            logger.error(f"Error clearing state for user {self.user_id}: {e}")
            return False 