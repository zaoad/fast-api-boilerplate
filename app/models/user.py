from beanie import Document, Indexed
from pydantic import EmailStr
from typing import Optional
from datetime import datetime

class User(Document):
    email: Indexed(EmailStr, unique=True)  # Indexed field for email
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None

    class Settings:
        name = "users"  # Collection name in MongoDB
        use_state_management = True  # Enable Beanie's state management

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "is_active": True,
                "is_superuser": False
            }
        }