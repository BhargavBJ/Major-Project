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

    # Init session state
    if "chatbot_response" not in st.session_state:
        st.session_state.chatbot_response = ""
    if "last_user_message" not in st.session_state:
        st.session_state.last_user_message = ""
    if "voice_input" not in st.session_state:
        st.session_state.voice_input = ""

    # 🎤 Voice Input Component (auto injects into Streamlit state)
    speech_component = """
    <script>
    let recognition;
    let finalTranscript = '';

    function startListening() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = function(event) {
            let interimTranscript = '';
            for (let i = 0; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }
            const displayText = finalTranscript + '<i style="color:gray;">' + interimTranscript + '</i>';
            document.getElementById("transcript").innerHTML = displayText;

            // Send finalTranscript into Streamlit state
            const input = window.parent.document.querySelector('textarea[aria-label="voice_input_box"]');
            if (input) {
                input.value = finalTranscript;
                input.dispatchEvent(new Event("input", { bubbles: true }));
            }
        };

        recognition.start();
    }

    function stopListening() {
        if (recognition) recognition.stop();
    }
    </script>

    <div style="margin:10px 0;padding:10px;background:#f9f9f9;border-radius:5px;">
        <button onclick="startListening()" style="margin-right:5px;background:#4CAF50;color:white;padding:6px 12px;border:none;border-radius:4px;">🎤 Start</button>
        <button onclick="stopListening()" style="background:#f44336;color:white;padding:6px 12px;border:none;border-radius:4px;">⏹ Stop</button>
        <div id="transcript" style="margin-top:10px;min-height:40px;font-family:monospace;color:#333;">🎤 Your speech will appear here...</div>
    </div>
    """
    components.html(speech_component, height=180)

    # Hidden text area linked with voice input
    message_input = st.sidebar.text_area(
        "💬 Your message:",
        key="voice_input_box",
        height=100,
        placeholder="Speak above or type here..."
    )

    ask_clicked = st.sidebar.button("📤 Ask Assistant")

    # Chat input fallback
    chat_input = st.sidebar.chat_input("Or type here and press Enter...")

    user_input = None
    if ask_clicked and message_input.strip():
        user_input = message_input.strip()
    elif chat_input:
        user_input = chat_input

    if user_input:
        st.session_state.last_user_message = user_input

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful health assistant..."),
            ("human", "Patient Record:\n{context}\n\nUser Question: {question}")
        ])
        chain = prompt | chat
        response = chain.invoke({"context": full_context, "question": user_input})

        answer = response.content
        st.session_state.chatbot_response = answer

        records_collection.insert_one({
            "email": st.session_state.email,
            "question": user_input,
            "answer": answer,
            "timestamp": datetime.utcnow()
        })

    if st.session_state.chatbot_response:
        st.sidebar.markdown("### 🤖 Assistant Response:")
        st.sidebar.success(st.session_state.chatbot_response)

        speak_html = f"""
        <button onclick="speakText()" style="background:#4CAF50;color:white;padding:8px 15px;border:none;border-radius:5px;">🔊 Speak Response</button>
        <script>
        function speakText() {{
            const text = `{st.session_state.chatbot_response.replace('`','').replace('"','').replace("'","")}`;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.9;
            speechSynthesis.speak(utterance);
        }}
        </script>
        """
        components.html(speak_html, height=50)

