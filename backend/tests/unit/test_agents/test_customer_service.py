import pytest
from unittest.mock import Mock, patch
from app.services.agents.support.customer_service import CustomerServiceAgent
from langchain_core.messages import HumanMessage, AIMessage

@pytest.fixture
def cs_agent():
    return CustomerServiceAgent()

class TestCustomerServiceAgent:
    @pytest.mark.asyncio
    async def test_handle_billing_query(self, cs_agent, mock_llm_response):
        state = {
            "messages": [
                ("user", "I have a question about my bill")
            ],
            "context": {"user_id": "test_123"}
        }
        
        with patch.object(cs_agent, '_safe_llm_call', return_value="Here's information about your bill"):
            result = await cs_agent.process(state)
            
            assert not result["requires_action"]
            assert "CUSTOMER_SERVICE" in result["dialog_state"]
            assert len(result["messages"]) > len(state["messages"])

    @pytest.mark.asyncio
    async def test_escalate_to_technical(self, cs_agent):
        state = {
            "messages": [
                ("user", "My account keeps showing technical errors")
            ],
            "context": {"user_id": "test_123"}
        }
        
        with patch.object(cs_agent, '_safe_llm_call', 
                         return_value="This seems like a technical issue. Let me transfer you."):
            result = await cs_agent.process(state)
            
            assert result["requires_action"]
            assert result["next"] == "TECHNICAL"
            assert result["action_type"] == "ESCALATE"

    def test_format_interaction_history(self, cs_agent):
        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there"),
            HumanMessage(content="Need help")
        ]
        
        history = cs_agent._format_interaction_history(messages)
        
        assert "Customer: Hello" in history
        assert "Agent: Hi there" in history
        assert len(history.split("\n")) == 3

    @pytest.mark.asyncio
    async def test_error_recovery(self, cs_agent):
        state = {
            "messages": [("user", "Hello")],
            "context": {"user_id": "test_123"}
        }
        
        with patch.object(cs_agent, '_safe_llm_call', side_effect=Exception("Test error")):
            result = await cs_agent.process(state)
            
            assert "error" in result
            assert "I apologize" in result["messages"][-1][1]
            assert not result["requires_action"] 