from fastapi import APIRouter, UploadFile, File, HTTPException
from services.vision import analyze_image
from models.schemas import DetectedData

router = APIRouter()

@router.post("/analyze-image")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    # Accept any image content type (image/png, image/jpeg, image/jpg, etc.)
    if not file.content_type or not file.content_type.startswith("image/"):
        print(f"Invalid content type: {file.content_type}")
        raise HTTPException(status_code=400, detail=f"Invalid image type: {file.content_type}")

    print(f"Analyzing image: {file.filename}, content-type: {file.content_type}")
    image_bytes = await file.read()
    print(f"Image size: {len(image_bytes)} bytes")

    try:
        detected = analyze_image(image_bytes)
        print(f"Vision result: {detected}")
    except Exception as e:
        # Log and return a 500 if vision service errors
        print(f"Vision service error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {str(e)}")

    # If analyzer returns an error message, surface it as a 400
    if isinstance(detected, dict) and detected.get("error"):
        print(f"Non-clothing detected: {detected.get('error')}")
        raise HTTPException(status_code=400, detail=detected.get("error"))

    return DetectedData(**detected)
