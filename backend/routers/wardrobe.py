import io
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from PIL import Image, ImageOps, UnidentifiedImageError

try:
    from PIL import DecompressionBombError
except ImportError:  # Pillow versions without this class
    DecompressionBombError = Image.DecompressionBombError
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import WardrobeItem
from models.wardrobe_schemas import WardrobeItemResponse
from routers.auth import get_current_user

router = APIRouter(prefix="/wardrobe", tags=["wardrobe"])

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_DIMENSION = 4096
THUMBNAIL_SIZE = (256, 256)
ALLOWED_EXTENSIONS = {"jpeg": "jpg", "png": "png", "webp": "webp"}


def _get_upload_root() -> Path:
    configured_root = os.getenv("WARDROBE_UPLOAD_ROOT")
    if configured_root:
        return Path(configured_root)
    return Path(__file__).resolve().parents[1] / "uploads" / "wardrobes"


def _safe_storage_path(user_id: int, image_format: str) -> Path:
    safe_extension = ALLOWED_EXTENSIONS.get(image_format.lower(), image_format.lower())
    user_dir = _get_upload_root() / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    random_name = uuid.uuid4().hex
    return user_dir / f"{random_name}.{safe_extension}"


def _is_safe_path(path: Path) -> bool:
    upload_root = _get_upload_root().resolve()
    try:
        path.resolve().relative_to(upload_root)
        return True
    except ValueError:
        return False


def _verify_and_prepare_image(file_bytes: bytes) -> tuple[bytes, str, tuple[int, int]]:
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Image exceeds 10 MB limit.")

    try:
        with Image.open(io.BytesIO(file_bytes)) as image:
            image.load()
            image = ImageOps.exif_transpose(image)
            if image.mode in {"RGBA", "LA", "P"}:
                image = image.convert("RGBA")
            else:
                image = image.convert("RGB")

            width, height = image.size
            if width > MAX_DIMENSION or height > MAX_DIMENSION:
                raise HTTPException(status_code=400, detail="Image dimensions exceed the safe limit.")

            if max(width, height) > 4096:
                raise HTTPException(status_code=400, detail="Image is too large for safe processing.")

            if image.width * image.height > 25_000_000:
                raise HTTPException(status_code=400, detail="Image is too large for safe processing.")

            output = io.BytesIO()
            image.save(output, format=image.format or "PNG", optimize=True, quality=90)
            data = output.getvalue()
            return data, (image.format or "PNG").lower(), image.size
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.") from exc
    except DecompressionBombError as exc:
        raise HTTPException(status_code=400, detail="Image is too large for safe processing.") from exc
    except OSError as exc:
        raise HTTPException(status_code=400, detail="Uploaded image is malformed or unreadable.") from exc


def _create_thumbnail(image_bytes: bytes, image_format: str) -> bytes:
    with Image.open(io.BytesIO(image_bytes)) as image:
        image = ImageOps.exif_transpose(image)
        if image.mode in {"RGBA", "LA", "P"}:
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")
        image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(output, format=image_format.upper() or "PNG", optimize=True, quality=85)
        return output.getvalue()


