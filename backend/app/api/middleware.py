from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
import time
import logging

logger = logging.getLogger(__name__)

async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url}")
        logger.error(f"Error details: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

def setup_middleware(app):
    # Add CORS middleware with development-friendly settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://frontend:3000",
            "http://localhost:8001",
            "http://127.0.0.1:8001"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )

    # Add logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # Enhanced request logging
        logger.info(f"Incoming request: {request.method} {request.url}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
        response = await call_next(request)
        
        # Ensure JSON content type for API responses
        if request.url.path.startswith("/api/"):
            response.headers["Content-Type"] = "application/json"
        
        duration = time.time() - start_time
        logger.info(
            f"Request completed - Method: {request.method} Path: {request.url.path} "
            f"Status: {response.status_code} Duration: {duration:.2f}s"
        )
        
        return response

    # Add exception handler
    app.middleware("http")(catch_exceptions_middleware)