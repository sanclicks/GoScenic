from pydantic import BaseModel, EmailStr
from typing import Optional

class UserProfile(BaseModel):
    email: EmailStr
    instagram_username: Optional[str] = None
    apple_id: Optional[str] = None
    full_name: Optional[str] = None

class PhotoShare(BaseModel):
    user_email: EmailStr
    photo_url: str
    caption: Optional[str] = None
    shared_with: Optional[str] = None  # email of another user

