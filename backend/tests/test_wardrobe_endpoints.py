import os
import io
import sys
import json
import tempfile
import shutil
import types
from pathlib import Path

import pytest


def _inject_dummy_ml_modules():
    """Inject lightweight stubs for heavy ML libs before importing app modules."""
    if 'torch' not in sys.modules:
        torch = types.SimpleNamespace()
        cuda = types.SimpleNamespace(is_available=lambda: False)
        def no_grad():
            class Ctx:
                def __enter__(self):
                    return None
                def __exit__(self, exc_type, exc, tb):
                    return False
            return Ctx()
        torch.cuda = cuda
        torch.no_grad = no_grad
        sys.modules['torch'] = torch

    if 'open_clip' not in sys.modules:
        open_clip = types.SimpleNamespace()
        def create_model_and_transforms(*args, **kwargs):
            # return dummy model, _, dummy preprocess
            model = types.SimpleNamespace(encode_image=lambda x: None, encode_text=lambda x: None)
            return model, None, (lambda img: img)
        def get_tokenizer(*args, **kwargs):
            return lambda labels: labels
        open_clip.create_model_and_transforms = create_model_and_transforms
        open_clip.get_tokenizer = get_tokenizer
        sys.modules['open_clip'] = open_clip


@pytest.fixture(autouse=True)
def isolate_env(tmp_path, monkeypatch):
    # Create temp DB and upload root
    db_path = tmp_path / "test_db.sqlite"
    upload_root = tmp_path / "uploads"
    upload_root.mkdir()

    monkeypatch.setenv('DATABASE_URL', f"sqlite:///{db_path}")
    monkeypatch.setenv('WARDROBE_UPLOAD_ROOT', str(upload_root))

    # Stub heavy ML modules so importing analyze/router doesn't import large deps
    _inject_dummy_ml_modules()

    # Import app after env is configured
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from main import app
    # Initialize DB schema
    from database.connection import init_db
    init_db()

    yield {
        'app': app,
        'db_path': db_path,
        'upload_root': upload_root,
    }


