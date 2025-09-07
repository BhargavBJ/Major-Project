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
    model_name="openai/gpt-oss-120b",
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

    # Initialize session state variables
    if "chatbot_response" not in st.session_state:
        st.session_state.chatbot_response = ""
    if "last_user_message" not in st.session_state:
        st.session_state.last_user_message = ""

    # Voice Input Section
    st.sidebar.markdown("### 🎤 Voice Input")

    # Simple Speech Recognition Component
    speech_component = """
    <div style="background: #f0f2f6; padding: 15px; border-radius: 8px; margin: 10px 0;">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div id="status" style="font-weight: bold; color: #1f77b4; flex: 1;">
                🎤 Ready to record
            </div>
            <button onclick="copyToClipboard()" id="copyBtn" style="
                background: #2196F3; color: white; border: none; padding: 6px 12px; 
                border-radius: 4px; cursor: pointer; font-size: 12px;" disabled>
                📋 Copy
            </button>
        </div>
        
        <div style="display: flex; gap: 8px; margin-bottom: 12px;">
            <button onclick="startListening()" id="startBtn" style="
                background: #4CAF50; color: white; border: none; padding: 8px 12px; 
                border-radius: 5px; cursor: pointer; font-size: 14px;">
                🎤 Start
            </button>
            <button onclick="stopListening()" id="stopBtn" style="
                background: #f44336; color: white; border: none; padding: 8px 12px; 
                border-radius: 5px; cursor: pointer; font-size: 14px;" disabled>
                ⏹️ Stop
            </button>
            <button onclick="clearTranscript()" style="
                background: #757575; color: white; border: none; padding: 8px 12px; 
                border-radius: 5px; cursor: pointer; font-size: 14px;">
                🗑️ Clear
            </button>
        </div>
        
        <div id="transcript" style="
            padding: 12px; background: white; border-radius: 5px; min-height: 80px; 
            border: 2px solid #ddd; font-family: monospace; font-size: 14px;
            white-space: pre-wrap; word-wrap: break-word;">
            <span style="color: #888;">Your speech will appear here...</span>
        </div>
        

    </div>

    <script>
    let recognition;
    let isListening = false;
    let finalTranscript = '';

    function startListening() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                isListening = true;
                updateUI('🔴 Listening... Speak now!', '#f44336');
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('copyBtn').disabled = true;
                finalTranscript = '';
            };
            
            recognition.onresult = function(event) {
                let interimTranscript = '';
                finalTranscript = '';
                
                for (let i = 0; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                const displayText = finalTranscript + 
                    '<span style="color: #666; font-style: italic;">' + interimTranscript + '</span>';
                document.getElementById('transcript').innerHTML = displayText || 
                    '<span style="color: #888;">Listening...</span>';
            };
            
            recognition.onerror = function(event) {
                updateUI('❌ Error: ' + event.error, '#f44336');
                resetButtons();
            };
            
            recognition.onend = function() {
                isListening = false;
                if (finalTranscript.trim()) {
                    updateUI('✅ Recording complete! Click Copy below.', '#4CAF50');
                    document.getElementById('copyBtn').disabled = false;
                    // Show just the final transcript without interim results
                    document.getElementById('transcript').innerHTML = finalTranscript.trim() || 
                        '<span style="color: #888;">No speech detected</span>';
                } else {
                    updateUI('⚠️ No speech detected. Try again.', '#ff9800');
                    document.getElementById('transcript').innerHTML = 
                        '<span style="color: #888;">No speech detected. Please try again.</span>';
                }
                resetButtons();
            };
            
            recognition.start();
        } else {
            updateUI('❌ Speech recognition not supported', '#f44336');
        }
    }

    function stopListening() {
        if (recognition && isListening) {
            recognition.stop();
        }
    }

    function clearTranscript() {
        finalTranscript = '';
        document.getElementById('transcript').innerHTML = 
            '<span style="color: #888;">Your speech will appear here...</span>';
        updateUI('🎤 Ready to record', '#1f77b4');
        document.getElementById('copyBtn').disabled = true;
    }

    function resetButtons() {
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
    }

    function updateUI(statusText, color) {
        document.getElementById('status').innerHTML = statusText;
        document.getElementById('status').style.color = color;
    }

    function copyToClipboard() {
        const text = finalTranscript.trim();
        if (text) {
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(function() {
                    updateUI('📋 Copied! Paste it in the message box below.', '#4CAF50');
                    setTimeout(() => {
                        updateUI('✅ Text ready to paste below', '#4CAF50');
                    }, 2000);
                }, function(err) {
                    // Fallback for older browsers
                    fallbackCopyToClipboard(text);
                });
            } else {
                fallbackCopyToClipboard(text);
            }
        } else {
            updateUI('⚠️ No text to copy. Please record first.', '#ff9800');
        }
    }

    function fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
            updateUI('📋 Copied! Paste it in the message box below.', '#4CAF50');
            setTimeout(() => {
                updateUI('✅ Text ready to paste below', '#4CAF50');
            }, 2000);
        } catch (err) {
            updateUI('❌ Copy failed. Please select and copy text manually.', '#f44336');
        }
        document.body.removeChild(textArea);
    }
    </script>
    """
    
    components.html(speech_component, height=250)

    # Text Input Area
    st.sidebar.markdown("### 💬 Message")
    message_input = st.sidebar.text_area(
        "Your message:",
        height=100,
        placeholder="Type here or paste voice input from above..."
    )

    # Ask Button
    ask_clicked = st.sidebar.button("📤 Ask Assistant", key="ask_btn", type="primary")

    # Handle message processing
    user_input = None
    
    # Check for regular chat input (original functionality)
    chat_input = st.sidebar.chat_input("Or type here and press Enter...")
    
    if ask_clicked and message_input.strip():
        user_input = message_input.strip()
    elif chat_input:
        user_input = chat_input

    # Process the message
    if user_input:
        st.session_state.last_user_message = user_input
        
        # Generate response
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

        # Store in database
        records_collection.insert_one({
            "email": email,
            "question": user_input,  
            "answer": answer,
            "timestamp": datetime.utcnow()
        })

    # Display response
    if st.session_state.chatbot_response:
        st.sidebar.markdown("### 🤖 Assistant Response:")
        st.sidebar.success(st.session_state.chatbot_response)

        # Text-to-Speech button
        speak_html = f"""
        <button onclick="speakText()" style="
            background-color: #4CAF50;
            color: white;
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        ">🔊 Speak Response</button>
        
        <script>
        function speakText() {{
            const text = `{st.session_state.chatbot_response.replace('`', '').replace('"', '').replace("'", "")}`;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.8;
            utterance.pitch = 1;
            speechSynthesis.speak(utterance);
        }}
        </script>
        """
        components.html(speak_html, height=50)

    # Usage instructions
    with st.sidebar.expander("📋 How to Use Voice Input"):
        st.markdown("""
        **Voice Input Steps:**
        1. Click "🎤 Start" to begin recording
        2. Speak your question clearly
        3. Click "⏹️ Stop" when finished
        4. Click "📋 Copy" to copy the transcribed text
        5. Paste (Ctrl+V) in the message box
        6. Click "📤 Ask Assistant" to send
        
        **Alternative:**
        - Type directly in the message box
        - Or use the chat input at the bottom
        
        **Listen to Response:**
        - Click "🔊 Speak Response" to hear the answer
        """)