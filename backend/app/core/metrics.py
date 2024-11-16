from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

# Metrics
REQUEST_COUNT = Counter(
    'app_request_count_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'app_active_requests',
    'Number of active requests'
)

LLM_CALLS = Counter(
    'app_llm_calls_total',
    'Total number of LLM API calls',
    ['agent_type', 'status']
)

LLM_LATENCY = Histogram(
    'app_llm_latency_seconds',
    'LLM API call latency in seconds',
    ['agent_type']
)

def track_request_metrics():
    """Decorator to track request metrics."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            ACTIVE_REQUESTS.inc()
            
            try:
                response = await func(*args, **kwargs)
                status = response.status_code
            except Exception as e:
                status = 500
                raise
            finally:
                duration = time.time() - start_time
                ACTIVE_REQUESTS.dec()
                
                # Record metrics
                REQUEST_COUNT.labels(
                    method=kwargs.get('request').method,
                    endpoint=kwargs.get('request').url.path,
                    status=status
                ).inc()
                
                REQUEST_LATENCY.labels(
                    method=kwargs.get('request').method,
                    endpoint=kwargs.get('request').url.path
                ).observe(duration)
            
            return response
        return wrapper
    return decorator

def track_llm_metrics(agent_type: str):
    """Decorator to track LLM API call metrics."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                response = await func(*args, **kwargs)
                status = "success"
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                
                # Record metrics
                LLM_CALLS.labels(
                    agent_type=agent_type,
                    status=status
                ).inc()
                
                LLM_LATENCY.labels(
                    agent_type=agent_type
                ).observe(duration)
            
            return response
        return wrapper
    return decorator 