import streamlit as st
from db import patients_collection, appointments_collection, records_collection
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

chat = ChatGroq(
    temperature=0.4,
    model_name="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def get_next_appointment(appointments):
    now = datetime.now()
    upcoming = sorted(
        [a for a in appointments if 'start' in a and datetime.fromisoformat(a['start']) > now],
        key=lambda x: datetime.fromisoformat(x['start'])
    )
    return upcoming[0] if upcoming else None

def fetch_chat_history(email):
    return list(records_collection.find({"email": email}))

def log_chat_message(email, question, answer):
    records_collection.insert_one({
        "email": email,
        "timestamp": datetime.utcnow(),
        "question": question,
        "answer": answer
    })

def sidebar_chatbot():
    st.sidebar.markdown("## 🤖 Ask Anything To Your Health Bot")

    if not st.session_state.get("email"):
        st.sidebar.info("Log in to chat with your assistant.")
        return

    email = st.session_state.email
    patient = patients_collection.find_one({"email": email})
    appointments = list(appointments_collection.find({"email": email}))
    history = fetch_chat_history(email)

    if not patient:
        st.sidebar.warning("Patient record not found.")
        return

    name = patient.get("name", "there")
    symptoms = patient.get("symptoms", "Not specified")
    conditions = patient.get("conditions", "Not specified")
    medications = patient.get("medications", "Not specified")

    next_apt = get_next_appointment(appointments)
    if next_apt:
        apt_time = datetime.fromisoformat(next_apt['start']).strftime("%A at %I:%M %p")
        apt_title = next_apt.get("title", "No title provided")
        apt_info = f"Your next appointment is '{apt_title}' scheduled for {apt_time}."
    else:
        apt_info = "You have no upcoming appointments at the moment."

    appointment_summary = "\n".join([
        f"- {a.get('title', 'No title')} on {datetime.fromisoformat(a['start']).strftime('%Y-%m-%d %I:%M %p')}"
        for a in appointments if 'start' in a
    ]) or "No appointments on record."

    chat_history = "\n".join([
        f"User: {msg['question']}\nAssistant: {msg['answer']}"
        for msg in history
    ]) or "No previous conversations."

    full_context = f"""
Patient Name: {name}
Email: {email}
Symptoms: {symptoms}
Conditions: {conditions}
Medications: {medications}

All Appointments:
{appointment_summary}

Upcoming Appointment Info:
{apt_info}

Previous Conversation History:
{chat_history}
    """

    user_input = st.sidebar.chat_input("Ask something...")
    if user_input:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful and friendly AI health assistant. Greet the patient by name. Use the full patient record and conversation history to respond accurately and avoid hallucinations."),
            ("human", "Patient Record:\n{context}\n\nUser Question: {question}")
        ])

        chain = prompt | chat
        response = chain.invoke({
            "context": full_context,
            "question": user_input
        })

        answer = response.content
        log_chat_message(email, user_input, answer)

        st.sidebar.markdown("**Assistant:**")
        st.sidebar.success(answer)
