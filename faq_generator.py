# faq_generator.py
import os, json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

groq_api_key = os.getenv("GROQ_API_KEY")

chat = ChatGroq(
    temperature=0.3,
    model_name="openai/gpt-oss-120b",
    groq_api_key=groq_api_key
)

faq_prompt = ChatPromptTemplate.from_template("""
You are a helpful medical FAQ generator for a Health Assistant app.
Based ONLY on the following content:
---
{content}
---
Generate 3 to 5 very relevant FAQs that a patient might naturally ask.
Keep answers short, clear, and medically safe.
❌ Do not explain what the assistant is or give generic FAQs.
✅ Only focus on the medical issue, treatment, lifestyle, or diet from the text.

Return strictly as JSON:
[
  {{"question": "string","answer":"string"}},
  {{"question": "string","answer":"string"}}
]
""")

def generate_faqs(content: str):
    try:
        prompt = faq_prompt.format_messages(content=content)
        response = chat.invoke(prompt).content.strip()

        # Try parsing JSON safely
        try:
            faqs = json.loads(response)
            if isinstance(faqs, list) and all("question" in f and "answer" in f for f in faqs):
                return faqs
        except:
            pass

        # Try extracting JSON substring if model adds text around it
        start = response.find("[")
        end = response.rfind("]") + 1
        if start != -1 and end != -1:
            try:
                faqs = json.loads(response[start:end])
                if isinstance(faqs, list) and all("question" in f and "answer" in f for f in faqs):
                    return faqs
            except:
                pass

        # 🚨 Fallback: generate at least 2 contextual FAQs from the input
        fallback = [
            {"question": "What should I focus on from this report?",
             "answer": content.split(".")[0][:120] + "..."},
            {"question": "Do I need professional consultation?",
             "answer": "Yes. Always discuss these findings with a qualified healthcare provider."}
        ]
        return fallback

    except Exception as e:
        # Absolute fallback if everything fails
        return [
            {"question": "Why don’t I see my FAQs?",
             "answer": "The AI service encountered an issue. Please try again later."}
        ]
