# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""Debug: print raw Gemini response to diagnose JSON parse error."""
from google import genai
from google.genai import types as genai_types
import google.auth
import sys

# Force UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
client = genai.Client(vertexai=True, project="studio-9101802118-8c9a8", location="global", credentials=creds)

sample_text = """
Liberty Head Nickels 1883-1912

    1883 Without Cents  o
    1883 With Cents     o
    1884                o
    1885                o
    1886                o
    1887                o
    1888                o
    1889                o
    1890                o
    1891                o
    1892                o
    1893                o
    1894                o
    1895                o
    1896                o
    1897                o
    1898                o
    1899                o
    1900                o
    1901                o
    1902                o
    1903                o
    1904                o
    1905                o
    1906                o
    1907                o
    1908                o
    1909                ●
    1910                ●
    1911                o
    1912                o
    1912-D              o
    1912-S              o
"""

PROMPT = (
    "You are analyzing a Littleton Coin Company checklist.\n"
    "Extract series_name and all coin entries.\n"
    "For each row: coin_subject = year/descriptor text, is_owned = true if circle is filled (●), false if empty (○ or o).\n"
    "Return ONLY valid JSON:\n"
    '{"series_name": "string", "entries": [{"coin_subject": "string", "is_owned": boolean}]}\n\n'
    "=== DOCUMENT TEXT ===\n" + sample_text
)

try:
    # Try with JSON mode
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=PROMPT,
        config=genai_types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,
            max_output_tokens=8192,
        ),
    )
    print("Response (JSON mode):")
    print(repr(response.text[:500]))
except Exception as e:
    print(f"JSON mode failed: {e}")
    # Fall back to text mode
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=PROMPT,
        config=genai_types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=8192,
        ),
    )
    print("Response (text mode):")
    print(repr(response.text[:500]))
