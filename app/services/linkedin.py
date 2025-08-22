import jwt
import requests
import urllib.parse
from sqlalchemy.orm import Session
from app.core.config import settings
from fastapi import HTTPException
from app.models.linkedin import LinkedInToken, LinkedInPost
from app.core.logging import get_logger
from app.schemas.linkedin import LinkedInPostCreate, LinkedInPostUpdate

logger = get_logger("app.services.linkedin")

def get_linkedin_token(code: str, db: Session, user_id: int):
    """
    Get a LinkedIn token using the code.
    """
    url = settings.LINKEDIN_ACCESS_TOKEN_URL
    client_id = settings.LINKEDIN_CLIENT_ID
    client_secret = settings.LINKEDIN_CLIENT_SECRET
    redirect_uri = settings.LINKEDIN_REDIRECT_URI

    logger.info(f"Getting LinkedIn token with code: {code}")
    logger.info(f"URL: {url}")
    logger.info(f"Client ID: {client_id}")
    logger.info(f"Client Secret: {client_secret}")
    logger.info(f"Redirect URI: {redirect_uri}")

    response = requests.post(
        url=url,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get LinkedIn token")

    token_info = response.json()

    db_token = LinkedInToken(
        user_id=user_id,
        access_token=token_info["access_token"],
        expires_in=token_info["expires_in"],
        scope=token_info["scope"],
        token_type=token_info["token_type"],
        id_token=token_info["id_token"],
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return {
        "message": "LinkedIn Token Saved Successfully"
    }

def get_linkedin_me(db: Session, user_id: int):
    """
    Get LinkedIn me endpoint.
    """
    db_token = db.query(LinkedInToken).filter(LinkedInToken.user_id == user_id).order_by(LinkedInToken.id.desc()).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="LinkedIn token not found")

    url = settings.LINKEDIN_USER_INFO_URL
    headers = {
        "Authorization": f"Bearer {db_token.access_token}",
    }

    response = requests.get(
        url=url,
        headers=headers,
    )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get LinkedIn me")

    return {
        "message": "LinkedIn Me Endpoint",
        "data": response.json(),
    }

def get_linkedin_auth_url():
    """
    Get LinkedIn authentication URL.
    """
    return {
        "message": "LinkedIn Authentication URL",
        "url": f"{settings.LINKEDIN_AUTH_URL}?response_type=code&client_id={settings.LINKEDIN_CLIENT_ID}&redirect_uri={settings.LINKEDIN_REDIRECT_URI}&scope={urllib.parse.quote(settings.LINKEDIN_SCOPE)}",
    }

def create_linkedin_post(post: LinkedInPostCreate, db: Session, user_id: int):
    """
    Create a new LinkedIn post.
    """
    db_token = db.query(LinkedInToken).filter(LinkedInToken.user_id == user_id).order_by(LinkedInToken.id.desc()).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="LinkedIn token not found")

    url = settings.LINKEDIN_REST_URL
    headers = {
        "Authorization": f"Bearer {db_token.access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202508"
    }

    linkedin_user_sub = get_user_sub_from_id_token(db_token.id_token)

    linkedin_post_body = {
        "author": f"urn:li:person:{linkedin_user_sub}",
        "commentary": post.text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }
    
    if post.image_id:
        image_urn = f"urn:li:image:{post.image_id}"
        linkedin_post_body["content"] = {
            "media": {
                "altText": "Tags from LinkedInAPI",
                "id": image_urn
            }
        }
    
    response = requests.post(
        url=f"{url}/posts",
        headers=headers,
        json=linkedin_post_body,
    )
    if response.status_code != 201:
        raise HTTPException(status_code=400, detail="Failed to create LinkedIn post")
    
    post_share_urn = response.headers.get("x-restli-id")

    db_post = LinkedInPost(
        user_id=user_id,
        post_id=post_share_urn.split(":")[-1],
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return {
        "message": "LinkedIn Post Created Successfully",
        "linkedin_post_id": post_share_urn.split(":")[-1],
    }

def get_user_sub_from_id_token(id_token: str):
    """
    Get user ID token.
    """
    decoded_token = jwt.decode(id_token, options={"verify_signature": False})
    return decoded_token.get("sub")

def upload_image_to_linkedin(user_id: int, image: bytes, db: Session):
    """
    Upload image to LinkedIn.
    """
    db_token = db.query(LinkedInToken).filter(LinkedInToken.user_id == user_id).order_by(LinkedInToken.id.desc()).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="LinkedIn token not found")
    
    linkedin_user_sub = get_user_sub_from_id_token(db_token.id_token)

    linkedin_token = db_token.access_token

    url = settings.LINKEDIN_REST_URL
    headers = {
        "Authorization": f"Bearer {linkedin_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "image/jpeg",
        "LinkedIn-Version": "202508"
    }

    initiate_image_upload_response = linkedin_image_upload_initiate(linkedin_user_sub, linkedin_token)
    upload_url = initiate_image_upload_response["uploadUrl"]

    response = requests.put(
        url=upload_url,
        headers=headers,
        data=image,
    )

    if response.status_code != 201:
        raise HTTPException(status_code=400, detail="Failed to upload image to LinkedIn")

    return initiate_image_upload_response["image"].split(":")[-1]

