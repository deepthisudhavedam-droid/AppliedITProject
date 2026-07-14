import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import app


def test_analyze_image_route_is_registered():
    client = TestClient(app)
    response = client.post("/analyze-image")

    assert response.status_code == 422