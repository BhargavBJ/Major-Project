import os
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError
import pytesseract
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
def analyze_tablet_image(input_path: str):
    try:
        image = Image.open(input_path).convert("RGB")
        extracted_text = pytesseract.image_to_string(image)
        cleaned_text = extracted_text.strip().replace("\n", " ")
        if not cleaned_text:
            print("No text detected in the image.")
            return
        print("\nExtracted Text:\n", cleaned_text)
        system_prompt = (
            "You are a skilled pharmacist. Based on the medicine name or composition given, "
            "describe what the tablet is used for, the medical condition it treats, and how it works. "
            "Keep it simple and clear for patients."
        )
        human_prompt = (
            "Medicine or composition: {medicine_text}. Explain what it does, and what condition it is commonly used for."
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])
        chat = ChatGroq(
            temperature=0.3,
            model_name="gemma2-9b-it",
            groq_api_key=GROQ_API_KEY
        )
        chain = prompt | chat
        print("\nMedicine Description:\n")
        for chunk in chain.stream({"medicine_text": cleaned_text}):
            print(chunk.content, end="", flush=True)
    except UnidentifiedImageError:
        print("Invalid image file or unsupported format.")

if __name__ == "__main__":
    image_path = "path_to_your_image.jpg"
    analyze_tablet_image(image_path)
