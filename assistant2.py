import streamlit as st
from diagnosis_agent import diagnose_patient
from diet_agent import suggest_diet
from routine_agent import suggest_routine

def assistant_page():
    st.title("AI Health Assistant")
    st.markdown(f"👤 Logged in as: {st.session_state.name}  \n📧 {st.session_state.email}")

    col1, col2, col3 = st.columns(3)

    if col1.button("🦢 Diagnose Patient"):
        output = diagnose_patient(st.session_state.name, st.session_state.email)
        st.session_state["faq_content"] = output
        st.markdown(output, unsafe_allow_html=True)

    if col2.button("🥗 Suggest Diet"):
        output = suggest_diet(st.session_state.name, st.session_state.email)
        st.session_state["faq_content"] = output
        st.markdown(output, unsafe_allow_html=True)

    if col3.button("🏃 Recommend Routine"):
        output = suggest_routine(st.session_state.name, st.session_state.email)
        st.session_state["faq_content"] = output
        st.markdown(output, unsafe_allow_html=True)
