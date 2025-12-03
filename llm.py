import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Set GEMINI_API_KEY env variable.")

genai.configure(api_key=API_KEY)

# Use gemini-2.0-flash or gemini-pro depending on your account access
MODEL = "gemini-2.0-flash"

def generate_insights(prompt: str):
    model = genai.GenerativeModel(MODEL)
    response = model.generate_content(prompt)
    return response.text
