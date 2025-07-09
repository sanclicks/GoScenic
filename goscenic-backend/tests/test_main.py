import os
import sys
from fastapi.testclient import TestClient

# Ensure environment variables so config endpoint returns true values
os.environ.setdefault("GOOGLE_API_KEY", "test")
os.environ.setdefault("OPENWEATHER_API_KEY", "test")
os.environ.setdefault("GAS_API_KEY", "test")
os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_S3_BUCKET", "test-bucket")

# Add backend directory to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the GoScenic API!"}


def test_get_config():
    response = client.get("/config")
    assert response.status_code == 200
    assert response.json() == {
        "GoogleAPI": True,
        "OpenWeatherAPI": True,
        "GasAPI": True,
    }


def test_create_profile():
    payload = {"email": "test@example.com", "full_name": "Tester"}
    response = client.post("/api/profile", json=payload)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_upload_photo(monkeypatch, tmp_path):
    def mock_upload_file(file_path: str, key: str) -> str:
        return f"https://bucket/{key}"

    monkeypatch.setattr("services.photo_service.upload_file", mock_upload_file)

    temp_file = tmp_path / "pic.jpg"
    temp_file.write_bytes(b"data")

    with open(temp_file, "rb") as f:
        response = client.post(
            "/api/upload-photo",
            files={"file": ("pic.jpg", f, "image/jpeg")},
            data={"user_email": "test@example.com"},
        )

    assert response.status_code == 200
    assert response.json()["photo_url"].startswith("https://bucket/")


