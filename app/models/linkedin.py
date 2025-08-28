from datetime import datetime
from typing import Optional
from beanie import Document

class LinkedInToken(Document):
    user_id: str
    access_token: str
    expires_in: int
    scope: str
    token_type: str
    id_token: str
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None

    class Settings:
        name = "linkedin_tokens"
        use_state_management = True

class LinkedInPost(Document):
    user_id: str
    post_id: str
    is_deleted: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None

    class Settings:
        name = "linkedin_posts"
        use_state_management = True