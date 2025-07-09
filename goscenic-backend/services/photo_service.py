from fastapi import UploadFile
import os
from tempfile import NamedTemporaryFile
from services.s3 import upload_file


def save_photo(file: UploadFile, user_email: str) -> str:
    suffix = os.path.splitext(file.filename)[1]
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    key = f"{user_email}/{os.path.basename(tmp_path)}"
    url = upload_file(tmp_path, key)
    os.remove(tmp_path)
    return url

