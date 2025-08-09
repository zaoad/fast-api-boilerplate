from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

_mongo_client: Optional[AsyncIOMotorClient] = None

async def get_mongo_client() -> AsyncIOMotorClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.get_mongo_url())
    return _mongo_client

async def get_mongo_db() -> AsyncIOMotorDatabase:
    client = await get_mongo_client()
    return client.get_default_database()

async def close_mongo() -> None:
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None 