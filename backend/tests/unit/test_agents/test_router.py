import pytest
from unittest.mock import Mock, patch
from app.services.agents.router import RouterAgent
from langchain_core.messages import HumanMessage, AIMessage

@pytest.fixture
def router_agent():
    return RouterAgent()

class TestRouterAgent:
    @pytest.mark.asyncio
    async def test_route_to_product(self, router_agent):
        state = {
            "messages": [
                ("user", "What are the prices of your products?")
            ],
            "context": {"user_id": "test_123"}
        }
        
        result = await router_agent.process(state)
        
        assert result["next"] == "PRODUCT"
        assert "ROUTER" in result["dialog_state"]
        assert not result.get("error")

    @pytest.mark.asyncio
    async def test_route_to_technical(self, router_agent):
        state = {
            "messages": [
                ("user", "I'm having a technical issue with the app")
            ],
            "context": {"user_id": "test_123"}
        }
        
        result = await router_agent.process(state)
        
        assert result["next"] == "TECHNICAL"
        assert "ROUTER" in result["dialog_state"]

    @pytest.mark.asyncio
    async def test_route_to_customer_service(self, router_agent):
        state = {
            "messages": [
                ("user", "I need help with my billing")
            ],
            "context": {"user_id": "test_123"}
        }
        
        result = await router_agent.process(state)
        
        assert result["next"] == "CUSTOMER_SERVICE"
        assert "ROUTER" in result["dialog_state"]

    @pytest.mark.asyncio
    async def test_error_handling(self, router_agent):
        with patch.object(router_agent, '_safe_llm_call', return_value=None):
            state = {
                "messages": [("user", "Hello")],
                "context": {"user_id": "test_123"}
            }
            
            result = await router_agent.process(state)
            
            assert result["error"]
            assert result["next"] == "CUSTOMER_SERVICE"
            assert "Error processing request" in result["messages"][-1][1] 