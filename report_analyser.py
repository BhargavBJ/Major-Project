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
    model_name="openai/gpt-oss-20b",
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
You will analyze medical reports and explain them in a way that is simple, supportive, and easy for a patient to understand.

Your answer must always be structured into the following clear sections:

1. 📝 Diagnosis Summary:
   - Explain the diagnosis in simple, non-technical language.
   - Use short, clear sentences so the patient understands their condition.

2. ✅ Key Positives in the Report:
   - Highlight any normal values or signs of good health.
   - Give encouragement (e.g., "Your blood sugar looks good, which means your diabetes is under good control.").

3. ⚠️ Key Concerns / Abnormal Findings:
   - Point out any values that are too high, too low, or worrying.
   - Explain what they might mean in plain English (e.g., "Your cholesterol is high, which can increase the risk of heart disease.").

4. 🍎 Diet Advice:
   - Give **specific and practical diet tips** tailored to the concerns.
   - Use a “Do Eat” and “Avoid” list for clarity.
   - If possible, suggest **easy recipes** or meal ideas.
   - Example format:
     Do Eat:
     - Fresh fruits like apples, oranges, and papaya.
     - Green vegetables like spinach, broccoli, and beans.
     Avoid:
     - Fried foods, sugary drinks, and processed meats.

5. 🏃 Lifestyle & Next Steps:
   - Give practical, daily-life changes (e.g., “Take a 20-minute walk after dinner”).
   - Suggest relaxation tips (breathing, yoga, meditation).
   - If serious, clearly recommend: “Please consult your doctor for further tests/medication.”

Your tone must always be:
- Supportive, kind, and encouraging.
- Focused on making the patient feel hopeful and capable of improving their health.
- Avoid overly technical jargon; always explain in plain words.
"""


    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", f"Here is the report text:\n{report_text}")
    ])

    chain = prompt | chat
    response = chain.invoke({})
    return response.content
