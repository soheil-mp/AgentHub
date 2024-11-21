from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect(cls):
        """Connect to MongoDB."""
        try:
            # Log connection URL (remove password for security)
            url = settings.MONGODB_URL
            safe_url = url.replace(url.split('@')[0].split('://')[-1], '***:***')
            logger.debug(f"Attempting MongoDB connection with URL: {safe_url}")
            
            # Create client with authentication
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            
            # Verify connection and authentication
            await cls.client.admin.command('ping')
            logger.info(f"Connected to MongoDB database: {settings.MONGODB_DB_NAME}")
            
            # Log database info
            server_info = await cls.client.server_info()
            logger.debug(f"MongoDB server version: {server_info.get('version')}")
            
        except Exception as e:
            logger.error(f"MongoDB connection error: {str(e)}")
            raise

    @classmethod
    async def close(cls):
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("Closed MongoDB connection")

    @classmethod
    async def get_db(cls):
        """Get database instance."""
        if not cls.db:
            await cls.connect()
        return cls.db

async def get_db() -> AsyncIOMotorClient:
    """Dependency for FastAPI endpoints."""
    try:
        # Log connection attempt
        logger.debug("Attempting to create MongoDB client")
        
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # Test connection
        logger.debug("Testing MongoDB connection")
        await client.admin.command('ping')
        logger.debug("MongoDB connection successful")
        
        try:
            yield client
        finally:
            logger.debug("Closing MongoDB client")
            client.close()
            
    except Exception as e:
        logger.error(f"MongoDB connection error in get_db: {str(e)}")
        raise

mongodb = MongoDB() 