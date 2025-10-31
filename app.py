import streamlit as st
import json, os
from datetime import datetime

# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="Queue Management System", page_icon="🎟️", layout="wide")

USER_FILE  = "users.json"
QUEUE_FILE = "queue_data.json"

# -------------------- UTIL FUNCTIONS --------------------
def ensure_file(path, default):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f)

def load_json(path):
    ensure_file(path, [])
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# -------------------- QUEUE LOGIC --------------------
def add_to_queue(name, age, category, notes, email):
    data = load_json(QUEUE_FILE)
    token = data[-1]["token"] + 1 if data else 1
    now = datetime.now().strftime("%I:%M:%S %p")
    entry = {
        "token": token,
        "name": name.strip(),
        "age": int(age),
        "category": category,
        "notes": notes.strip(),
        "entered": now,
        "start": "",
        "end": "",
        "status": "Waiting",
        "user": email
    }
    data.append(entry)
    save_json(QUEUE_FILE, data)
    return token

def update_status(token, status):
    data = load_json(QUEUE_FILE)
    for p in data:
        if p["token"] == token:
            if status == "In Progress" and not p["start"]:
                p["start"] = datetime.now().strftime("%I:%M:%S %p")
            if status == "Completed" and not p["end"]:
                p["end"] = datetime.now().strftime("%I:%M:%S %p")
            p["status"] = status
            break
    save_json(QUEUE_FILE, data)

# -------------------- LOGIN / REGISTER --------------------
def smart_login(email, pwd):
    users = load_json(USER_FILE)
    for u in users:
        if u["email"].lower() == email.lower() and u["password"] == pwd:
            return "login"
    if any(u["email"].lower() == email.lower() for u in users):
        return "wrong_password"
    users.append({"email": email, "password": pwd})
    save_json(USER_FILE, users)
    return "registered"

# -------------------- SESSION STORE --------------------
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""

# -------------------- LOGIN PAGE --------------------
if not st.session_state.auth:

    st.markdown("""
    <style>
    body, .stApp {
        background: url("https://raw.githubusercontent.com/Chaitanya081/virtual_queue_system-/main/assets1/login_bg.jpg") no-repeat center center fixed !important;
        background-size: cover !important;
        font-family: 'Segoe UI', sans-serif;
    }

    .login-container {
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        flex-direction:column;
    }

    .login-box {
        width:420px;
        padding:35px;
        background:rgba(255,255,255,0.65);
        border-radius:12px;
        box-shadow:0 8px 25px rgba(0,0,0,0.3);
        text-align:center;
        backdrop-filter:blur(8px);
    }

    .login-title {
        font-size:32px;
        font-weight:900;
        color:#004b8d;
        margin-bottom:15px;
    }

    input {
        background:white !important;
        border-radius:6px !important;
        height:40px;
    }

    .stButton>button {
        width:100%;
        background:#0e8e6c;
        color:white;
        font-weight:bold;
        padding:10px;
        border-radius:6px;
        border:none;
        margin-top:10px;
    }
    .stButton>button:hover {
        background:#0b775a;
    }

    .footer {
        position:absolute;
        bottom:10px;
        width:100%;
        text-align:center;
        color:white;
        font-size:13px;
        text-shadow:1px 1px 2px black;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-container"><div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Queue Management System</div>', unsafe_allow_html=True)

    email = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("LOGIN"):
        if not email or not pwd:
            st.warning("⚠ Enter username & password")
        else:
            result = smart_login(email, pwd)
            if result in ("login", "registered"):
                st.session_state.auth = True
                st.session_state.user = email
                st.rerun()
            else:
                st.error("❌ Incorrect Password")

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown('<div class="footer">© 2024 Queue Management System | All Rights Reserved</div>',
                unsafe_allow_html=True)

    st.stop()

# -------------------- APP SIDEBAR --------------------
st.sidebar.success(f"Logged in as: {st.session_state.user}")

menu = st.sidebar.radio("Menu", ["Dashboard", "User Queue", "Staff Console", "Logout"])

if menu == "Logout":
    st.session_state.clear()
    st.rerun()

st.markdown("<h2 style='text-align:center;'>🎟 Virtual Queue Management System</h2>", unsafe_allow_html=True)

# -------------------- DASHBOARD --------------------
if menu == "Dashboard":
    data = load_json(QUEUE_FILE)
    total=len(data)
    wait=sum(1 for x in data if x["status"]=="Waiting")
    prog=sum(1 for x in data if x["status"]=="In Progress")
    done=sum(1 for x in data if x["status"]=="Completed")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Tokens", total)
    c2.metric("Waiting", wait)
    c3.metric("In Progress", prog)
    c4.metric("Completed", done)

    st.write("### Recent Activity")
    for p in data[-8:][::-1]:
        st.success(f"#{p['token']} {p['name']} | {p['category']} | {p['status']} | {p['entered']}")

# -------------------- USER QUEUE PAGE --------------------
elif menu == "User Queue":
    st.subheader("🧾 Generate Token")

    with st.form("queue_form"):
        name = st.text_input("Full Name")
        age  = st.number_input("Age", 1, 120)
        category = st.selectbox("Service", ["General", "Billing", "Consultation"])
        notes = st.text_area("Reason / Symptoms")
        go = st.form_submit_button("Get Token")

    if go:
        if not name:
            st.error("⚠ Name required")
        else:
            token = add_to_queue(name, age, category, notes, st.session_state.user)
            st.success(f"✅ Token #{token} issued")

    st.write("### Current Queue")
    for p in load_json(QUEUE_FILE):
        if p["status"]=="Waiting":
            st.warning(f"#{p['token']} {p['name']} ({p['age']}) - {p['category']} | {p['entered']}")

# -------------------- STAFF PANEL --------------------
elif menu == "Staff Console":
    st.subheader("🧑‍⚕️ Staff Console")
    data = load_json(QUEUE_FILE)

    st.write("### Waiting")
    for p in [x for x in data if x["status"]=="Waiting"]:
        c1,c2,c3 = st.columns([3,1,1])
        c1.write(f"#{p['token']} {p['name']} ({p['age']}) - {p['category']}")
        if c2.button("Start", key="s"+str(p["token"])):
            update_status(p["token"], "In Progress"); st.rerun()
        if c3.button("Cancel", key="c"+str(p["token"])):
            update_status(p["token"], "Cancelled"); st.rerun()

    st.write("### In Progress")
    for p in [x for x in data if x["status"]=="In Progress"]:
        c1,c2 = st.columns([3,1])
        c1.write(f"#{p['token']} {p['name']} | Start: {p['start']}")
        if c2.button("Finish", key="f"+str(p["token"])):
            update_status(p["token"], "Completed"); st.rerun()
