from typing import Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from app.core.logging import get_logger
from app.core.security import decode_jwt
from app.schemas.user import User
from app.services.user import get_user

logger = get_logger("app.core.auth")

async def get_current_user(
    credential: Union[HTTPAuthorizationCredentials, None] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> User:
    """Get the current user from the database based on the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication required. Please pass bearer token in the authorization header.",
            headers={"WWW-Authenticate": 'Bearer realm="auth_required"'},
        )
    try:
        payload = decode_jwt(credential.credentials)
        if payload is None:
            raise credentials_exception
        user_id: str = payload.get("sub")
    except JWTError:
        raise credentials_exception
    
    user = await get_user(id=user_id)
    if user is None:
        raise credentials_exception
    
    return User(
        id=str(user.id),
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser
    )

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current user and verify that they are active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current user and verify that they are a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not enough permissions"
        )
    return current_user
