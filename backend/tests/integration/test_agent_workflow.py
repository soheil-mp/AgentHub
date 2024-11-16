import pytest
from app.services.graph import get_chat_graph
from app.services.state import StateManager
from typing import Dict, Any
import json

@pytest.fixture
async def state_manager():
    manager = StateManager("test_user_123")
    yield manager
    await manager.clear_state()

class TestAgentWorkflow:
    @pytest.mark.asyncio
    async def test_technical_to_product_flow(self, state_manager):
        initial_state = {
            "messages": [
                ("user", "I'm having trouble installing the premium version")
            ],
            "context": {"user_id": "test_user_123"}
        }
        
        # Initialize state
        await state_manager.update_state(initial_state)
        
        # Process through graph
        graph = get_chat_graph()
        result = await graph.ainvoke(initial_state)
        
        # Verify flow
        assert "TECHNICAL" in result["dialog_state"]
        assert result.get("requires_action") == True
        assert result.get("next") == "PRODUCT"

    @pytest.mark.asyncio
    async def test_product_to_customer_service_flow(self, state_manager):
        initial_state = {
            "messages": [
                ("user", "What's the price of the premium plan?"),
                ("assistant", "The premium plan is $29.99/month"),
                ("user", "I have a billing issue with my subscription")
            ],
            "context": {"user_id": "test_user_123"}
        }
        
        await state_manager.update_state(initial_state)
        graph = get_chat_graph()
        result = await graph.ainvoke(initial_state)
        
        assert "PRODUCT" in result["dialog_state"]
        assert result.get("requires_action") == True
        assert result.get("next") == "CUSTOMER_SERVICE"

    @pytest.mark.asyncio
    async def test_escalation_to_human(self, state_manager):
        initial_state = {
            "messages": [
                ("user", "This is urgent and needs immediate attention")
            ],
            "context": {
                "user_id": "test_user_123",
                "error_count": 3
            }
        }
        
        await state_manager.update_state(initial_state)
        graph = get_chat_graph()
        result = await graph.ainvoke(initial_state)
        
        assert "HUMAN_PROXY" in result["dialog_state"]
        assert result.get("requires_action") == True
        assert result.get("next") == "HUMAN_AGENT"
        assert result.get("priority") == "HIGH"

    @pytest.mark.asyncio
    async def test_error_recovery_flow(self, state_manager):
        initial_state = {
            "messages": [
                ("user", "Hello"),
                ("assistant", "Hi there"),
                ("system", "Error occurred")
            ],
            "context": {
                "user_id": "test_user_123",
                "error_count": 1
            }
        }
        
        await state_manager.update_state(initial_state)
        graph = get_chat_graph()
        result = await graph.ainvoke(initial_state)
        
        assert result.get("error") is not None
        assert result.get("next") == "CUSTOMER_SERVICE"
        assert "error_count" in result["context"]
        assert result["context"]["error_count"] > 1 