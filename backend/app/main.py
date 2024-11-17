from fastapi import FastAPI
from app.api.routes import chat
from app.api.middleware import setup_middleware
from app.core.config import settings
from app.services.cache import get_cache
import logging

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-agent chat system API"
)

# Setup middleware
setup_middleware(app)

# Include routers
app.include_router(chat.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        # Log API key status (don't log the actual key!)
        logger.info(f"OpenAI API key loaded: {settings.is_valid_openai_key}")
        
        # Initialize cache
        cache = await get_cache()
        app.state.cache = cache
        logger.info("Cache service initialized")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        # Don't raise - allow app to start without cache

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        if hasattr(app.state, 'cache'):
            await app.state.cache.close()
            logger.info("Cache connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}") 