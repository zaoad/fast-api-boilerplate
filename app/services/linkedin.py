import requests
import urllib.parse
from sqlalchemy.orm import Session
from app.core.config import settings
from fastapi import HTTPException
from app.models.linkedin import LinkedInToken
from app.core.logging import get_logger

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
    db_token = db.query(LinkedInToken).filter(LinkedInToken.user_id == user_id).first()
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