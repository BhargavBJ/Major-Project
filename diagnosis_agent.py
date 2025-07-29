from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os, db
from dotenv import load_dotenv
import streamlit as st
load_dotenv()

def diagnose_patient(name: str, email: str) -> str:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

    patient = db.patients_collection.find_one({"name": name, "email": email}, {"_id": 0, "name": 1, "symptoms": 1})
    if not patient:
        return "Patient not found."

    symptoms = patient.get("symptoms", [])
    system_prompt = (
        "You are a doctor with excellent knowledge about the human body and all diseases with their cures. "
        "Just give the name of the possible disease, comma-separated if more than one."
    )
    human_prompt = ("Give the diagnosis report based on the symptoms: {topic}. Confine it to the top three possibilities."
                    "Tell it like : Top 3 possible diagnosis")
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human_prompt)])
    chat = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant", groq_api_key=GROQ_API_KEY)
    chain = prompt | chat
    output = "".join(chunk.content for chunk in chain.stream({"topic": symptoms}))
    return f"### Diagnosis for {name}\n**Symptoms**: {', '.join(symptoms)}\n\n**Report**: {output}"
