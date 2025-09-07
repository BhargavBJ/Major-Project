import streamlit as st
from report_analyser import  extract_text_from_file, analyze_report_with_llm

def report_analyser_page():
    st.title("📄 Upload & Analyze Medical Report")

    uploaded_file = st.file_uploader("Upload a medical report (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
    
    if uploaded_file:
        with st.spinner("Extracting text and analyzing..."):
            try:
                report_text = extract_text_from_file(uploaded_file)
                if not report_text.strip():
                    st.warning("The uploaded file seems to be empty or unreadable.")
                    return

                result = analyze_report_with_llm(report_text)
                st.success("✅ Analysis Complete!")

                st.markdown("### 🧠 Report Summary")
                st.markdown(result)
                st.session_state["faq_content"] = result
            except Exception as e:
                st.error(f"Error: {e}")
