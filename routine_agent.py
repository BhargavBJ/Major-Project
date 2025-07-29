from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import db
import streamlit as st
load_dotenv()

def suggest_routine(name: str, email: str) -> str:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

    patient = db.patients_collection.find_one(
        {"name": name, "email": email},
        {"_id": 0, "name": 1, "symptoms": 1, "conditions": 1}
    )
    if not patient:
        return f"No patient found with name '{name}' and email '{email}'."

    symptoms = patient.get("symptoms", [])
    conditions = patient.get("conditions", [])
    display_name = patient.get("name", "Unknown")

    system_prompt = """
    You are a doctor by profession and have excellent knowledge about the Human Body and all the diseases with their cures. 
    Give the routine for the patient based on the symptoms and conditions. Use the patient's name instead of their pronouns and be specific.
    """
    human_prompt = (
        "Give the routine for the patient name: {name} based on the symptoms provided in: {symptoms} "
        "and the conditions provided in: {conditions}."
    )

    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human_prompt)])
    chat = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant", groq_api_key=GROQ_API_KEY)
    chain = prompt | chat

    result = "".join(chunk.content for chunk in chain.stream({
        "name": display_name,
        "symptoms": symptoms,
        "conditions": conditions
    }))

    return (
        f"### Routine for {display_name}\n"
        f"**Symptoms**: {', '.join(symptoms)}\n"
        f"**Conditions**: {', '.join(conditions)}\n\n"
        f"**Recommended Routine**:\n{result}"
    )
