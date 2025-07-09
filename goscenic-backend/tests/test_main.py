import os
import sys
from fastapi.testclient import TestClient

# Ensure environment variables so config endpoint returns true values
os.environ.setdefault("GOOGLE_API_KEY", "test")
os.environ.setdefault("OPENWEATHER_API_KEY", "test")
os.environ.setdefault("GAS_API_KEY", "test")
os.environ.setdefault("OPENAI_API_KEY", "test")

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

