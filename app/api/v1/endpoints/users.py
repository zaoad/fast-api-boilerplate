from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user import (
    get_user,
    get_users,
    create_user,
    update_user,
    delete_user,
    get_user_by_email,
)
from app.core.logging import get_logger
from app.core.auth import get_current_active_user, get_current_superuser

logger = get_logger("app.api.users")

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[User], summary="Get all users")
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser)  # Only superusers can list all users
):
    """
    Retrieve a list of users with pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    
    Note: This endpoint requires superuser privileges.
    """
    logger.info(f"Fetching users with skip={skip}, limit={limit}")
    
    users = await get_users(skip=skip, limit=limit)
    logger.info(f"Found {len(users)} users")
    return users

@router.post("/", response_model=User, summary="Create new user", status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user: UserCreate,
    current_user: User = Depends(get_current_superuser)  # Only superusers can create users directly
):
    """
    Create a new user.
    
    - **email**: User's email address
    - **password**: User's password
    - **is_active**: Whether the user is active (default: True)
    - **is_superuser**: Whether the user has superuser privileges (default: False)
    
    Note: This endpoint requires superuser privileges. For regular user registration, use the /auth/signup endpoint.
    """
    logger.info(f"Creating new user with email={user.email}")
    
    existing_user = await get_user_by_email(email=user.email)
    if existing_user:
        logger.warning(f"Email already registered: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = await create_user(user=user)
    logger.info(f"User created successfully with id={new_user.id}")
    return new_user

@router.get("/me", response_model=User, summary="Get current user")
async def read_user_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    
    Returns the current authenticated user's details.
    """
    logger.info(f"User {current_user.email} requested their profile")
    return current_user

@router.get("/{user_id}", response_model=User, summary="Get user by ID")
async def read_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific user by their ID.
    
    - **user_id**: The ID of the user to retrieve
    
    Note: Regular users can only view their own profile. Superusers can view any profile.
    """
    logger.info(f"Fetching user by ID={user_id}")
    
    # Check if user is trying to access their own profile or is a superuser
    if user_id != str(current_user.id) and not current_user.is_superuser:
        logger.warning(f"Access denied: User {current_user.id} attempted to access profile of user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this profile"
        )
    
    user = await get_user(id=user_id)
    if user is None:
        logger.warning(f"User not found: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"User found: id={user_id}")
    return user

@router.put("/{user_id}", response_model=User, summary="Update user")
async def update_user_endpoint(
    user_id: str,
    user: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a user's information.
    
    - **user_id**: The ID of the user to update
    - **email**: New email address (optional)
    - **password**: New password (optional)
    - **is_active**: New active status (optional)
    - **is_superuser**: New superuser status (optional)
    
    Note: Regular users can only update their own profile and cannot modify is_active or is_superuser.
    Superusers can update any profile with all fields.
    """
    logger.info(f"Updating user with id={user_id}")
    
    # Check if user is trying to update their own profile or is a superuser
    if user_id != str(current_user.id) and not current_user.is_superuser:
        logger.warning(f"Access denied: User {current_user.id} attempted to update profile of user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this profile"
        )
    
    # If not superuser, prevent modifying is_active and is_superuser
    if not current_user.is_superuser:
        if user.is_active is not None or user.is_superuser is not None:
            logger.warning(f"Access denied: User {current_user.id} attempted to modify privileged fields")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to modify these fields"
            )
    
    updated_user = await update_user(id=user_id, user=user)
    if updated_user is None:
        logger.warning(f"User not found for update: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"User updated successfully: id={user_id}")
    return updated_user

@router.delete("/{user_id}", summary="Delete user")
async def delete_user_endpoint(
    user_id: str,
    current_user: User = Depends(get_current_superuser)  # Only superusers can delete users
):
    """
    Delete a user by their ID.
    
    - **user_id**: The ID of the user to delete
    
    Note: This endpoint requires superuser privileges.
    """
    logger.info(f"Deleting user with id={user_id}")
    
    success = await delete_user(id=user_id)
    if not success:
        logger.warning(f"User not found for deletion: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"User deleted successfully: id={user_id}")
    return {"message": "User deleted successfully"} 