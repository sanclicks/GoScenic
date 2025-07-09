from typing import Dict
from models.user import UserProfile

# In-memory storage for demo purposes
USERS: Dict[str, UserProfile] = {}


def create_user(profile: UserProfile) -> UserProfile:
    USERS[profile.email] = profile
    return profile


def get_user(email: str) -> UserProfile | None:
    return USERS.get(email)

