from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict, Any, List
import logging
import backoff
from datetime import datetime
from app.core.config import settings
from app.core.logging_config import mongodb_logger
from pymongo.errors import (
    ConnectionFailure, 
    OperationFailure, 
    ServerSelectionTimeoutError
)

class MongoDB:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.logger = mongodb_logger
        self._connection_params = self._get_connection_params()

    def _get_connection_params(self) -> Dict[str, Any]:
        """Get MongoDB connection parameters with optimal settings."""
        return {
            "maxPoolSize": 50,
            "minPoolSize": 10,
            "maxIdleTimeMS": 300000,
            "waitQueueTimeoutMS": 10000,
            "connectTimeoutMS": 5000,
            "serverSelectionTimeoutMS": 5000,
            "socketTimeoutMS": 5000,
            "retryWrites": True,
            "retryReads": True,
            "w": "majority",
            "readPreference": "primaryPreferred",
            "readConcernLevel": "majority"
        }

    @backoff.on_exception(
        backoff.expo,
        (ConnectionFailure, ServerSelectionTimeoutError, OperationFailure),
        max_tries=5,
        max_time=30
    )
    async def connect(self):
        """Connect to MongoDB with retries and connection pooling."""
        try:
            if self.client:
                return
                
            self.logger.info("Attempting to connect to MongoDB...")
            
            # Use Docker service name for MongoDB host
            mongodb_host = settings.MONGODB_HOST
            self.logger.info(f"Using MongoDB host: {mongodb_host}")
            
            # Connect with application user
            app_url = (
                f"mongodb://{settings.MONGODB_USER}:{settings.MONGODB_PASSWORD}@"
                f"{mongodb_host}:{settings.MONGODB_PORT}/"
                f"{settings.MONGODB_DB_NAME}?authSource=admin"
            )
            
            # Log connection attempt (without password)
            safe_url = app_url.replace(settings.MONGODB_PASSWORD, "***")
            self.logger.info(f"Using connection URL: {safe_url}")
            
            self.client = AsyncIOMotorClient(
                app_url,
                **self._connection_params
            )
            
            # Test connection
            await self.client.admin.command('ping')
            self.logger.info("Successfully connected to MongoDB")
            
            self.db = self.client[settings.MONGODB_DB_NAME]
            server_info = await self.client.server_info()
            self.logger.info(f"Connected to MongoDB {server_info.get('version')}")
            
            # Verify database access
            await self.db.command('ping')
            self.logger.info(f"Successfully accessed database: {settings.MONGODB_DB_NAME}")
            
            await self._ensure_indexes()
            
        except Exception as e:
            self.logger.error(
                f"MongoDB connection error: {str(e)}\n"
                f"Host: {mongodb_host}\n"
                f"Port: {settings.MONGODB_PORT}\n"
                f"Database: {settings.MONGODB_DB_NAME}\n"
                f"User: {settings.MONGODB_USER}",
                exc_info=True
            )
            raise

    async def _ensure_app_user(self):
        """Ensure application user exists."""
        try:
            admin_db = self.client.admin
            users = await admin_db.command("usersInfo")
            
            app_user_exists = any(
                user["user"] == settings.MONGODB_USER 
                for user in users.get("users", [])
            )
            
            if not app_user_exists:
                await admin_db.command(
                    "createUser",
                    settings.MONGODB_USER,
                    pwd=settings.MONGODB_PASSWORD,
                    roles=[
                        {"role": "readWrite", "db": settings.MONGODB_DB_NAME},
                        {"role": "dbAdmin", "db": settings.MONGODB_DB_NAME}
                    ]
                )
                self.logger.info(f"Created application user: {settings.MONGODB_USER}")
            else:
                self.logger.info(f"Application user {settings.MONGODB_USER} already exists")
        except Exception as e:
            self.logger.error(f"Error ensuring application user: {str(e)}")
            raise

    async def _ensure_indexes(self):
        """Create and verify necessary indexes."""
        try:
            # Define index configurations
            index_configs = {
                "users": [
                    {"keys": [("email", 1)], "unique": True},
                    {"keys": [("created_at", 1)]}
                ],
                "conversations": [
                    {"keys": [("user_id", 1), ("started_at", -1)]},
                    {"keys": [("ended_at", 1)]}
                ],
                "messages": [
                    {"keys": [("conversation_id", 1), ("created_at", 1)]},
                    {"keys": [("created_at", 1)]}
                ],
                "flight_bookings": [
                    {"keys": [("user_id", 1)]},
                    {"keys": [("booking_reference", 1)], "unique": True},
                    {"keys": [("created_at", 1)]}
                ],
                "hotel_bookings": [
                    {"keys": [("user_id", 1)]},
                    {"keys": [("booking_reference", 1)], "unique": True},
                    {"keys": [("check_in_date", 1)]}
                ],
                "car_rentals": [
                    {"keys": [("user_id", 1)]},
                    {"keys": [("booking_reference", 1)], "unique": True},
                    {"keys": [("pickup_time", 1)]}
                ],
                "excursions": [
                    {"keys": [("user_id", 1)]},
                    {"keys": [("booking_reference", 1)], "unique": True},
                    {"keys": [("activity_date", 1)]}
                ]
            }

            for collection, indexes in index_configs.items():
                for index in indexes:
                    await self.db[collection].create_index(
                        index["keys"],
                        unique=index.get("unique", False),
                        background=True
                    )

            self.logger.info("MongoDB indexes verified")
        except Exception as e:
            self.logger.error(f"Error ensuring indexes: {str(e)}")
            raise

    async def disconnect(self):
        """Safely close MongoDB connection."""
        if self.client:
            await self.client.close()
            self.client = None
            self.db = None
            self.logger.info("MongoDB connection closed")

    async def check_health(self) -> Dict[str, Any]:
        """Enhanced health check with detailed status."""
        try:
            if not self.client:
                return {"status": "disconnected"}
                
            start_time = datetime.utcnow()
            await self.client.admin.command('ping')
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            server_info = await self.client.server_info()
            server_status = await self.client.admin.command('serverStatus')
            
            return {
                "status": "connected",
                "version": server_info.get('version'),
                "latency_ms": round(latency, 2),
                "connections": server_status.get('connections', {}),
                "operations": server_status.get('opcounters', {}),
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        return await self.db.users.find_one({"email": email})

    async def get_user_conversations(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's conversations with pagination."""
        cursor = self.db.conversations.find(
            {"user_id": user_id}
        ).sort("started_at", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        """Get all messages for a conversation."""
        cursor = self.db.messages.find(
            {"conversation_id": conversation_id}
        ).sort("created_at", 1)
        return await cursor.to_list(length=None)

    async def get_user_bookings(self, user_id: str, booking_type: str) -> List[Dict]:
        """Get user's bookings of a specific type."""
        collection_map = {
            "flight": "flight_bookings",
            "hotel": "hotel_bookings",
            "car": "car_rentals",
            "excursion": "excursions"
        }
        collection = collection_map.get(booking_type)
        if not collection:
            raise ValueError(f"Invalid booking type: {booking_type}")
            
        cursor = self.db[collection].find(
            {"user_id": user_id}
        ).sort("created_at", -1)
        return await cursor.to_list(length=None)

    async def get_booking_by_reference(self, booking_reference: str) -> Optional[Dict]:
        """Find a booking by reference across all booking collections."""
        booking_collections = [
            "flight_bookings",
            "hotel_bookings",
            "car_rentals",
            "excursions"
        ]
        
        for collection in booking_collections:
            booking = await self.db[collection].find_one(
                {"booking_reference": booking_reference}
            )
            if booking:
                booking["booking_type"] = collection.replace("_bookings", "").replace("_", "")
                return booking
        return None

    async def create_conversation(self, user_id: str) -> str:
        """Create a new conversation and return its ID."""
        result = await self.db.conversations.insert_one({
            "user_id": user_id,
            "started_at": datetime.utcnow(),
            "metadata": {}
        })
        return str(result.inserted_id)

    async def add_message(self, conversation_id: str, role: str, content: str) -> Dict:
        """Add a message to a conversation."""
        message = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "created_at": datetime.utcnow(),
            "metadata": {}
        }
        await self.db.messages.insert_one(message)
        return message

    async def end_conversation(self, conversation_id: str) -> bool:
        """End a conversation by setting its end time."""
        result = await self.db.conversations.update_one(
            {"_id": conversation_id},
            {"$set": {"ended_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def create_booking(self, booking_type: str, booking_data: Dict) -> str:
        """Create a new booking of specified type."""
        collection_map = {
            "flight": "flight_bookings",
            "hotel": "hotel_bookings",
            "car": "car_rentals",
            "excursion": "excursions"
        }
        collection = collection_map.get(booking_type)
        if not collection:
            raise ValueError(f"Invalid booking type: {booking_type}")
            
        booking_data.update({
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        result = await self.db[collection].insert_one(booking_data)
        return str(result.inserted_id)

    async def update_booking_status(
        self, 
        booking_type: str, 
        booking_reference: str, 
        status: str
    ) -> bool:
        """Update booking status."""
        collection_map = {
            "flight": "flight_bookings",
            "hotel": "hotel_bookings",
            "car": "car_rentals",
            "excursion": "excursions"
        }
        collection = collection_map.get(booking_type)
        if not collection:
            raise ValueError(f"Invalid booking type: {booking_type}")
            
        result = await self.db[collection].update_one(
            {"booking_reference": booking_reference},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0

mongodb = MongoDB() 