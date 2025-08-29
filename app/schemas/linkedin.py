from typing import Optional
from pydantic import BaseModel, Field


class LinkedInPostCreate(BaseModel):
    """LinkedIn post creation model with optional image."""
    text: str = Field(..., description="The text content of the LinkedIn post", min_length=1, max_length=3000)
    image_id: Optional[str] = Field(None, description="Optional image ID for the post")

class LinkedInPostUpdate(BaseModel):
    """LinkedIn post update model with all fields optional."""
    text: str = Field(None, description="The text content of the LinkedIn post", min_length=1, max_length=3000)

class LinkedInTaskRequest(BaseModel):
    task_type: str
    data: dict

class TaskResponse(BaseModel):
    task_id: str
    message: str