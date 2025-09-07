import streamlit as st
from pymongo import MongoClient  # if not already imported
from db import patients_collection

def signup_page():
    st.title("📝 New Patient Registration")
    with st.form("signup_form", clear_on_submit=True):
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=0, max_value=120, step=1)
        gender = st.selectbox("Gender", ["male", "female", "other"])
        email = st.text_input("Email")
        conditions = st.text_area("Known Medical Conditions (comma-separated)")
        symptoms = st.text_area("Current Symptoms (comma-separated)")
        submitted = st.form_submit_button("Register")
        if submitted:
            if not all([name, email, conditions, symptoms]):
                st.warning("All fields are required.")
            else:
                existing = patients_collection.find_one({"email": email})
                if existing:
                    st.error("An account with this email already exists.")
                else:
                    patient = {
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "email": email,
                        "conditions": [c.strip() for c in conditions.split(",") if c.strip()],
                        "symptoms": [s.strip() for s in symptoms.split(",") if s.strip()],
                        "contact": None
                    }
                    patients_collection.insert_one(patient)
                    st.success("Patient registered successfully. You can now log in.")
