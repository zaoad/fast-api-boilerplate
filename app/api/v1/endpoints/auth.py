from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password
from app.core.auth import get_current_user
from app.core.config import settings
from app.schemas.auth import Token, Login, SignupResponse
from app.schemas.user import UserCreate, User
from app.services.user import get_user_by_email, create_user
from app.core.logging import get_logger

logger = get_logger("app.api.auth")

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

@router.post("/login", response_model=Token)
async def login(
    login_data: Login,
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    logger.info(f"Login attempt for user with email: {login_data.email}")
    
    user = await get_user_by_email(login_data.email)
    if not user:
        logger.warning(f"Login failed: User with email {login_data.email} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not verify_password(login_data.password, user.hashed_password):
        logger.warning(f"Login failed: Invalid password for user {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )
    
    logger.info(f"User {login_data.email} successfully logged in")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/oauth", response_model=Token)
async def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    OAuth2 compatible token login using form, get an access token for future requests.
    This endpoint is primarily for Swagger UI authentication.
    """
    logger.info(f"OAuth login attempt for user with username: {form_data.username}")
    
    user = get_user_by_email(email=form_data.username)
    if not user:
        logger.warning(f"OAuth login failed: User with email {form_data.username} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"OAuth login failed: Invalid password for user {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )
    
    logger.info(f"User {form_data.username} successfully logged in via OAuth")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
):
    """
    Create a new user account.
    """
    logger.info(f"Signup attempt for user with email: {user_data.email}")
    
    # Check if user already exists
    user = await get_user_by_email(email=user_data.email)

    if user:
        logger.warning(f"Signup failed: User with email {user_data.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    user = await create_user(user=user_data)
    
    logger.info(f"User {user_data.email} successfully registered with ID: {str(user.id)}")
    return {"message": "User created successfully", "user_id": str(user.id)}

@router.get("/me", response_model=User)
async def read_current_user(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.
    """
    logger.info(f"User {current_user.email} requested their profile")
    return current_user 