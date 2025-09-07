import streamlit as st
from db import patients_collection

def profile_page():
    st.title("👤 My Profile")

    if not st.session_state.get("email"):
        st.warning("You must be logged in to view this page.")
        return

    user = patients_collection.find_one({"email": st.session_state.email})

    if not user:
        st.error("User profile not found.")
        return

    # Pre-fill current values
    age = st.number_input("Age", min_value=0, max_value=120, value=user.get("age", 0), step=1)
    gender = st.selectbox("Gender", ["male", "female", "other"], index=["male", "female", "other"].index(user.get("gender", "other")))
    conditions = st.text_area("Known Medical Conditions (comma-separated)", value=", ".join(user.get("conditions", [])))
    symptoms = st.text_area("Current Symptoms (comma-separated)", value=", ".join(user.get("symptoms", [])))

    if st.button("💾 Update Profile"):
        updated_data = {
            "age": age,
            "gender": gender,
            "conditions": [c.strip() for c in conditions.split(",") if c.strip()],
            "symptoms": [s.strip() for s in symptoms.split(",") if s.strip()]
        }

        patients_collection.update_one(
            {"email": st.session_state.email},
            {"$set": updated_data}
        )
        st.success("✅ Profile updated successfully.")
