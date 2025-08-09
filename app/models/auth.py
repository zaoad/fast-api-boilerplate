from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    """Token payload model for decoding JWT."""
    sub: Optional[int] = None
    exp: Optional[int] = None

class Login(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str

class SignupResponse(BaseModel):
    """Response model for successful signup."""
    message: str
    user_id: int 