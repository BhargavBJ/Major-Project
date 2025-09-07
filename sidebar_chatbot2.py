import streamlit as st
from db import patients_collection, appointments_collection, records_collection
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from datetime import datetime
import os
from dotenv import load_dotenv
import uuid
import streamlit.components.v1 as components

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

def sidebar_chatbot():
    st.sidebar.markdown("## 🤖 Ask Anything To Your Health Bot")

    if not st.session_state.get("email"):
        st.sidebar.info("Log in to chat with your assistant.")
        return

    patient = patients_collection.find_one({"email": st.session_state.email})
    appointments = list(appointments_collection.find({"email": st.session_state.email}))
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

    full_context = f"""
Patient Name: {name}
Email: {patient.get('email')}
Symptoms: {symptoms}
Conditions: {conditions}
Medications: {medications}

All Appointments:
{appointment_summary}

Upcoming Appointment Info:
{apt_info}
    """

    if "chatbot_response" not in st.session_state:
        st.session_state.chatbot_response = ""
    if "last_user_message" not in st.session_state:
        st.session_state.last_user_message = ""
    user_input = st.sidebar.chat_input("Ask something...")
    if user_input:
        st.session_state.last_user_message = user_input
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful and friendly AI health assistant. Greet the patient by name. Use the full patient record below to respond accurately and avoid hallucinations. Answer questions about any appointment (past or future) based on the record."),
            ("human", "Patient Record:\n{context}\n\nUser Question: {question}")
        ])

        chain = prompt | chat
        response = chain.invoke({
            "context": full_context,
            "question": user_input
        })

        email = st.session_state.email
        answer = response.content
        st.session_state.chatbot_response = answer

        records_collection.insert_one({
    "email": email,
    "question": user_input,  
    "answer": answer,
    "timestamp": datetime.utcnow()
})


    if st.session_state.chatbot_response:
        st.sidebar.markdown("**Assistant:**")
        st.sidebar.success(st.session_state.chatbot_response)

        components.html(f"""
            <script>
                function speak(text) {{
                    const utterance = new SpeechSynthesisUtterance(text);
                    window.speechSynthesis.speak(utterance);
                }}
            </script>
            <button onclick="speak(`{st.session_state.chatbot_response}`)"
                style="background-color:#4CAF50;color:white;padding:5px 10px;border:none;border-radius:5px;cursor:pointer;margin-top:5px;">
                🔊 Speak
            </button>
        """, height=50)
