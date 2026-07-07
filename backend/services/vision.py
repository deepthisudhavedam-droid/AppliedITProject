import io
from typing import Dict, List
from PIL import Image
import torch
import open_clip


# -----------------------------
# Load CLIP model (OpenCLIP)
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="openai"
)
tokenizer = open_clip.get_tokenizer("ViT-B-32")

model = model.to(device)
model.eval()


# -----------------------------
# Label spaces
# -----------------------------
CATEGORIES = [
    "T-shirt", "Shirt", "Blouse", "Sweater", "Hoodie", "Jacket", "Coat",
    "Jeans", "Trousers", "Shorts", "Skirt", "Dress", "Saree", "Kurta",
    "Suit", "Blazer", "Tracksuit", "Activewear", "Ethnic wear","Gym wear"
]

COLORS = [
    "Black", "White", "Grey", "Blue", "Navy", "Red", "Green", "Yellow",
    "Beige", "Brown", "Pink", "Purple", "Orange", "Pastel", "Multicolor","Lavender"
]

PATTERNS = [
    "Solid", "Striped", "Checked", "Plaid", "Floral", "Polka dots",
    "Graphic print", "Abstract print", "Animal print", "Geometric","Embroidered"
]

STYLES = [
    "Casual", "Formal", "Business casual", "Streetwear", "Sporty",
    "Party", "Traditional", "Minimal", "Elegant", "Boho"
]

GENDERS = [
    "Menswear", "Womenswear", "Unisex"
]

FITS = [
    "Slim", "Regular", "Relaxed", "Oversized", "Tailored", "Athletic", "Loose","Fitted"
]

CLOTHING_CHECK = [
    "a photo of clothing",
    "a photo of a shirt",
    "a photo of pants",
    "a photo of a dress",
    "a photo of a jacket",
    "a photo of a coat",
    "a photo of a blouse",
    "a photo of a hoodie",
    "a photo of a sweater",
    "a photo of a skirt",
    "a photo of a T-shirt",
    "a photo of clothes hanging on a hanger",
    "a photo of a person wearing a shirt",
    "a photo of a person wearing pants",
    "a photo of a person wearing a dress",
    "a photo of a person wearing clothing",
    "a photo of a fashion mannequin",
    "a photo of a clothing display",
    "a photo of a shirt on a hanger"
]

NON_CLOTHING_CHECK = [
    "a photo of a building",
    "a photo of a car",
    "a photo of a tree",
    "a photo of a landscape",
    "a photo of a room interior",
    "a photo of a fruit",
    "a photo of a plant",
    "a photo of an animal",
    "a photo of a vehicle",
    "a photo of a piece of furniture"
]


# -----------------------------
# Clothing detection helper
# -----------------------------
def is_clothing_image(image: Image.Image) -> bool:
    image_tensor = preprocess(image).unsqueeze(0).to(device)
    text_tokens = tokenizer(CLOTHING_CHECK + NON_CLOTHING_CHECK).to(device)

    with torch.no_grad():
        img_feat = model.encode_image(image_tensor)
        txt_feat = model.encode_text(text_tokens)

        img_feat /= img_feat.norm(dim=-1, keepdim=True)
        txt_feat /= txt_feat.norm(dim=-1, keepdim=True)

        similarity = (img_feat @ txt_feat.T).softmax(dim=-1)[0]

    clothing_score = similarity[:len(CLOTHING_CHECK)].max().item()
    non_clothing_score = similarity[len(CLOTHING_CHECK):].max().item()

    print(f"Clothing score: {clothing_score:.4f}, Non-clothing score: {non_clothing_score:.4f}")
    
    # Simply return True if clothing score is higher than non-clothing
    is_clothing = clothing_score > non_clothing_score
    print(f"Is clothing: {is_clothing}")
    return is_clothing


# -----------------------------
# CLIP scoring helper
# -----------------------------
def _clip_best_label(image: Image.Image, labels: List[str]) -> str:
    image_tensor = preprocess(image).unsqueeze(0).to(device)

    text_tokens = tokenizer(labels).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image_tensor)
        text_features = model.encode_text(text_tokens)

        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        similarity = (image_features @ text_features.T).softmax(dim=-1)

    best_idx = similarity[0].argmax().item()
    return labels[best_idx]


# -----------------------------
# Main function
# -----------------------------
def analyze_image(image_bytes: bytes) -> Dict[str, str]:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    if not is_clothing_image(image):
        return {
            "error": "No clothing detected. Please upload a photo of a shirt, pant, dress, jacket, or clothing on a hanger/person."
        }

    return {
        "category": _clip_best_label(image, CATEGORIES),
        "color": _clip_best_label(image, COLORS),
        "pattern": _clip_best_label(image, PATTERNS),
        "style": _clip_best_label(image, STYLES),
        "gender": _clip_best_label(image, GENDERS),
        "fit": _clip_best_label(image, FITS),
    }
