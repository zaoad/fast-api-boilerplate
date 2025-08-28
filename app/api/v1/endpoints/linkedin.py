from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
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
from app.core.auth import get_current_user
from app.schemas.user import User
from app.schemas.linkedin import LinkedInPostCreate, LinkedInPostUpdate

logger = get_logger("app.api.auth")

router = APIRouter(
    prefix="/linkedin",
    tags=["linkedin"],
)

@router.get("/auth/url")
async def linkedin_auth_url(current_user: User = Depends(get_current_user)):
    """
    LinkedIn authentication URL endpoint.
    """
    return await get_linkedin_auth_url()

@router.get("/auth")
async def linkedin_auth(code: str, current_user: User = Depends(get_current_user)):
    """
    LinkedIn authentication endpoint.
    """
    return await get_linkedin_token(code, current_user.id)

@router.get("/me")
async def linkedin_me(current_user: User = Depends(get_current_user)):
    """
    LinkedIn me endpoint.
    """
    return await get_linkedin_me(current_user.id)

@router.post("/posts")
async def linkedin_post_create(post: LinkedInPostCreate, current_user: User = Depends(get_current_user)):
    """
    Create a new LinkedIn post.
    """
    return await create_linkedin_post(post, current_user.id)

@router.post("/upload-image")
async def upload_image(
    image: UploadFile = File(..., description="Image file to upload to LinkedIn"),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an image to LinkedIn and return the image ID.
    """
    image_bytes = await image.read()
    
    image_id = await upload_image_to_linkedin(current_user.id, image_bytes)
    
    return {
        "message": "Image uploaded successfully to LinkedIn",
        "image_id": image_id
    }

@router.put("/posts/{post_id}")
async def linkedin_post_update(post_id: str, post: LinkedInPostUpdate, current_user: User = Depends(get_current_user)):
    """
    Update a LinkedIn post.
    """
    return await update_linkedin_post(post_id, post, current_user.id)

@router.delete("/posts/{post_id}")
async def linkedin_post_delete(post_id: str, current_user: User = Depends(get_current_user)):
    """
    Delete a LinkedIn post.
    """
    return await delete_linkedin_post(post_id, current_user.id)
