import json, os
from google import genai
from google.genai import types

CATEGORIES = {"Pothole", "Garbage", "Water Leakage", "Drainage", "Streetlight", "Pollution", "Other"}
SEVERITIES = {"Low", "Medium", "High"}

def analyze_image(image_bytes: bytes, mime_type: str) -> dict:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or key == "put_your_key_here":
        raise RuntimeError("Gemini API key missing. Add it to backend/.env")
    client = genai.Client(api_key=key)
    prompt = '''
Inspect this civic issue photo. Return ONLY valid JSON with keys:
category (Pothole, Garbage, Water Leakage, Drainage, Streetlight, Pollution, Other),
severity (Low, Medium, High), summary (one short sentence),
department (short relevant department).
If unclear, choose Other and Medium. Do not infer an exact address.
Severity is only an AI triage suggestion and needs human verification.
'''
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=[prompt, types.Part.from_bytes(data=image_bytes, mime_type=mime_type)],
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    result = json.loads(response.text or "{}")
    category = result.get("category", "Other")
    severity = result.get("severity", "Medium")
    return {
        "category": category if category in CATEGORIES else "Other",
        "severity": severity if severity in SEVERITIES else "Medium",
        "summary": str(result.get("summary", "Manual review required."))[:500],
        "department": str(result.get("department", "Municipal Corporation"))[:100],
    }
