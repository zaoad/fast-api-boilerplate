from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from typing import Optional
from app.models.user import User
from app.models.linkedin import LinkedInToken, LinkedInPost

_mongo_client: Optional[AsyncIOMotorClient] = None

async def init_mongodb():
    """Initialize MongoDB connection and Beanie ODM."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.get_database_url())
        await init_beanie(
            database=_mongo_client[settings.MONGODB_DB],
            document_models=[User, LinkedInToken, LinkedInPost]  # Add all your document models here
        )