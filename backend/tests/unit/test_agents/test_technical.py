import pytest
from unittest.mock import Mock, patch
from app.services.agents.support.technical import TechnicalAgent
from langchain_core.messages import HumanMessage, AIMessage

@pytest.fixture
def technical_agent():
    return TechnicalAgent()

class TestTechnicalAgent:
    @pytest.mark.asyncio
    async def test_process_technical_issue(self, technical_agent, mock_llm_response):
        state = {
            "messages": [
                ("user", "My app keeps crashing when I try to login")
            ],
            "context": {"user_id": "test_123"}
        }
        
        with patch.object(technical_agent, '_safe_llm_call', 
                         return_value="Here are the steps to resolve your login issue..."):
            result = await technical_agent.process(state)
            
            assert not result["requires_action"]
            assert "TECHNICAL" in result["dialog_state"]
            assert len(result["messages"]) > len(state["messages"])

    @pytest.mark.asyncio
    async def test_escalate_to_product(self, technical_agent):
        state = {
            "messages": [
                ("user", "What are the system requirements for the app?")
            ],
            "context": {"user_id": "test_123"}
        }
        
        with patch.object(technical_agent, '_safe_llm_call', 
                         return_value="I'll need to check the product specifications..."):
            result = await technical_agent.process(state)
            
            assert result["requires_action"]
            assert result["next"] == "PRODUCT"
            assert result["action_type"] == "ESCALATE"

    def test_needs_escalation(self, technical_agent):
        # Test product escalation
        response = "I need to check the product specifications to answer that."
        needs_escalation, dept, reason = technical_agent._needs_escalation(response)
        assert needs_escalation
        assert dept == "PRODUCT"
        
        # Test billing escalation
        response = "This seems to be a billing issue."
        needs_escalation, dept, reason = technical_agent._needs_escalation(response)
        assert needs_escalation
        assert dept == "CUSTOMER_SERVICE"
        
        # Test no escalation needed
        response = "Here's how to fix your technical issue..."
        needs_escalation, dept, reason = technical_agent._needs_escalation(response)
        assert not needs_escalation

    @pytest.mark.asyncio
    async def test_error_handling(self, technical_agent):
        state = {
            "messages": [("user", "Help with error")],
            "context": {"user_id": "test_123"}
        }
        
        with patch.object(technical_agent, '_safe_llm_call', side_effect=Exception("Test error")):
            result = await technical_agent.process(state)
            
            assert result["requires_action"]
            assert result["next"] == "CUSTOMER_SERVICE"
            assert "error" in result
            assert "I apologize" in result["messages"][-1][1] 