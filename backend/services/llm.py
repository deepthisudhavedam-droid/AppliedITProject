import os
import json
from pathlib import Path

try:
    from google import genai as google_genai
    from google.genai import types as google_genai_types
except ImportError:  # pragma: no cover - fallback for older environments
    google_genai = None
    google_genai_types = None

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - fallback for environments without the old package
    genai = None

from models.schemas import DetectedData


def get_dotenv_path():
    candidates = [
        Path(__file__).resolve().parents[1] / ".env",
        Path(__file__).resolve().parents[2] / ".env",
        Path.cwd() / ".env",
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def _load_dotenv_values():
    env_path = get_dotenv_path()
    if not env_path.exists():
        return {}

    values = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def resolve_api_key():
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        value = os.getenv(key)
        if value and value.strip():
            return value.strip()

    dotenv_values = _load_dotenv_values()
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        value = dotenv_values.get(key)
        if value and value.strip():
            return value.strip()

    return None


def resolve_model_candidates():
    env_model = os.getenv("GEMINI_MODEL")
    if env_model and env_model.strip():
        return [env_model.strip()]

    dotenv_values = _load_dotenv_values()
    dotenv_model = dotenv_values.get("GEMINI_MODEL")
    if dotenv_model and dotenv_model.strip():
        return [dotenv_model.strip()]

    return [
        "models/gemini-2.5-flash-lite",
        "models/gemini-flash-latest",
        "models/gemini-2.0-flash-lite-001",
        "models/gemini-2.0-flash-lite",
        "models/gemini-2.0-flash-001",
        "models/gemini-pro-latest",
    ]


def configure_genai():
    api_key = resolve_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Add it to the environment or a .env file.")

    if google_genai is not None:
        return api_key

    if genai is not None:
        genai.configure(api_key=api_key)
        return api_key

    raise RuntimeError("No supported Gemini client is available. Install google-genai or google-generativeai.")


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
    api_key = configure_genai()

    try:
        last_error = None
        for model_name in resolve_model_candidates():
            try:
                print(f"Initializing {model_name}...")

                if google_genai is not None:
                    client = google_genai.Client(api_key=api_key)
                    print(f"Sending request to Gemini API with {model_name}...")
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=google_genai_types.GenerateContentConfig(
                            temperature=0.7,
                            max_output_tokens=4000,
                        ),
                    )
                else:
                    model = genai.GenerativeModel(model_name)
                    print(f"Sending request to Gemini API with {model_name}...")
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.7,
                            max_output_tokens=4000,
                        ),
                    )

                break
            except Exception as exc:
                last_error = exc
                exc_str = str(exc)
                print(f"Model {model_name} failed: {exc}")
                # Check for quota or rate limit errors
                if "429" in exc_str or "RESOURCE_EXHAUSTED" in exc_str or "quota" in exc_str.lower():
                    print(f"Quota or rate limit exceeded - moving to next model")
                elif "503" in exc_str or "UNAVAILABLE" in exc_str:
                    print(f"Model temporarily unavailable - moving to next model")
        else:
            last_error_str = str(last_error)
            if "429" in last_error_str or "RESOURCE_EXHAUSTED" in last_error_str:
                raise RuntimeError(
                    "Gemini API quota exceeded. The free tier has daily/per-minute limits. "
                    "Please wait for the quota to reset, or upgrade to a paid plan. "
                    f"Error: {last_error}"
                )
            elif "503" in last_error_str or "UNAVAILABLE" in last_error_str:
                raise RuntimeError(
                    "All Gemini models are temporarily unavailable due to high demand. "
                    "Please try again in a few moments."
                )
            else:
                raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")
        
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
