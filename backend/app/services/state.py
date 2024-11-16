from typing import Dict, Any, Optional
from datetime import datetime
import json
from app.services.cache import cache
import logging

logger = logging.getLogger(__name__)

class StateManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._state_key = f"state:{user_id}"
        self._history_key = f"history:{user_id}"

    async def get_state(self) -> Dict[str, Any]:
        """Get current state for user"""
        try:
            state = cache.get(self._state_key)
            return state if state else {
                "messages": [],
                "next": "ROUTER",
                "context": {"user_id": self.user_id},
                "dialog_state": []
            }
        except Exception as e:
            logger.error(f"Error getting state: {e}")
            return self._get_default_state()

    async def update_state(self, state: Dict[str, Any]) -> bool:
        """Update state and save to history"""
        try:
            # Save current state
            success = cache.set(self._state_key, state)
            
            # Add to history with timestamp
            history_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "state": state
            }
            current_history = cache.get(self._history_key) or []
            current_history.append(history_entry)
            
            # Keep last 10 state changes
            if len(current_history) > 10:
                current_history = current_history[-10:]
            
            cache.set(self._history_key, current_history)
            
            return success
        except Exception as e:
            logger.error(f"Error updating state: {e}")
            return False

    async def clear_state(self) -> bool:
        """Clear current state"""
        try:
            return (
                cache.delete(self._state_key) and
                cache.delete(self._history_key)
            )
        except Exception as e:
            logger.error(f"Error clearing state: {e}")
            return False

    def _get_default_state(self) -> Dict[str, Any]:
        """Return default state structure"""
        return {
            "messages": [],
            "next": "ROUTER",
            "context": {"user_id": self.user_id},
            "dialog_state": []
        } 