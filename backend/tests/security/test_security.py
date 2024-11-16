import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings
import json
import re
import time
import asyncio
import aiohttp
from unittest.mock import patch, AsyncMock

@pytest.fixture
def test_client():
    return TestClient(app)

class TestSecurity:
    def test_sql_injection_prevention(self, test_client, mock_chat_graph):
        """Test prevention of SQL injection attempts."""
        with patch('app.api.routes.chat.get_chat_graph', return_value=mock_chat_graph), \
             patch('app.services.state.StateManager.get_state', new_callable=AsyncMock) as mock_get_state, \
             patch('app.services.state.StateManager.update_state', new_callable=AsyncMock) as mock_update_state:
            
            mock_get_state.return_value = {"messages": [], "context": {}}
            mock_update_state.return_value = True
            
            malicious_inputs = [
                "'; DROP TABLE users; --",
                "1; SELECT * FROM users",
            ]
            
            for payload in malicious_inputs:
                response = test_client.post(
                    "/api/v1/chat/",
                    json={
                        "messages": [{"role": "user", "content": payload}],
                        "user_id": "test_user_123"
                    },
                    timeout=2
                )
                
                assert response.status_code in [200, 400, 422]
                if response.status_code == 200:
                    assert not any(
                        keyword in response.text.lower()
                        for keyword in ["select", "insert", "update", "delete", "drop"]
                    )

    def test_xss_prevention(self, test_client, mock_chat_graph):
        """Test prevention of XSS attempts."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src='x' onerror='alert(1)'>",
        ]
        
        with patch('app.api.routes.chat.get_chat_graph', return_value=mock_chat_graph):
            for payload in xss_payloads:
                response = test_client.post(
                    "/api/v1/chat/",
                    json={
                        "messages": [{"role": "user", "content": payload}],
                        "user_id": "test_user_123"
                    },
                    timeout=2
                )
                
                assert response.status_code == 200
                assert "<script>" not in response.text
                assert "javascript:" not in response.text

    @pytest.mark.asyncio
    async def test_rate_limiting(self, test_client, mock_chat_graph):
        """Test rate limiting functionality."""
        with patch('app.api.routes.chat.get_chat_graph', return_value=mock_chat_graph):
            async def make_request():
                return test_client.post(
                    "/api/v1/chat/",
                    json={
                        "messages": [{"role": "user", "content": "test"}],
                        "user_id": "test_user_123"
                    },
                    timeout=2
                ).status_code

            # Make concurrent requests
            tasks = [make_request() for _ in range(10)]
            responses = await asyncio.gather(*tasks)
            assert 429 in responses  # At least one request should be rate limited

    def test_input_validation(self, test_client):
        """Test input validation and sanitization."""
        invalid_inputs = [
            {"messages": None},
            {"messages": [], "user_id": ""},
            {"messages": [{"role": "invalid", "content": "test"}]},
            {"messages": [{"role": "user", "content": "x" * 10000}]},  # Too long
        ]
        
        for payload in invalid_inputs:
            response = test_client.post("/api/v1/chat/", json=payload)
            assert response.status_code in [400, 422]

    def test_error_message_safety(self, test_client):
        """Test that error messages don't leak sensitive information."""
        response = test_client.post(
            "/api/v1/chat/",
            json={"invalid": "data"}
        )
        
        assert response.status_code in [400, 422]
        error_response = response.json()
        
        assert not any(
            sensitive in json.dumps(error_response).lower()
            for sensitive in ["password", "token", "key", "secret", "credentials"]
        ) 