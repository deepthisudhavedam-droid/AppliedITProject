import os
import json
import google.generativeai as genai
from models.schemas import DetectedData

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the API
genai.configure(api_key=GEMINI_API_KEY)


def build_prompt(detected: DetectedData) -> str:
    return f"""You are an elite AI fashion stylist and outfit‑matching expert.

You will receive detected clothing attributes from a vision model (CLIP or similar):

Detected clothing attributes:
- Category: {detected.category}
- Color: {detected.color}
- Pattern: {detected.pattern}
- Style: {detected.style}
- Gender: {detected.gender}
- Fit: {detected.fit}

TASK:
Using the detected item as the anchor piece, generate 3 complete outfit combinations that complement it.

For each outfit, you MUST include:
- title: A short, stylish name for the outfit.
- description: A clear explanation of why this outfit pairs well with the detected item.
- match_percentage (0–100): How well the outfit complements the detected item.
- reasoning: A short justification for the match score.
- best_occasion: The single most suitable occasion for this outfit (e.g., Casual Outing, First Date, Office Casual, College, Travel, Party, Family Gathering).
- suggested_items: An array of clothing items and accessories that complete the outfit.

GUIDELINES:
- Ensure all suggestions logically match the detected item’s category, color, pattern, style, and fit.
- Use modern fashion logic and color theory.
- Keep tone confident, helpful, and stylist‑like.
- Avoid repeating the same items across all 3 outfits.
- Make sure each outfit feels distinct.

OUTPUT FORMAT:
Return ONLY a valid JSON object with the following structure:

{{
  "suggestions": [
    {{
      "title": "",
      "description": "",
      "match_percentage": 0,
      "reasoning": "",
      "best_occasion": "",
      "suggested_items": ["", ""]
    }}
  ]
}}

Do NOT include any text outside the JSON.

"""


def call_llm(prompt: str):
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")

    try:
        model_name = "gemini-flash-lite-latest"
        print(f"Initializing {model_name}...")
        model = genai.GenerativeModel(model_name)
        
        print(f"Sending request to Gemini API...")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4000,  # Increased to prevent truncation
            )
        )
        
        print(f"Got response from Gemini")
        
        # Check if response is blocked
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            raise RuntimeError(f"Response blocked: {response.prompt_feedback.block_reason}")
        
        # Get text from response
        if not response.text or response.text.strip() == "":
            print(f"Response text is empty!")
            raise RuntimeError(f"Empty response from Gemini API")
        
        text = response.text
        print(f"Response text length: {len(text)}")
        
        # Strip markdown code blocks if present
        if text.startswith("```"):
            # Remove ```json or ``` from start
            text = text.lstrip("`").lstrip("json").lstrip("\n")
            # Remove ``` from end
            text = text.rstrip("`").rstrip("\n")
            print(f"Stripped markdown, new length: {len(text)}")
        
        # Fix common JSON issues
        # Remove trailing commas before closing brackets
        text = text.replace("},\n    ,", "},")  # Fix: },\n    , -> },
        text = text.replace("]\n    ,", "],")   # Fix: ]\n    , -> ],
        text = text.replace("},\n,", "},")      # Fix: },\n, -> },
        text = text.replace("},\n}", "},\n}")   # Ensure proper closing
        
        # Ensure response ends properly if truncated
        if not text.rstrip().endswith("}"):
            print(f"Response appears truncated. Attempting to repair...")
            # Count open and close braces
            open_braces = text.count("{")
            close_braces = text.count("}")
            if open_braces > close_braces:
                # Add missing closing braces
                text = text.rstrip() + "}" * (open_braces - close_braces)
                print(f"Added {open_braces - close_braces} closing brace(s)")
        
        print(f"Final text length: {len(text)}")
        print(f"First 200 chars: {text[:200]}")
        print(f"Last 100 chars: {text[-100:]}")
        
        # Parse JSON
        parsed = json.loads(text)
        print(f"Successfully parsed JSON response")
        return parsed
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Text to parse (first 500 chars): {text[:500] if 'text' in locals() else 'No text'}")
        raise RuntimeError(f"Failed to parse LLM response as JSON: {e}")
    except Exception as e:
        print(f"Error calling Gemini: {str(e)}")
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Gemini API error: {e}")


def generate_outfits(detected: DetectedData):
    prompt = build_prompt(detected)
    return call_llm(prompt)
