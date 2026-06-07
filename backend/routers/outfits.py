from fastapi import APIRouter, HTTPException
from models.schemas import DetectedData, OutfitResponse, OutfitSuggestion
from services.llm import generate_outfits

router = APIRouter(prefix="/generate-outfits", tags=["outfits"])


@router.post("", response_model=OutfitResponse)
async def generate_outfits_endpoint(detected: DetectedData):
    print(f"Received detected data: {detected}")
    
    try:
        print(f"Calling generate_outfits with: category={detected.category}, color={detected.color}")
        llm_result = generate_outfits(detected)
        print(f"LLM result: {llm_result}")
    except Exception as e:
        print("LLM ERROR:", str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    suggestions_raw = llm_result.get("suggestions", [])
    print(f"Found {len(suggestions_raw)} suggestions")

    suggestions = [
        OutfitSuggestion(
            title=s["title"],
            description=s["description"],
            match_percentage=int(s["match_percentage"]),
            reasoning=s["reasoning"],
            best_occasion=s["best_occasion"],
            suggested_items=s["suggested_items"],
        )
        for s in suggestions_raw
    ]

    return OutfitResponse(
        detected=detected,
        suggestions=suggestions,
    )
