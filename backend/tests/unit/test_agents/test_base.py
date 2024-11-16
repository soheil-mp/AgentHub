import pytest
from unittest.mock import Mock, patch
from app.services.agents.base import BaseAgent, RateLimiter
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from datetime import datetime, timedelta

@pytest.fixture
def base_agent():
    return BaseAgent(
        model="gpt-3.5-turbo",
        temperature=0.7,
        system_prompt="Test system prompt"
    )

class TestBaseAgent:
    def test_init(self, base_agent):
        assert base_agent.system_prompt == "Test system prompt"
        assert base_agent.llm is not None
        assert base_agent.memory is not None

    def test_format_messages(self, base_agent):
        messages = [
            ("user", "Hello"),
            ("assistant", "Hi there"),
            ("system", "System message")
        ]
        formatted = base_agent.format_messages(messages)
        
        assert len(formatted) == 4  # Including system prompt
        assert isinstance(formatted[0], SystemMessage)
        assert isinstance(formatted[1], HumanMessage)
        assert isinstance(formatted[2], AIMessage)
        assert isinstance(formatted[3], SystemMessage)

    @pytest.mark.asyncio
    async def test_safe_llm_call(self, base_agent, mock_llm_response):
        with patch.object(base_agent.llm, 'ainvoke') as mock_invoke:
            mock_invoke.return_value.content = mock_llm_response
            messages = [HumanMessage(content="Test")]
            
            response = await base_agent._safe_llm_call(messages)
            assert response == mock_llm_response
            mock_invoke.assert_called_once()

    def test_update_memory(self, base_agent):
        messages = [
            HumanMessage(content="User message"),
            AIMessage(content="Assistant message")
        ]
        base_agent.update_memory(messages)
        memory_messages = base_agent.get_memory_messages()
        
        assert len(memory_messages) == 2
        assert isinstance(memory_messages[0], HumanMessage)
        assert isinstance(memory_messages[1], AIMessage)

    def test_clear_memory(self, base_agent):
        messages = [HumanMessage(content="Test")]
        base_agent.update_memory(messages)
        base_agent.clear_memory()
        
        assert len(base_agent.get_memory_messages()) == 0

class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        limiter = RateLimiter(calls_per_minute=2)
        
        # First two calls should be immediate
        start_time = datetime.now()
        await limiter.acquire()
        await limiter.acquire()
        first_duration = datetime.now() - start_time
        
        # Third call should wait
        await limiter.acquire()
        total_duration = datetime.now() - start_time
        
        assert first_duration < timedelta(seconds=1)
        assert total_duration >= timedelta(seconds=1) 