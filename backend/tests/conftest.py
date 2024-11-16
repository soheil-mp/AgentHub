import pytest
from fastapi.testclient import TestClient
from redis.asyncio import Redis
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from typing import Generator, AsyncGenerator
from app.main import app, create_app
from app.core.config import Settings, get_settings
from app.services.cache import RedisCache, cache
from app.services.state import StateManager
from app.services.graph import get_chat_graph
from unittest.mock import patch

@pytest.fixture
def test_settings() -> Settings:
    """Test settings with test configurations."""
    return Settings(
        OPENAI_API_KEY="test-api-key",
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        REDIS_DB=1,  # Use different DB for testing
        PROJECT_NAME="TestAgentHub",
        RATE_LIMIT_PER_MINUTE=100
    )

@pytest.fixture
def test_app(test_settings):
    """Test app fixture."""
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: test_settings
    return app

@pytest.fixture
def test_client(test_app):
    """Test client fixture with mocked Redis."""
    with patch('app.services.cache.redis_client') as mock_redis:
        # Mock Redis methods
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock(return_value=True)
        mock_redis.delete = AsyncMock(return_value=True)
        mock_redis.aclose = AsyncMock()
        
        # Create test client
        client = TestClient(test_app)
        yield client

@pytest.fixture
def mock_chat_graph():
    """Mock chat graph for testing."""
    return {
        "messages": [{"role": "assistant", "content": "Test response"}],
        "requires_action": False,
        "next": None,
        "dialog_state": "ROUTER",
        "context": {},
        "ainvoke": AsyncMock(return_value={
            "messages": [{"role": "assistant", "content": "Test response"}],
            "requires_action": False,
            "next": None,
            "dialog_state": "ROUTER",
            "context": {}
        })
    }

@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    client = AsyncMock(spec=Redis)
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=True)
    client.aclose = AsyncMock()
    return client

@pytest.fixture
def mock_redis_connection(mock_redis_client):
    """Mock Redis connection."""
    with patch('app.services.cache.redis_client', mock_redis_client):
        yield mock_redis_client

@pytest.fixture
def mock_state_manager():
    """Mock state manager."""
    manager = AsyncMock()
    manager.get_state = AsyncMock(return_value={"messages": [], "context": {}})
    manager.update_state = AsyncMock(return_value=True)
    manager.cleanup = AsyncMock()
    return manager

@pytest.fixture(autouse=True)
def override_cache(mock_redis_connection):
    """Override cache with mock Redis."""
    with patch('app.core.dependencies.cache.client', mock_redis_connection):
        yield

@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter."""
    limiter = AsyncMock()
    limiter.acquire = AsyncMock()
    return limiter

@pytest.fixture(autouse=True)
def mock_llm():
    """Mock LLM to prevent API calls."""
    with patch('langchain_openai.ChatOpenAI') as mock:
        mock_llm = mock.return_value
        mock_llm.invoke = Mock(return_value="Test response")
        mock_llm.ainvoke = AsyncMock(return_value="Test response")
        yield mock_llm

@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "content": "This is a mock LLM response",
        "additional_kwargs": {},
        "type": "ai",
        "example": False,
    }

@pytest.fixture
def mock_llm_string_response():
    """Mock LLM string response for testing."""
    return "This is a mock LLM response" 