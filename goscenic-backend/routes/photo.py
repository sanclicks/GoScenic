from fastapi import APIRouter, UploadFile, File, Form
from models.user import PhotoShare
from services.photo_service import save_photo

router = APIRouter()


@router.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...), user_email: str = Form(...)):
    url = save_photo(file, user_email)
    return {"photo_url": url}

