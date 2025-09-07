# main.py V-6.0
import os, streamlit as st, pandas as pd, pytesseract
from dotenv import load_dotenv
from signup import signup_page
from login import login_page
from assistant2 import assistant_page
from calendar_view import calendar_page
from tablet_analyser import tablet_analyzer_page
from motivational_agent import generate_motivational_quote
from report import report_analyser_page
from update import profile_page
from sidebar_chatbot3 import sidebar_chatbot
from faq_generator import generate_faqs

chatbot_available = True
load_dotenv()
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
st.set_page_config(page_title="AI Health Assistant & Calendar", layout="wide")

for key in ["logged_in", "name", "email"]:
    if key not in st.session_state:
        st.session_state[key] = None


def extract_text(x):
    if not x:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        return " ".join(str(v) for v in x.values())
    if isinstance(x, list):
        return " ".join(extract_text(i) for i in x)
    return str(x)


def collect_context(preferred=None):
    buckets = {
        "assistant": [
            "diagnosis_output", "diet_output", "routine_output", "assistant_output",
            "assistant_result", "generated_text", "latest_output"
        ],
        "tablet": [
            "tablet_output", "pill_identification", "ocr_text", "tablet_result",
            "meds_summary", "latest_output"
        ],
        "report": [
            "report_summary", "report_output", "analysis_output",
            "report_result", "latest_output"
        ],
        "profile": [
            "profile_output", "medical_history", "allergies",
            "profile_changes", "latest_output"
        ]
    }

    parts = []
    keys = buckets.get(preferred, [])
    for k in keys:
        v = st.session_state.get(k, "")
        if isinstance(v, str) and len(v.strip()) > 60:
            parts.append(v.strip())

    if not parts:
        for k, v in st.session_state.items():
            if k in ("logged_in", "name", "email"):
                continue
            if isinstance(v, str) and len(v.strip()) > 120:
                parts.append(v.strip())

    text = (" ".join(parts)).strip()
    return text if len(text) > 120 else ""


def render_faq_section(content):
    text = extract_text(content).strip()
    if not text:
        text = collect_context("assistant")
    if text:
        faqs = generate_faqs(text)
        if faqs and isinstance(faqs, list):
            st.markdown("---")
            st.subheader("❓ Frequently Asked Questions")
            for i, faq in enumerate(faqs):
                q = (faq.get("question") or "").strip()
                a = (faq.get("answer") or "").strip()
                if not q or not a:
                    continue
                with st.expander(f"Q{i+1}: {q}"):
                    st.write(a)


if st.session_state.logged_in:
    if chatbot_available:
        try:
            sidebar_chatbot()
        except Exception:
            st.sidebar.warning("Sidebar chatbot failed to load.")

    with st.container():
        st.markdown("### 💬 Daily Motivation")
        with st.spinner("Generating motivational message..."):
            try:
                st.info(generate_motivational_quote())
            except Exception:
                st.warning("Couldn't load quote right now.")

    st.markdown(f"👤 Logged in as: {st.session_state.name}  \n📧 {st.session_state.email}")

    col1, col2 = st.columns([10, 1])
    with col1:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["🤖 AI Assistant", "📅 Calendar", "💊 Tablet Analyzer", "📄 Report Analyzer", "📝 Edit Profile"]
        )
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.name = None
            st.session_state.email = None
            st.rerun()

    with tab1:
        res = assistant_page()
        ctx = extract_text(res) or collect_context("assistant")
        if ctx:
            render_faq_section(ctx)

    with tab2:
        calendar_page()

    with tab3:
        tabs = tablet_analyzer_page()
        ctx = extract_text(tabs) or collect_context("tablet")
        if ctx:
            render_faq_section(ctx)

    with tab4:
        reps = report_analyser_page()
        ctx = extract_text(reps) or collect_context("report")
        if ctx:
            render_faq_section(ctx)

    with tab5:
        prof = profile_page()
        ctx = extract_text(prof) or collect_context("profile")
        if ctx:
            render_faq_section(ctx)

else:
    st.title("Welcome to AI Health Assistant")
    page = st.radio("Select an option:", ["Login", "Sign Up"], horizontal=True)
    if page == "Login":
        login_page()
    else:
        signup_page()
