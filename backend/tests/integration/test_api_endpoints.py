import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings
from typing import Dict, Any
import json
from unittest.mock import patch, AsyncMock

@pytest.fixture
def test_client():
    with patch('app.services.cache.RedisCache.get', new_callable=AsyncMock) as mock_get, \
         patch('app.services.cache.RedisCache.set', new_callable=AsyncMock) as mock_set:
        mock_get.return_value = None
        mock_set.return_value = True
        yield TestClient(app)

@pytest.fixture
def valid_chat_request() -> Dict[str, Any]:
    return {
        "messages": [
            {"role": "user", "content": "Hello, I need help"}
        ],
        "user_id": "test_user_123",
        "context": {"locale": "en-US"}
    }

@pytest.fixture
def mock_chat_graph():
    """Mock chat graph for testing."""
    return {
        "nodes": [],
        "edges": [],
        "start_node": "start",
        "end_node": "end",
    }

class TestChatEndpoints:
    def test_chat_successful_response(self, test_client, valid_chat_request, mock_chat_graph):
        with patch('app.api.routes.chat.get_chat_graph', return_value=mock_chat_graph), \
             patch('app.services.state.StateManager.get_state', new_callable=AsyncMock) as mock_get_state, \
             patch('app.services.state.StateManager.update_state', new_callable=AsyncMock) as mock_update_state:
            
            mock_get_state.return_value = {"messages": [], "context": {}}
            mock_update_state.return_value = True
            
            response = test_client.post("/api/v1/chat/", json=valid_chat_request)
            assert response.status_code == 200
            data = response.json()
            assert "messages" in data
            assert "next" in data

    def test_chat_empty_messages(self, test_client):
        request = {
            "messages": [],
            "user_id": "test_user_123"
        }
        response = test_client.post("/api/v1/chat/", json=request)
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["code"] == "NO_MESSAGES"

    def test_chat_missing_user_id(self, test_client):
        request = {
            "messages": [{"role": "user", "content": "Hello"}]
            # missing user_id
        }
        response = test_client.post("/api/v1/chat/", json=request)
        
        assert response.status_code == 422
        data = response.json()
        assert "user_id" in str(data["detail"])

    def test_chat_invalid_message_format(self, test_client):
        request = {
            "messages": [{"invalid_field": "content"}],
            "user_id": "test_user_123"
        }
        response = test_client.post("/api/v1/chat/", json=request)

        assert response.status_code == 422
        data = response.json()
        assert "field required" in str(data["detail"]).lower()

    def test_chat_large_context(self, test_client, mock_chat_graph):
        large_context = {"data" + str(i): "value" for i in range(100)}
        request = {
            "messages": [{"role": "user", "content": "Hello"}],
            "user_id": "test_user_123",
            "context": large_context
        }
        
        with patch('app.api.routes.chat.get_chat_graph', return_value=mock_chat_graph):
            response = test_client.post("/api/v1/chat/", json=request)
            assert response.status_code == 200

    def test_chat_conversation_flow(self, test_client, mock_chat_graph):
        with patch('app.api.routes.chat.get_chat_graph', return_value=mock_chat_graph):
            # First message
            request1 = {
                "messages": [{"role": "user", "content": "I have a technical issue"}],
                "user_id": "test_user_123"
            }
            response1 = test_client.post("/api/v1/chat/", json=request1)
            assert response1.status_code == 200
            
            # Follow-up message
            request2 = {
                "messages": [
                    {"role": "user", "content": "I have a technical issue"},
                    {"role": "assistant", "content": response1.json()["messages"][-1]["content"]},
                    {"role": "user", "content": "Yes, it's about login"}
                ],
                "user_id": "test_user_123"
            }
            response2 = test_client.post("/api/v1/chat/", json=request2)
            assert response2.status_code == 200
            
            # Verify conversation continuity
            data = response2.json()
            assert len(data["messages"]) > len(response1.json()["messages"]) 