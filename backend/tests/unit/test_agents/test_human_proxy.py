import pytest
from unittest.mock import Mock, patch
from app.services.agents.support.human_proxy import HumanProxyAgent
from langchain_core.messages import HumanMessage, AIMessage

@pytest.fixture
def human_proxy_agent():
    return HumanProxyAgent()

class TestHumanProxyAgent:
    def test_format_case_summary(self, human_proxy_agent):
        messages = [
            HumanMessage(content="I need urgent help"),
            AIMessage(content="I understand your concern")
        ]
        context = {
            "user_id": "test_123",
            "priority_level": "High",
            "escalation_reason": "Urgent assistance needed"
        }
        
        summary = human_proxy_agent._format_case_summary(messages, context)
        
        assert "Case Summary" in summary
        assert "User ID: test_123" in summary
        assert "Priority: High" in summary
        assert "Customer: I need urgent help" in summary
        assert "AI: I understand your concern" in summary

    @pytest.mark.asyncio
    async def test_process_urgent_case(self, human_proxy_agent):
        state = {
            "messages": [
                ("user", "This is an urgent issue that needs human attention")
            ],
            "context": {
                "user_id": "test_123",
                "priority_level": "High"
            }
        }
        
        result = await human_proxy_agent.process(state)
        
        assert result["requires_action"]
        assert result["next"] == "HUMAN_AGENT"
        assert result["action_type"] == "HUMAN_ESCALATION"
        assert "priority" in result
        assert "case_summary" in result
        assert "needs_human_review" in result["context"]

    @pytest.mark.asyncio
    async def test_error_handling(self, human_proxy_agent):
        state = {
            "messages": [("user", "Need help")],
            "context": {"user_id": "test_123"}
        }
        
        with patch.object(human_proxy_agent, '_format_case_summary', 
                         side_effect=Exception("Test error")):
            result = await human_proxy_agent.process(state)
            
            assert result["requires_action"]
            assert result["next"] == "CUSTOMER_SERVICE"
            assert "error" in result
            assert "I apologize" in result["messages"][-1][1]

    def test_format_case_summary_with_long_history(self, human_proxy_agent):
        messages = [HumanMessage(content=f"Message {i}") for i in range(10)]
        context = {"user_id": "test_123"}
        
        summary = human_proxy_agent._format_case_summary(messages, context)
        
        # Should only include last 5 messages
        assert summary.count("Customer:") == 5
        assert "Message 9" in summary
        assert "Message 0" not in summary 