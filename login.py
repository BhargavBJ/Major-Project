import streamlit as st
from db import patients_collection

def login_page():
    st.title("🧑‍⚕ Patient Login")
    name = st.text_input("Enter your name")
    email = st.text_input("Enter your email")
    if st.button("Login"):
        if not name or not email:
            st.warning("Please enter both name and email.")
            return
        user = patients_collection.find_one({"name": name, "email": email})
        if user:
            st.session_state.logged_in = True
            st.session_state.name = name
            st.session_state.email = email
            st.rerun()
        else:
            st.error("Name or email not found in the database. Access denied.")