def _make_png_bytes():
    # small valid PNG via Pillow when available
    try:
        from PIL import Image
        img = Image.new('RGB', (4, 4), color=(255, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
    except Exception:
        return b'\x89PNG\r\n\x1a\n'


def register_user_and_token(client, username, email, password='secret'):
    # Use register/login flow to get a token for realism
    r = client.post('/register', json={'username': username, 'email': email, 'password': password})
    assert r.status_code == 200
    r = client.post('/login', json={'email': email, 'password': password})
    assert r.status_code == 200
    data = r.json()
    return data['access_token']


def test_upload_requires_auth(isolate_env):
    from fastapi.testclient import TestClient
    client = TestClient(isolate_env['app'])

    files = {'file': ('a.png', b'notimage', 'image/png')}
    r = client.post('/wardrobe/items', files=files)
    assert r.status_code == 401


def test_list_requires_auth(isolate_env):
    from fastapi.testclient import TestClient
    client = TestClient(isolate_env['app'])
    r = client.get('/wardrobe/items')
    assert r.status_code == 401


def test_valid_image_upload_and_listing(isolate_env):
    from fastapi.testclient import TestClient
    client = TestClient(isolate_env['app'])

    token = register_user_and_token(client, 'u1', 'u1@example.com')

    png = _make_png_bytes()
    files = {'file': ('good.png', png, 'image/png')}
    r = client.post('/wardrobe/items', files=files, headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    item = r.json()
    assert 'id' in item

    # list
    r = client.get('/wardrobe/items', headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    items = r.json()
    assert any(i['id'] == item['id'] for i in items)


def test_invalid_mime_type(isolate_env):
    from fastapi.testclient import TestClient
    client = TestClient(isolate_env['app'])
    token = register_user_and_token(client, 'u2', 'u2@example.com')

    files = {'file': ('file.txt', b'hello', 'text/plain')}
    r = client.post('/wardrobe/items', files=files, headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 400


def test_fake_image_with_image_extension(isolate_env):
    from fastapi.testclient import TestClient
    client = TestClient(isolate_env['app'])
    token = register_user_and_token(client, 'u3', 'u3@example.com')

    files = {'file': ('fake.png', b'this is not an image', 'image/png')}
    r = client.post('/wardrobe/items', files=files, headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 400


def test_oversized_upload(isolate_env):
    from fastapi.testclient import TestClient
    client = TestClient(isolate_env['app'])
    token = register_user_and_token(client, 'u4', 'u4@example.com')

    # Create payload larger than MAX_FILE_SIZE (10MB)
    big = b'a' * (10 * 1024 * 1024 + 1)
    files = {'file': ('big.png', big, 'image/png')}
    r = client.post('/wardrobe/items', files=files, headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 413


def test_user_specific_listing_and_access_controls(isolate_env):
    from fastapi.testclient import TestClient
    client = TestClient(isolate_env['app'])

    token1 = register_user_and_token(client, 'alice', 'alice@example.com')
    token2 = register_user_and_token(client, 'bob', 'bob@example.com')

    png = _make_png_bytes()
    files = {'file': ('a.png', png, 'image/png')}
    r = client.post('/wardrobe/items', files=files, headers={'Authorization': f'Bearer {token1}'})
    assert r.status_code == 200
    item1 = r.json()

    # Bob uploads his own
    r = client.post('/wardrobe/items', files=files, headers={'Authorization': f'Bearer {token2}'})
    assert r.status_code == 200
    item2 = r.json()

    # Alice lists -> only her item
    r = client.get('/wardrobe/items', headers={'Authorization': f'Bearer {token1}'})
    assert r.status_code == 200
    items = r.json()
    assert any(i['id'] == item1['id'] for i in items)
    assert not any(i['id'] == item2['id'] for i in items)

    # Bob cannot read Alice metadata
    r = client.get(f"/wardrobe/items/{item1['id']}", headers={'Authorization': f'Bearer {token2}'})
    assert r.status_code == 404

    # Bob cannot load Alice image
    r = client.get(f"/wardrobe/items/{item1['id']}/image", headers={'Authorization': f'Bearer {token2}'})
    assert r.status_code == 404

    # Bob cannot delete Alice item
    r = client.delete(f"/wardrobe/items/{item1['id']}", headers={'Authorization': f'Bearer {token2}'})
    assert r.status_code == 404


def test_successful_deletion_removes_record_and_files(isolate_env):
    from fastapi.testclient import TestClient
    from database.connection import get_db
    from database.models import WardrobeItem

    client = TestClient(isolate_env['app'])
    token = register_user_and_token(client, 'deleter', 'del@example.com')

    png = _make_png_bytes()
    files = {'file': ('d.png', png, 'image/png')}
    r = client.post('/wardrobe/items', files=files, headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    item = r.json()

    # Ensure files exist
    upload_root = Path(os.getenv('WARDROBE_UPLOAD_ROOT'))
    full_path = upload_root / str(item['user_id']) / item['stored_filename']
    assert full_path.exists()

    # Delete
    r = client.delete(f"/wardrobe/items/{item['id']}", headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200

    # DB record gone
    db = next(get_db())
    found = db.query(WardrobeItem).filter(WardrobeItem.id == item['id']).first()
    assert found is None

    # Files removed (or missing silently)
    assert not full_path.exists()


def test_missing_physical_file_does_not_traceback(isolate_env):
    from fastapi.testclient import TestClient
    from database.connection import get_db
    from database.models import WardrobeItem

    client = TestClient(isolate_env['app'])
    token = register_user_and_token(client, 'm1', 'm1@example.com')

    png = _make_png_bytes()
    files = {'file': ('m.png', png, 'image/png')}
    r = client.post('/wardrobe/items', files=files, headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    item = r.json()

    # Remove physical file manually
    upload_root = Path(os.getenv('WARDROBE_UPLOAD_ROOT'))
    full_path = upload_root / str(item['user_id']) / item['stored_filename']
    if full_path.exists():
        full_path.unlink()

    # Request image should return 404, not 500
    r = client.get(f"/wardrobe/items/{item['id']}/image", headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 404


def test_unsafe_filenames_cannot_traverse(isolate_env):
    from fastapi.testclient import TestClient
    from database.connection import get_db
    from database.models import WardrobeItem

    client = TestClient(isolate_env['app'])
    token = register_user_and_token(client, 't1', 't1@example.com')

    # Create an entry with unsafe stored_filename
    db = next(__import__('database.connection', fromlist=['get_db']).get_db())
    unsafe_name = '../evil.png'
    item = WardrobeItem(user_id=1, stored_filename=unsafe_name, original_filename='evil.png', image_url='/wardrobe/items/999/image', thumbnail_url='/wardrobe/items/999/thumbnail', content_type='image/png', file_size=10)
    db.add(item)
    db.commit()
    db.refresh(item)

    # Attempt to fetch thumbnail and image
    r1 = client.get(f"/wardrobe/items/{item.id}/thumbnail", headers={'Authorization': f'Bearer {token}'})
    r2 = client.get(f"/wardrobe/items/{item.id}/image", headers={'Authorization': f'Bearer {token}'})
    assert r1.status_code == 404
    assert r2.status_code == 404
