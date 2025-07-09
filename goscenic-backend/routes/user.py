from fastapi import APIRouter
from models.user import UserProfile
from services.user_service import create_user, get_user

router = APIRouter()


@router.post("/profile")
async def create_profile(profile: UserProfile):
    created = create_user(profile)
    return created


@router.get("/profile/{email}")
async def get_profile(email: str):
    user = get_user(email)
    if user:
        return user
    return {"error": "User not found"}

