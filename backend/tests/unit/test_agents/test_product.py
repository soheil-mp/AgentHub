import pytest
from unittest.mock import Mock, patch
from app.services.agents.support.product import ProductAgent
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime

@pytest.fixture
def product_agent():
    return ProductAgent()

class TestProductAgent:
    @pytest.mark.asyncio
    async def test_process_product_query(self, product_agent):
        state = {
            "messages": [
                ("user", "What features does the premium plan include?")
            ],
            "context": {"user_id": "test_123"}
        }
        
        with patch.object(product_agent, '_safe_llm_call', 
                         return_value="The premium plan includes..."):
            result = await product_agent.process(state)
            
            assert not result["requires_action"]
            assert "last_product_interaction" in result["context"]
            assert isinstance(
                datetime.fromisoformat(result["context"]["last_product_interaction"]),
                datetime
            )

    @pytest.mark.asyncio
    async def test_escalate_to_technical(self, product_agent):
        state = {
            "messages": [
                ("user", "The product isn't working on my device")
            ],
            "context": {"user_id": "test_123"}
        }
        
        with patch.object(product_agent, '_safe_llm_call', 
                         return_value="This seems like a technical issue..."):
            result = await product_agent.process(state)
            
            assert result["requires_action"]
            assert result["next"] == "TECHNICAL"
            assert result["action_type"] == "ESCALATE"

    @pytest.mark.asyncio
    async def test_handle_pricing_query(self, product_agent):
        state = {
            "messages": [
                ("user", "How much does the basic plan cost?")
            ],
            "context": {"user_id": "test_123"}
        }
        
        with patch.object(product_agent, '_safe_llm_call', 
                         return_value="The basic plan costs $10/month..."):
            result = await product_agent.process(state)
            
            assert not result["requires_action"]
            assert len(result["messages"]) > len(state["messages"])
            assert "$10/month" in result["messages"][-1][1]

    @pytest.mark.asyncio
    async def test_error_recovery(self, product_agent):
        state = {
            "messages": [("user", "Tell me about products")],
            "context": {"user_id": "test_123"}
        }
        
        with patch.object(product_agent, '_safe_llm_call', side_effect=Exception("Test error")):
            result = await product_agent.process(state)
            
            assert result["requires_action"]
            assert result["next"] == "CUSTOMER_SERVICE"
            assert "error" in result
            assert "I apologize" in result["messages"][-1][1] 