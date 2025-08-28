from typing import Optional, List
from datetime import datetime
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

async def get_user(id: str) -> Optional[User]:
    """Get a user by ID."""
    return await User.get(id)

async def get_user_by_email(email: str) -> Optional[User]:
    """Get a user by email."""
    return await User.find_one({"email": email})

async def get_users(skip: int = 0, limit: int = 100) -> List[User]:
    """Get a list of users with pagination."""
    users = await User.find_all().skip(skip).limit(limit).to_list()
    return users

async def create_user(user: UserCreate) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=datetime.utcnow()
    )
    await db_user.insert()
    return db_user

async def update_user(id: str, user: UserUpdate) -> Optional[User]:
    """Update a user's information."""
    db_user = await get_user(id)
    if not db_user:
        return None
    
    # Get dict of values that are set (not None)
    update_data = {k: v for k, v in user.dict().items() if v is not None}
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    update_data["updated_at"] = datetime.utcnow()
    
    await db_user.set(update_data)
    return db_user

async def delete_user(id: str) -> bool:
    """Delete a user."""
    db_user = await get_user(id)
    if not db_user:
        return False
    await db_user.delete()
    return True 