from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, Tuple[datetime, int]] = {}
        self.window_size = timedelta(minutes=1)
        self.max_requests = 60  # 60 requests per minute

    async def check_rate_limit(self, user_id: str = None) -> bool:
        """
        Check if the request should be rate limited.
        Returns True if request is allowed, raises HTTPException if rate limited.
        """
        try:
            if not user_id:
                return True  # Skip rate limiting if no user_id

            current_time = datetime.now()
            
            # Clean up old entries
            self._cleanup_old_requests(current_time)

            # Get or create user's request record
            window_start, request_count = self.requests.get(user_id, (current_time, 0))

            # Reset window if needed
            if current_time - window_start > self.window_size:
                window_start = current_time
                request_count = 0

            # Check rate limit
            if request_count >= self.max_requests:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later."
                    }
                )

            # Update request count
            self.requests[user_id] = (window_start, request_count + 1)
            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in rate limiter: {e}")
            return True  # Allow request on error

    def _cleanup_old_requests(self, current_time: datetime) -> None:
        """Remove entries older than the window size."""
        cutoff_time = current_time - self.window_size
        self.requests = {
            user_id: (window_start, count)
            for user_id, (window_start, count) in self.requests.items()
            if window_start > cutoff_time
        } 