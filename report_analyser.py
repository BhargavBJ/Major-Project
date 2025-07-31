import os
import fitz  # PyMuPDF for PDF
import docx
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

chat = ChatGroq(
    temperature=0.2,
    model_name="llama-3.1-8b-instant",
    groq_api_key=GROQ_API_KEY
)

def extract_text_from_file(uploaded_file):
    extension = uploaded_file.name.split(".")[-1].lower()
    if extension == "pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
    elif extension == "docx":
        doc = docx.Document(uploaded_file)
        text = "\n".join(p.text for p in doc.paragraphs)
    elif extension == "txt":
        text = uploaded_file.read().decode("utf-8")
    else:
        raise ValueError("Unsupported file format. Please upload a PDF, DOCX, or TXT file.")
    return text

def analyze_report_with_llm(report_text):
    system_prompt = """
You are a helpful and knowledgeable medical assistant.
Analyze the following medical report and provide:

1. A short summary of the diagnosis (in simple language).
2. Key positives in the report.
3. Key concerns or negatives (e.g., abnormal or dangerous values).
4. Clear, patient-friendly advice or next steps to improve their health.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", f"Here is the report text:\n{report_text}")
    ])

    chain = prompt | chat
    response = chain.invoke({})
    return response.content
