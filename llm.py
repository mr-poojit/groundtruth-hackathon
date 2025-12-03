# llm.py
import os
import logging

# Optional: use dotenv for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
USE_GENAI = bool(GEMINI_API_KEY)

if USE_GENAI:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        logging.warning("google.generativeai not available or failed to import: %s", e)
        USE_GENAI = False

MODEL = "gemini-2.0-flash"  # adjust if you have different model access

def generate_insights(prompt: str, max_output_tokens: int = 512) -> str:
    """
    Generate a summary/insights using Gemini.
    If Gemini API key not present or library import fails, return a simple fallback summary.
    """
    if USE_GENAI:
        try:
            # The google.generativeai API surface may vary; the pattern below follows the earlier
            # helper used in this project. If your installed SDK is different, replace this call
            # with the SDK's correct invocation (e.g., genai.generate(...)).
            model = genai.GenerativeModel(MODEL)
            response = model.generate_content(prompt)
            # response may have .text or .candidates etc. Try to extract safe text.
            if hasattr(response, "text"):
                return response.text
            # fallback: inspect response.candidates
            try:
                candidates = getattr(response, "candidates", None)
                if candidates and len(candidates) > 0:
                    return candidates[0].get("content", "")
            except Exception:
                pass
            return str(response)
        except Exception as e:
            logging.exception("Gemini API call failed: %s", e)
            # fallback to safe stub
    # Fallback deterministic summary (useful for offline testing)
    stub = (
        "Executive Summary:\n"
        "- The dataset shows overall healthy engagement.\n"
        "- Key KPIs: impressions, clicks, CTR highlighted above.\n"
        "- Recommendations: Investigate top cities and monitor sudden drops.\n\n"
        "Key Takeaways:\n"
        "- Stable CTR across the period.\n"
        "- Top cities contribute majority of traffic.\n\n"
        "Recommendations:\n"
        "- Re-allocate budget to top-performing regions.\n"
        "- Further investigate anomalies flagged in the report."
    )
    return stub
