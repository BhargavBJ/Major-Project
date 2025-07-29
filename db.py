import streamlit as st
from pymongo import MongoClient
import certifi

# Use secrets from Streamlit Cloud
MONGO_URI = st.secrets["MONGO_URI"]

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

# Define your database and collections
db = client["medicare_agent"]
patients_collection = db["patients"]
alerts_collection = db["alerts"]
appointments_collection = db["appointments"]
records_collection = db["records"]
reminders_collection = db["reminders"]
risk_collection = db["risk_predictions"]
vision_collection = db["vision_insights"]

# Optional connection check (commented for production use)
# try:
#     client.admin.command("ping")
#     print("✅ Successfully connected to MongoDB!")
# except Exception as e:
#     print("❌ Failed to connect to MongoDB:", e)
