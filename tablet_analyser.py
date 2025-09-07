import streamlit as st
from PIL import Image, UnidentifiedImageError
import pytesseract
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def tablet_analyzer_page():
    st.title("💊 Tablet Strip Analyzer")
    uploaded_file = st.file_uploader("Upload a clear image of the tablet strip", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        try:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded Tablet Image", use_column_width=True)
            with st.spinner("🔍 Analyzing image for text..."):
                extracted_text = pytesseract.image_to_string(image)
                cleaned_text = extracted_text.strip().replace("\n", " ")
            st.markdown("**📄 Extracted Text:**")
            st.code(cleaned_text or "No text found.", language="text")
            if cleaned_text:
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
                    model_name="openai/gpt-oss-120b",
                    groq_api_key=GROQ_API_KEY
                )
                chain = prompt | chat
                st.markdown("**🤖 Medicine Description:**")
                output = "".join(chunk.content for chunk in chain.stream({"medicine_text": cleaned_text}))
                st.success(output)
                st.session_state["medicine_description"] = output
                return output
            else:
                st.warning("Could not extract any text. Please upload a clearer image.")
        except UnidentifiedImageError:
            st.error("⚠️ Failed to open image. Please upload a valid image file.")
