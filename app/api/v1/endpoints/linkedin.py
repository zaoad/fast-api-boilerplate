from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.logging import get_logger
from app.services.linkedin import (
    get_linkedin_token,
    get_linkedin_me,
    get_linkedin_auth_url,
    create_linkedin_post,
    update_linkedin_post,
    delete_linkedin_post,
    upload_image_to_linkedin,
)
from app.db.base import get_db
from app.core.security import get_current_active_user
from app.schemas.user import User
from app.schemas.linkedin import LinkedInPostCreate, LinkedInPostUpdate

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


@router.post("/posts")
def linkedin_post_create(post: LinkedInPostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Create a new LinkedIn post.
    """
    return create_linkedin_post(post, db, current_user.id)


@router.post("/upload-image")
async def upload_image(
    image: UploadFile = File(..., description="Image file to upload to LinkedIn"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload an image to LinkedIn and return the image ID.
    """
    image_bytes = await image.read()
    
    image_id = upload_image_to_linkedin(current_user.id, image_bytes, db)
    
    return {
        "message": "Image uploaded successfully to LinkedIn",
        "image_id": image_id
    }


@router.put("/posts/{post_id}")
def linkedin_post_update(post_id: str, post: LinkedInPostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Update a LinkedIn post.
    """
    return update_linkedin_post(post_id, post, db, current_user.id)

@router.delete("/posts/{post_id}")
def linkedin_post_delete(post_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Delete a LinkedIn post.
    """
    return delete_linkedin_post(post_id, db, current_user.id)
