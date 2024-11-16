import pytest
from unittest.mock import Mock, AsyncMock
from app.services.cache import RedisCache
import json

@pytest.fixture
def redis_cache():
    mock_client = Mock()
    mock_client.get = AsyncMock()
    mock_client.set = AsyncMock()
    mock_client.delete = AsyncMock()
    cache = RedisCache(client=mock_client)
    return cache

class TestRedisCache:
    @pytest.mark.asyncio
    async def test_get_existing_key(self, redis_cache):
        test_data = {"key": "value"}
        redis_cache.client.get.return_value = json.dumps(test_data)
        
        result = await redis_cache.get("test_key")
        assert result == test_data
        redis_cache.client.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, redis_cache):
        redis_cache.client.get.return_value = None
        
        result = await redis_cache.get("nonexistent_key")
        assert result is None
        redis_cache.client.get.assert_called_once_with("nonexistent_key")

    @pytest.mark.asyncio
    async def test_set_successful(self, redis_cache):
        test_data = {"key": "value"}
        redis_cache.client.set.return_value = True
        
        result = await redis_cache.set("test_key", test_data)
        assert result is True
        redis_cache.client.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_with_ttl(self, redis_cache):
        test_data = {"key": "value"}
        ttl = 3600
        redis_cache.client.set.return_value = True
        
        result = await redis_cache.set("test_key", test_data, ttl)
        assert result is True
        redis_cache.client.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_existing_key(self, redis_cache):
        redis_cache.client.delete.return_value = 1
        
        result = await redis_cache.delete("test_key")
        assert result is True
        redis_cache.client.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self, redis_cache):
        redis_cache.client.delete.return_value = 0
        
        result = await redis_cache.delete("nonexistent_key")
        assert result is False
        redis_cache.client.delete.assert_called_once_with("nonexistent_key")

    @pytest.mark.asyncio
    async def test_error_handling(self, redis_cache):
        redis_cache.client.get.side_effect = Exception("Test error")
        
        result = await redis_cache.get("test_key")
        assert result is None 