import streamlit as st
import json, os
from datetime import datetime

# -------------------------
# App Config
# -------------------------
st.set_page_config(page_title="Virtual Queue System", page_icon="🎟️", layout="wide")

QUEUE_FILE = "queue_data.json"
USER_FILE = "users.json"

# -------------------------
# Utilities
# -------------------------
def load_json(path):
    if not os.path.exists(path):
        return []
    return json.load(open(path, "r"))

def save_json(path, data):
    json.dump(data, open(path, "w"), indent=4)

def register_user(email, password):
    users = load_json(USER_FILE)
    for u in users:
        if u["email"] == email:
            return False, "Email already exists!"
    users.append({"email": email, "password": password})
    save_json(USER_FILE, users)
    return True, "Registration Successful!"

def login_user(email, password):
    users = load_json(USER_FILE)
    for u in users:
        if u["email"] == email and u["password"] == password:
            return True
    return False

def add_person(name, age, category, notes, user):
    data = load_json(QUEUE_FILE)
    token = len(data) + 1
    now = datetime.now().strftime("%I:%M:%S %p")
    entry = {
        "token": token,
        "name": name,
        "age": age,
        "category": category,
        "notes": notes,
        "entered_time": now,
        "start_time": "",
        "end_time": "",
        "status": "Waiting",
        "user": user
    }
    data.append(entry)
    save_json(QUEUE_FILE, data)
    return token

def update_status(token, new_status):
    data = load_json(QUEUE_FILE)
    for p in data:
        if p["token"] == token:
            if new_status == "In Progress":
                p["start_time"] = datetime.now().strftime("%I:%M:%S %p")
            if new_status == "Completed":
                p["end_time"] = datetime.now().strftime("%I:%M:%S %p")
            p["status"] = new_status
    save_json(QUEUE_FILE, data)

# -------------------------
# Dark Theme CSS
# -------------------------
st.markdown("""
<style>
.stApp {background-color:#0e1117; color:#fff;}
.title{text-align:center;font-size:32px;font-weight:800;}
.stButton>button{background:#1f77b4;color:white;border-radius:10px;padding:8px 18px;}
.queue-card{background:#1a1c23;padding:12px;border-left:5px solid #1f77b4;
border-radius:8px;margin-bottom:6px;}
input, textarea, select {background:#262730 !important; color:white !important;}
section[data-testid="stSidebar"] {background:#17191f;}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Session Init
# -------------------------
if "logged" not in st.session_state:
    st.session_state.logged = False
if "email" not in st.session_state:
    st.session_state.email = ""

# -------------------------
# Login & Register Page
# -------------------------
if not st.session_state.logged:
    st.markdown("<div class='title'>🔐 Login to Virtual Queue</div>", unsafe_allow_html=True)
    choice = st.radio("Select", ["Login", "Register"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Register":
        if st.button("Register"):
            ok, msg = register_user(email, password)
            st.success(msg) if ok else st.error(msg)

    else:
        if st.button("Login"):
            if login_user(email, password):
                st.session_state.logged = True
                st.session_state.email = email
                st.success("✅ Login Successful!")
                st.rerun()
            else:
                st.error("❌ Invalid Credentials")

    st.stop()

# -------------------------
# Logged-In Application
# -------------------------
st.sidebar.success(f"✅ Logged in: {st.session_state.email}")
menu = st.sidebar.radio("Menu", ["User Queue", "Staff Console", "Logout"])

# Logout
if menu == "Logout":
    st.session_state.logged = False
    st.session_state.email = ""
    st.rerun()

st.markdown("<div class='title'>🎟️ Virtual Queue Management System</div>", unsafe_allow_html=True)

# -------------------------
# User Queue
# -------------------------
if menu == "User Queue":
    st.header("🧾 Join the Queue")

    with st.form("queue"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full Name")
        age = col1.number_input("Age", 1, 120)
        category = col2.selectbox("Service Type",
                                  ["General", "Customer Support", "Billing", "Consultation", "Enquiry"])
        notes = col2.text_area("Notes")

        submit = st.form_submit_button("Generate Token")

        if submit:
            token = add_person(name, age, category, notes, st.session_state.email)
            st.success(f"🎫 Your Token: **{token}**")
            st.info("Please wait. Staff will call you.")

    st.subheader("⏳ Current Queue")
    queue = load_json(QUEUE_FILE)
    for p in queue:
        if p["status"] == "Waiting":
            st.markdown(f"""
            <div class='queue-card'>
            <b>Token {p['token']}</b> | {p['name']} ({p['age']} yrs) - {p['category']}<br>
            🕒 Entered: {p['entered_time']}<br>
            <i>Notes:</i> {p['notes']} 
            </div>
            """, unsafe_allow_html=True)

# -------------------------
# Staff Console
# -------------------------
elif menu == "Staff Console":
    st.header("🧑‍💼 Staff Console")

    data = load_json(QUEUE_FILE)
    waiting = [d for d in data if d["status"] == "Waiting"]
    active = [d for d in data if d["status"] == "In Progress"]

    st.subheader("🕒 Waiting")
    for p in waiting:
        col1, col2, col3 = st.columns([3,1,1])
        col1.write(f"Token {p['token']} - {p['name']} ({p['age']})")
        if col2.button("Start", key=f"start{p['token']}"):
            update_status(p["token"], "In Progress")
            st.rerun()
        if col3.button("Cancel", key=f"cancel{p['token']}"):
            update_status(p["token"], "Cancelled")
            st.rerun()

    st.subheader("⚙️ In Progress")
    for p in active:
        col1, col2 = st.columns([3,1])
        col1.write(f"Token {p['token']} - {p['name']} | Start: {p['start_time']}")
        if col2.button("Finish", key=f"finish{p['token']}"):
            update_status(p["token"], "Completed")
            st.rerun()

    st.subheader("✅ Completed")
    for p in data:
        if p["status"] == "Completed":
            st.write(f"Token {p['token']} - {p['name']} | ⏱ {p['start_time']} → {p['end_time']}")
