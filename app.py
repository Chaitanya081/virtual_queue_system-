import streamlit as st
import json
import time
import os
from datetime import datetime

# --------------------------
# Basic Config
# --------------------------
st.set_page_config(
    page_title="Virtual Queue Management",
    page_icon="🎟️",
    layout="wide"
)

DATA_FILE = "queue_data.json"

# --------------------------
# Helper Functions
# --------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_person(name, age, category, notes):
    data = load_data()
    token_no = len(data) + 1
    entry = {
        "token_no": token_no,
        "name": name,
        "age": age,
        "category": category,
        "notes": notes,
        "status": "Waiting",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    data.append(entry)
    save_data(data)
    return token_no

def get_waiting_list():
    data = load_data()
    return [item for item in data if item["status"] == "Waiting"]

def update_status(token_no, new_status):
    data = load_data()
    for item in data:
        if item["token_no"] == token_no:
            item["status"] = new_status
            break
    save_data(data)

# --------------------------
# Modern UI Styling
# --------------------------
st.markdown(
    """
    <style>
        .stApp {
            background-color: #f4f9ff;
        }
        [data-base-theme="dark"] .stApp {
            background-color: #0f1116;
        }
        .title {
            text-align: center;
            font-size: 34px;
            font-weight: 800;
            color: #1a1a1a;
            margin-bottom: 15px;
        }
        [data-base-theme="dark"] .title {
            color: #f9fafc;
        }
        .stButton>button {
            background-color: #0066ff;
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 10px 20px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #004bcc;
        }
        .queue-card {
            padding: 15px;
            border-radius: 12px;
            background-color: rgba(220, 235, 255, 0.8);
            margin-bottom: 8px;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
            border-left: 6px solid #007bff;
        }
        [data-base-theme="dark"] .queue-card {
            background-color: rgba(255,255,255,0.05);
            border-left: 4px solid #4dabf7;
        }
        .queue-card small {
            color: #555;
        }
        [data-base-theme="dark"] .queue-card small {
            color: #ccc;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='title'>🎟️ Virtual Queue Management System</div>", unsafe_allow_html=True)
menu = ["👤 User Registration", "🧑‍💼 Staff Console"]
choice = st.sidebar.radio("Select Module", menu)

# --------------------------
# Module 1: User Registration
# --------------------------
if choice == "👤 User Registration":
    st.subheader("🧾 Register to Join the Queue")

    with st.form("queue_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=0, max_value=120, step=1)
        with col2:
            category = st.selectbox(
                "Select Service / Category",
                ["General Service", "Customer Support", "Billing", "Consultation", "Enquiry"]
            )
            notes = st.text_area("Additional Notes / Reason")
        submitted = st.form_submit_button("Generate Token")

        if submitted:
            if name and age > 0:
                token_no = add_person(name, age, category, notes)
                st.success("✅ Token Generated Successfully!")
                st.info(f"🎫 Your Token Number: **{token_no}**")
                st.write("Please wait for your turn. You will be called soon.")
            else:
                st.warning("⚠️ Please enter valid details before submitting.")

    # Add multiple members to queue
    st.markdown("### 👨‍👩‍👧 Add Multiple Members")
    member_count = st.number_input("How many members to add?", min_value=1, max_value=5, step=1)
    if st.button("Add Members"):
        for i in range(member_count):
            st.write(f"✅ Member {i+1} can now fill the registration form above individually.")

    # Display current queue
    st.subheader("⏳ Current Waiting Queue")
    waiting_list = get_waiting_list()
    if waiting_list:
        for w in waiting_list:
            st.markdown(
                f"""
                <div class="queue-card">
                <b>Token #{w['token_no']}</b> | {w['name']} ({w['age']} yrs) - {w['category']}<br>
                <i>Notes:</i> {w['notes']}<br>
                <small>🕒 Registered at {w['timestamp']} | Status: <b>{w['status']}</b></small>
                </div>
                """,
                unsafe_allow_html=True
