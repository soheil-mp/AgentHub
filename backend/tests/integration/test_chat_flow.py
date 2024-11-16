import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

class TestChatFlow:
    def test_product_query_flow(self, test_client, mock_chat_graph):
        """Test complete flow for product query."""
        with patch('app.api.routes.chat.get_chat_graph', return_value=mock_chat_graph), \
             patch('app.services.state.StateManager.get_state', new_callable=AsyncMock) as mock_get_state, \
             patch('app.services.state.StateManager.update_state', new_callable=AsyncMock) as mock_update_state:
            
            mock_get_state.return_value = {"messages": [], "context": {}}
            mock_update_state.return_value = True
            
            chat_request = {
                "messages": [{"role": "user", "content": "What are your product prices?"}],
                "user_id": "test_user_123",
                "context": {"locale": "en-US"}
            }
            
            response = test_client.post("/api/v1/chat/", json=chat_request)
            assert response.status_code == 200
            data = response.json()
            assert "messages" in data
            assert len(data["messages"]) > 0

    def test_conversation_context(self, test_client, mock_chat_graph):
        """Test conversation context preservation."""
        with patch('app.api.routes.chat.get_chat_graph', return_value=mock_chat_graph), \
             patch('app.services.state.StateManager.get_state', new_callable=AsyncMock) as mock_get_state, \
             patch('app.services.state.StateManager.update_state', new_callable=AsyncMock) as mock_update_state:
            
            mock_get_state.return_value = {"messages": [], "context": {}}
            mock_update_state.return_value = True
            
            # First message
            response1 = test_client.post("/api/v1/chat/", json={
                "messages": [{"role": "user", "content": "Tell me about your products"}],
                "user_id": "test_user_123"
            })
            assert response1.status_code == 200
            
            # Update mock state with first response
            mock_get_state.return_value = {
                "messages": [
                    {"role": "user", "content": "Tell me about your products"},
                    {"role": "assistant", "content": "Test response"}
                ],
                "context": {}
            }
            
            # Follow-up message
            response2 = test_client.post("/api/v1/chat/", json={
                "messages": [
                    {"role": "user", "content": "Tell me about your products"},
                    {"role": "assistant", "content": "Test response"},
                    {"role": "user", "content": "What about pricing?"}
                ],
                "user_id": "test_user_123"
            })
            assert response2.status_code == 200
            
            data = response2.json()
            assert len(data["messages"]) > 2

    def test_error_handling(self, test_client):
        """Test error handling in chat flow."""
        # Test invalid request
        response = test_client.post("/api/v1/chat/", json={
            "messages": [],  # Empty messages
            "user_id": "test_user_123"
        })
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "NO_MESSAGES"

    @pytest.mark.asyncio
    async def test_state_management(self, test_client, mock_state_manager):
        """Test state management during chat flow."""
        with patch('app.api.routes.chat.get_chat_graph', return_value=mock_chat_graph), \
             patch('app.services.state.StateManager.get_state', new_callable=AsyncMock) as mock_get_state, \
             patch('app.services.state.StateManager.update_state', new_callable=AsyncMock) as mock_update_state:
            
            mock_get_state.return_value = {"messages": [], "context": {}}
            mock_update_state.return_value = True
            
            # Initial request
            response = test_client.post("/api/v1/chat/", json={
                "messages": [{"role": "user", "content": "Hello"}],
                "user_id": "test_user_123"
            })
            assert response.status_code == 200
            
            # Verify state was updated
            mock_get_state.return_value = {
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Test response"}
                ],
                "context": {"dialog_state": "ROUTER"}
            }
            
            state = await mock_get_state()
            assert len(state["messages"]) > 0
            assert "dialog_state" in state["context"]