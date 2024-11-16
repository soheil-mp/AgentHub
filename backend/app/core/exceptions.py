from typing import Optional, Dict, Any
from fastapi import HTTPException, status

class BaseError(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class AgentError(BaseError):
    """Errors related to agent operations"""
    pass

class StateError(BaseError):
    """Errors related to state management"""
    pass

class CacheError(BaseError):
    """Errors related to caching operations"""
    pass

class ValidationError(BaseError):
    """Errors related to input validation"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        ) 