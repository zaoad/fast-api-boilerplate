from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """Base user model with shared attributes."""
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

class UserCreate(UserBase):
    """User creation model with password."""
    password: str

class UserUpdate(BaseModel):
    """User update model with all fields optional."""
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserInDBBase(UserBase):
    """User model as stored in DB, with ID."""
    id: int

    class Config:
        from_attributes = True

class User(UserInDBBase):
    """User model for API responses."""
    pass

class UserInDB(UserInDBBase):
    """User model with hashed password for internal use."""
    hashed_password: str 