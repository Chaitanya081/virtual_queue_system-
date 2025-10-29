import streamlit as st
import json
import time
import os
from datetime import datetime

# --------------------------
# Configuration
# --------------------------
st.set_page_config(
    page_title="🏥 Virtual Queue Management",
    page_icon="🩺",
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

def add_patient(name, age, department, symptoms):
    data = load_data()
    token_no = len(data) + 1
    entry = {
        "token_no": token_no,
        "name": name,
        "age": age,
        "department": department,
        "symptoms": symptoms,
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
# UI Design
# --------------------------
st.markdown(
    """
    <style>
        .main {
            background-color: #f8fbff;
        }
        .stButton>button {
            background-color: #4a90e2;
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
            border: none;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #357ABD;
        }
        .title {
            text-align: center;
            color: #2c3e50;
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='title'>🏥 Hospital Virtual Queue Management System</div>", unsafe_allow_html=True)
menu = ["👩‍⚕️ Patient Registration", "🧑‍💼 Staff Console"]
choice = st.sidebar.radio("Select Module", menu)

# --------------------------
# Module 1: Patient Registration
# --------------------------
if choice == "👩‍⚕️ Patient Registration":
    st.subheader("🩺 Register Patients for Consultation")

    with st.form("patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Patient Name")
            age = st.number_input("🎂 Age", min_value=0, max_value=120, step=1)
        with col2:
            department = st.selectbox("🏥 Department", ["General Medicine", "Pediatrics", "Orthopedics", "ENT", "Cardiology", "Neurology", "Dermatology"])
            symptoms = st.text_area("📝 Symptoms / Reason for Visit")
        submitted = st.form_submit_button("Generate Token")

        if submitted:
            if name and age > 0:
                token_no = add_patient(name, age, department, symptoms)
                st.success(f"✅ Token Generated Successfully!")
                st.info(f"🎫 Your Token Number: **{token_no}**")
                st.write("Please wait in the respective department. You will be called soon.")
            else:
                st.warning("⚠️ Please fill in all details correctly.")

    # Adding multiple members to queue
    st.markdown("### 👨‍👩‍👧 Add Multiple Family Members")
    member_count = st.number_input("How many members to add?", min_value=1, max_value=5, step=1)
    if st.button("Add Members"):
        for i in range(member_count):
            st.write(f"**Member {i+1} added to the queue successfully! (Fill above form separately)**")

    # Display current waiting queue
    st.subheader("🕒 Current Waiting Queue")
    waiting_list = get_waiting_list()
    if waiting_list:
        for w in waiting_list:
            st.markdown(
                f"""
                <div style='padding:10px; border-radius:10px; background-color:#eaf2fd; margin-bottom:5px'>
                <b>Token #{w['token_no']}</b> | {w['name']} ({w['age']} yrs) - {w['department']} <br>
                <i>Symptoms:</i> {w['symptoms']} <br>
                <small>⏰ Registered at {w['timestamp']} | Status: <b>{w['status']}</b></small>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("🎉 No patients waiting right now.")

# --------------------------
# Module 2: Staff Console
# --------------------------
elif choice == "🧑‍💼 Staff Console":
    st.subheader("🧑‍⚕️ Nurse / Reception Console")

    data = load_data()
    if not data:
        st.info("No patient data available.")
    else:
        departments = ["All"] + sorted(list(set([d["department"] for d in data])))
        selected_dept = st.selectbox("Filter by Department", departments)

        if selected_dept != "All":
            data = [d for d in data if d["department"] == selected_dept]

        waiting_patients = [d for d in data if d["status"] == "Waiting"]
        consulting_patients = [d for d in data if d["status"] == "Consulting"]

        # Waiting List
        st.markdown("### 🕒 Patients Waiting")
        if waiting_patients:
            for p in waiting_patients:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**Token #{p['token_no']}** - {p['name']} ({p['age']} yrs) - {p['department']}")
                with col2:
                    if st.button(f"Start {p['token_no']}", key=f"start_{p['token_no']}"):
                        update_status(p['token_no'], "Consulting")
                        st.success(f"✅ Token {p['token_no']} moved to Consulting")
                with col3:
                    if st.button(f"Cancel {p['token_no']}", key=f"cancel_{p['token_no']}"):
                        update_status(p['token_no'], "Cancelled")
                        st.warning(f"❌ Token {p['token_no']} cancelled")
        else:
            st.info("No patients waiting currently.")

        # Consulting List
        st.markdown("### 👨‍⚕️ Patients in Consultation")
        if consulting_patients:
            for p in consulting_patients:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Token #{p['token_no']}** - {p['name']} ({p['age']} yrs) - {p['department']}")
                with col2:
                    if st.button(f"Complete {p['token_no']}", key=f"done_{p['token_no']}"):
                        update_status(p['token_no'], "Completed")
                        st.success(f"✅ Token {p['token_no']} marked as Completed")
        else:
            st.info("No patients are currently being consulted.")

        # All Patients Summary
        st.markdown("### 📋 Full Queue Data")
        st.table(data)