def linkedin_image_upload_initiate(sub: str, linkedin_token: str):
    """
    Initiate image upload to LinkedIn.
    """
    url = settings.LINKEDIN_REST_URL
    headers = {
        "Authorization": f"Bearer {linkedin_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202508"
    }

    body = {
        "initializeUploadRequest": {
            "owner": f"urn:li:person:{sub}"
        }
    }

    response = requests.post(
        url=f"{url}/images?action=initializeUpload",
        headers=headers,
        json=body,
    )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to Initiate upload image to LinkedIn")
    
    return response.json()["value"]

def update_linkedin_post(post_id: str, post_update: LinkedInPostUpdate, db: Session, user_id: int):
    """
    Update a LinkedIn post.
    """
    db_token = db.query(LinkedInToken).filter(LinkedInToken.user_id == user_id).order_by(LinkedInToken.id.desc()).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="LinkedIn token not found")
    
    post = db.query(LinkedInPost).filter(
            LinkedInPost.user_id == user_id,
            LinkedInPost.post_id == post_id,
            LinkedInPost.is_deleted == False
        ).first()
    if not post:
        raise HTTPException(status_code=404, detail="LinkedIn post does not exist for this user")

    url = settings.LINKEDIN_REST_URL
    headers = {
        "Authorization": f"Bearer {db_token.access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202508"
    }
    body = {
        "patch": {
            "$set": {"commentary": post_update.text, "contentCallToActionLabel": "LEARN_MORE"},
            "adContext": {"$set": {"dscName": "Updating Post"}},
        }
    }
    response = requests.post(
        url=f"{url}/posts/{urllib.parse.quote(f'urn:li:share:{post_id}')}",
        headers=headers,
        json=body,
    )
    if response.status_code != 204:
        raise HTTPException(status_code=400, detail="Failed to update LinkedIn post")
    
    return {
        "message": "LinkedIn Post Updated Successfully",
    }

def delete_linkedin_post(post_id: str, db: Session, user_id: int):
    """
    Delete a LinkedIn post.
    """
    db_token = db.query(LinkedInToken).filter(LinkedInToken.user_id == user_id).order_by(LinkedInToken.id.desc()).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="LinkedIn token not found")
    
    post = db.query(LinkedInPost).filter(
        LinkedInPost.user_id == user_id,
        LinkedInPost.post_id == post_id,
        LinkedInPost.is_deleted == False
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="LinkedIn post does not exist for this user")

    url = settings.LINKEDIN_REST_URL
    headers = {
        "Authorization": f"Bearer {db_token.access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202508"
    }

    response = requests.delete(
        url=f"{url}/posts/{urllib.parse.quote(f'urn:li:share:{post_id}')}",
        headers=headers,
    )
    if response.status_code != 204:
        raise HTTPException(status_code=400, detail="Failed to delete LinkedIn post")

    post.is_deleted = True
    db.commit()
    db.refresh(post)
    
    return {
        "message": "LinkedIn Post Deleted Successfully",
    }