import pytest
from unittest.mock import Mock, patch
from app.services.state import StateManager
from datetime import datetime

@pytest.fixture
def state_manager():
    return StateManager("test_user_123")

class TestStateManager:
    @pytest.mark.asyncio
    async def test_get_state_new_user(self, state_manager, mock_cache):
        state = await state_manager.get_state()
        
        assert state["messages"] == []
        assert state["next"] == "ROUTER"
        assert state["context"]["user_id"] == "test_user_123"
        assert state["dialog_state"] == []

    @pytest.mark.asyncio
    async def test_update_state(self, state_manager, mock_cache):
        test_state = {
            "messages": [("user", "test message")],
            "next": "PRODUCT",
            "context": {"user_id": "test_user_123"},
            "dialog_state": ["ROUTER", "PRODUCT"]
        }
        
        success = await state_manager.update_state(test_state)
        assert success is True
        
        # Verify history was updated
        history = mock_cache.get(f"history:{state_manager.user_id}")
        assert len(history) == 1
        assert "timestamp" in history[0]
        assert history[0]["state"] == test_state

    @pytest.mark.asyncio
    async def test_clear_state(self, state_manager, mock_cache):
        success = await state_manager.clear_state()
        assert success is True
        
        mock_cache.delete.assert_any_call(f"state:{state_manager.user_id}")
        mock_cache.delete.assert_any_call(f"history:{state_manager.user_id}")

    @pytest.mark.asyncio
    async def test_history_limit(self, state_manager, mock_cache):
        # Create 12 state updates
        for i in range(12):
            state = {
                "messages": [("user", f"message {i}")],
                "next": "ROUTER",
                "context": {"user_id": "test_user_123"},
                "dialog_state": ["ROUTER"]
            }
            await state_manager.update_state(state)
        
        # Verify only last 10 states are kept
        history = mock_cache.get(f"history:{state_manager.user_id}")
        assert len(history) == 10
        assert history[-1]["state"]["messages"][0][1] == "message 11" 