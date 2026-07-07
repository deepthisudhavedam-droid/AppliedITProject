from pydantic import BaseModel
from typing import List


class DetectedData(BaseModel):
    category: str
    color: str
    pattern: str
    style: str
    gender: str
    fit: str


class OutfitSuggestion(BaseModel):
    title: str
    description: str
    match_percentage: int
    reasoning: str
    best_occasion: str
    suggested_items: List[str]


class OutfitResponse(BaseModel):
    detected: DetectedData
    suggestions: List[OutfitSuggestion]