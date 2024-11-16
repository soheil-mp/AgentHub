import pytest
import asyncio
from typing import List, Dict, Any
from app.services.graph import get_chat_graph
from app.services.state import StateManager
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def sample_requests() -> List[Dict[str, Any]]:
    return [
        {
            "messages": [("user", f"Test message {i}")],
            "user_id": f"test_user_{i}",
            "context": {"test_param": f"value_{i}"}
        } for i in range(50)
    ]

class TestLoadPerformance:
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, sample_requests):
        """Test system performance under concurrent load."""
        start_time = time.time()
        response_times = []
        
        async def process_request(request: Dict[str, Any]) -> float:
            req_start = time.time()
            state_manager = StateManager(request["user_id"])
            graph = get_chat_graph()
            
            try:
                await state_manager.update_state(request)
                await graph.ainvoke(request)
                return time.time() - req_start
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                return -1
        
        # Process requests concurrently
        tasks = [process_request(req) for req in sample_requests]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        valid_times = [t for t in results if t > 0]
        total_time = time.time() - start_time
        
        metrics = {
            "total_requests": len(sample_requests),
            "successful_requests": len(valid_times),
            "failed_requests": len(results) - len(valid_times),
            "total_time": total_time,
            "avg_response_time": statistics.mean(valid_times),
            "median_response_time": statistics.median(valid_times),
            "p95_response_time": statistics.quantiles(valid_times, n=20)[-1],
            "requests_per_second": len(valid_times) / total_time
        }
        
        # Assert performance requirements
        assert metrics["successful_requests"] / len(sample_requests) >= 0.95
        assert metrics["avg_response_time"] < 2.0
        assert metrics["p95_response_time"] < 5.0

    @pytest.mark.asyncio
    async def test_memory_usage(self, sample_requests):
        """Test memory usage under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process requests sequentially to measure memory growth
        state_managers = []
        for request in sample_requests:
            manager = StateManager(request["user_id"])
            await manager.update_state(request)
            state_managers.append(manager)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Cleanup
        for manager in state_managers:
            await manager.clear_state()
        
        # Assert reasonable memory usage
        assert memory_growth < 100  # MB
        
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting functionality."""
        from app.services.agents.base import RateLimiter
        
        limiter = RateLimiter(calls_per_minute=30)
        start_time = time.time()
        
        # Try to make requests faster than the rate limit
        for _ in range(40):
            await limiter.acquire()
        
        total_time = time.time() - start_time
        
        # Should take at least 1 minute due to rate limiting
        assert total_time >= 60 