from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.middleware import ErrorHandlerMiddleware, RequestLoggingMiddleware
from app.core.logging import setup_logging
from app.api.routes import chat

def create_app() -> FastAPI:
    # Setup logging
    setup_logging(settings.LOG_LEVEL)
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    
    # Add middlewares
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(chat.router, prefix=settings.API_V1_STR)
    
    return app

app = create_app() 