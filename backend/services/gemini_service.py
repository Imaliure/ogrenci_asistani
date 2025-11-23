import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=API_KEY)

def get_gemini_response(question):
    model = genai.GenerativeModel("models/gemini-2.5-flash")

    prompt = (
        f"Lütfen yanıtı kısa ve öz yaz. En fazla 300 karakterlik cevap ver. \n\n"
        f"Soru: {question}"
    )

    response = model.generate_content(
        contents=[{"role": "user", "parts": [{"text": prompt}]}]
    )

    return response.candidates[0].content.parts[0].text