def _get_item_or_404(db: Session, item_id: int, user_id: int) -> WardrobeItem:
    item = db.query(WardrobeItem).filter(WardrobeItem.id == item_id, WardrobeItem.user_id == user_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wardrobe item not found.")
    return item


@router.post("/items", response_model=WardrobeItemResponse)
async def upload_wardrobe_item(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    color: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file is required.")

    file_bytes = await file.read()
    normalized_bytes, detected_format, dimensions = _verify_and_prepare_image(file_bytes)
    if detected_format not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WebP images are supported.")

    stored_path = _safe_storage_path(current_user.id, detected_format)
    thumbnail_bytes = _create_thumbnail(normalized_bytes, detected_format)

    thumbnail_path = stored_path.with_name(stored_path.stem + "_thumb" + stored_path.suffix)
    stored_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        stored_path.write_bytes(normalized_bytes)
        thumbnail_path.write_bytes(thumbnail_bytes)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Unable to save uploaded image.") from exc

    item = WardrobeItem(
        user_id=current_user.id,
        stored_filename=stored_path.name,
        original_filename=file.filename,
        image_url=f"/wardrobe/items/{uuid.uuid4().hex}/image",
        thumbnail_url=f"/wardrobe/items/{uuid.uuid4().hex}/thumbnail",
        content_type=f"image/{detected_format}",
        file_size=len(normalized_bytes),
        category=category,
        color=color,
        notes=notes,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    item.image_url = f"/wardrobe/items/{item.id}/image"
    item.thumbnail_url = f"/wardrobe/items/{item.id}/thumbnail"
    db.commit()
    db.refresh(item)

    return item


@router.get("/items", response_model=list[WardrobeItemResponse])
def list_wardrobe_items(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id).order_by(WardrobeItem.created_at.desc()).all()
    return items


@router.get("/items/{item_id}", response_model=WardrobeItemResponse)
def get_wardrobe_item(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return _get_item_or_404(db, item_id, current_user.id)


@router.get("/items/{item_id}/image")
def get_wardrobe_item_image(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    item = _get_item_or_404(db, item_id, current_user.id)
    storage_path = _get_upload_root() / str(current_user.id) / item.stored_filename
    if not _is_safe_path(storage_path) or not storage_path.exists() or storage_path.is_dir():
        raise HTTPException(status_code=404, detail="Image file not found.")
    return FileResponse(storage_path, media_type=item.content_type)


@router.get("/items/{item_id}/thumbnail")
def get_wardrobe_item_thumbnail(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    item = _get_item_or_404(db, item_id, current_user.id)
    thumbnail_name = item.stored_filename.replace(".png", "_thumb.png") if item.stored_filename.endswith(".png") else item.stored_filename.replace(".jpg", "_thumb.jpg").replace(".jpeg", "_thumb.jpeg").replace(".webp", "_thumb.webp")
    storage_path = _get_upload_root() / str(current_user.id) / thumbnail_name
    if not _is_safe_path(storage_path) or not storage_path.exists() or storage_path.is_dir():
        raise HTTPException(status_code=404, detail="Thumbnail file not found.")
    return FileResponse(storage_path, media_type=item.content_type)


@router.delete("/items/{item_id}", response_model=dict)
def delete_wardrobe_item(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    item = _get_item_or_404(db, item_id, current_user.id)
    upload_root = _get_upload_root()
    storage_path = upload_root / str(current_user.id) / item.stored_filename
    thumbnail_path = None
    if item.stored_filename.endswith(".png"):
        thumbnail_path = upload_root / str(current_user.id) / item.stored_filename.replace(".png", "_thumb.png")
    elif item.stored_filename.endswith(".jpg") or item.stored_filename.endswith(".jpeg"):
        thumbnail_path = upload_root / str(current_user.id) / item.stored_filename.replace(".jpg", "_thumb.jpg").replace(".jpeg", "_thumb.jpeg")
    elif item.stored_filename.endswith(".webp"):
        thumbnail_path = upload_root / str(current_user.id) / item.stored_filename.replace(".webp", "_thumb.webp")

    backup_files = {}
    for path in [storage_path, thumbnail_path]:
        if path and _is_safe_path(path) and path.exists() and path.is_file():
            backup_files[path] = path.read_bytes()

    try:
        db.delete(item)
        db.commit()
    except Exception as exc:
        db.rollback()
        for path, data in backup_files.items():
            try:
                path.write_bytes(data)
            except OSError:
                pass
        raise HTTPException(status_code=500, detail="Unable to delete wardrobe item.") from exc

    for path in [storage_path, thumbnail_path]:
        if path and _is_safe_path(path):
            try:
                if path.exists() and path.is_file():
                    path.unlink()
            except OSError:
                pass

    return {"message": "Wardrobe item deleted."}
