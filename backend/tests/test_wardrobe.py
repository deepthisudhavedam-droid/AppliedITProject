import io
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

sys.path.append(str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test_wardrobe.db")
    monkeypatch.setenv("WARDROBE_UPLOAD_ROOT", str(tmp_path / "uploads"))

    import database.connection as connection_module
    import main as main_module

    connection_module.engine = None
    connection_module.SessionLocal = None

    from database.connection import Base, init_db

    db_path = Path("test_wardrobe.db")
    if db_path.exists():
        db_path.unlink()

    init_db()
    yield
    Base.metadata.drop_all(bind=connection_module.engine)


from main import app


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def create_test_image_bytes(format_name: str = "PNG") -> bytes:
    image = Image.new("RGB", (120, 90), color="red")
    buffer = io.BytesIO()
    image.save(buffer, format=format_name)
    return buffer.getvalue()


def test_upload_and_access_wardrobe_item(client: TestClient):
    register_response = client.post(
        "/register",
        json={"username": "wardrobeuser", "email": "wardrobe@example.com", "password": "secret123"},
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/login",
        json={"email": "wardrobe@example.com", "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    image_bytes = create_test_image_bytes("PNG")
    upload_response = client.post(
        "/wardrobe/items",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("sample.png", image_bytes, "image/png")},
        data={"category": "tops", "color": "red", "notes": "test item"},
    )

    assert upload_response.status_code == 200, upload_response.text
    payload = upload_response.json()
    assert payload["stored_filename"].endswith(".png")
    assert payload["image_url"].startswith("/wardrobe/items/")
    assert payload["thumbnail_url"].startswith("/wardrobe/items/")

    list_response = client.get("/wardrobe/items", headers={"Authorization": f"Bearer {token}"})
    assert list_response.status_code == 200
    items = list_response.json()
    assert len(items) == 1

    item_id = payload["id"]
    detail_response = client.get(f"/wardrobe/items/{item_id}", headers={"Authorization": f"Bearer {token}"})
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == item_id

    image_response = client.get(f"/wardrobe/items/{item_id}/image", headers={"Authorization": f"Bearer {token}"})
    assert image_response.status_code == 200
    assert image_response.headers["content-type"].startswith("image/")

    thumbnail_response = client.get(f"/wardrobe/items/{item_id}/thumbnail", headers={"Authorization": f"Bearer {token}"})
    assert thumbnail_response.status_code == 200
    assert thumbnail_response.headers["content-type"].startswith("image/")

    delete_response = client.delete(f"/wardrobe/items/{item_id}", headers={"Authorization": f"Bearer {token}"})
    assert delete_response.status_code == 200

    missing_response = client.get(f"/wardrobe/items/{item_id}", headers={"Authorization": f"Bearer {token}"})
    assert missing_response.status_code == 404
