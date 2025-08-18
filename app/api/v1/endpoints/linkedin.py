from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.logging import get_logger
from app.services.linkedin import get_linkedin_token, get_linkedin_me, get_linkedin_auth_url
from app.db.base import get_db
from app.core.security import get_current_active_user
from app.models.user import User

logger = get_logger("app.api.auth")

router = APIRouter(
    prefix="/linkedin",
    tags=["linkedin"],
)

@router.get("/auth/url")
def linkedin_auth_url(current_user: User = Depends(get_current_active_user)):
    """
    LinkedIn authentication URL endpoint.
    """
    return get_linkedin_auth_url()

@router.get("/auth")
def linkedin_auth(code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    LinkedIn authentication endpoint.
    """

    return get_linkedin_token(code, db, current_user.id)

@router.get("/me")
def linkedin_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    LinkedIn me endpoint.
    """
    return get_linkedin_me(db, current_user.id)