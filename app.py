import streamlit as st
import json, os
from datetime import datetime

# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="Queue Management System", page_icon="🎟️", layout="wide")

USER_FILE  = "users.json"
QUEUE_FILE = "queue_data.json"

# -------------------- FILE FUNCTIONS --------------------
def ensure_file(path, default):
    if not os.path.exists(path):
        with open(path, "w") as f: json.dump(default, f)

def load_json(path):
    ensure_file(path, [])
    with open(path, "r") as f: return json.load(f)

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f, indent=4)

# -------------------- QUEUE FUNCTIONS --------------------
def add_to_queue(name, age, category, notes, email):
    data = load_json(QUEUE_FILE)
    token = (data[-1]["token"] + 1) if data else 1
    now = datetime.now().strftime("%I:%M:%S %p")
    entry = {
        "token": token, "name": name.strip(), "age": int(age),
        "category": category, "notes": notes.strip(), "entered": now,
        "start": "", "end": "", "status": "Waiting", "user": email
    }
    data.append(entry); save_json(QUEUE_FILE, data)
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

# -------------------- STYLES --------------------
st.markdown("""
<style>
.stApp {background:#0e1117;color:#fff;}
section[data-testid="stSidebar"]{background:#17191f;}
.metric{padding:12px;background:#151821;border:1px solid #222532;border-radius:12px;text-align:center;}
.queue{background:#1a1c23;padding:12px;border-left:5px solid #1f77b4;border-radius:10px;margin-bottom:8px;}
.stButton>button{background:#1f77b4;color:white;border-radius:10px;padding:8px 16px;}
.stButton>button:hover{background:#125f93;}
input,textarea,select{background:#262730!important;color:white!important;}
.title{text-align:center;font-size:30px;font-weight:800;margin-top:5px;}
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION --------------------
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""

# -------------------- SMART LOGIN FUNCTION --------------------
def smart_login(email, pwd):
    users = load_json(USER_FILE)
    for u in users:
        if u["email"].lower() == email.lower() and u["password"] == pwd:
            return "login"
    if any(u["email"].lower() == email.lower() for u in users):
        return "wrong_password"
    users.append({"email": email, "password": pwd}); save_json(USER_FILE, users)
    return "registered"

# -------------------- LOGIN PAGE --------------------
if not st.session_state.auth:

    st.markdown("""
    <style>
    body, .stApp {
        background: url("https://raw.githubusercontent.com/Chaitanya081/virtual_queue_system-/main/assets1/login_bg.jpg") no-repeat center center fixed !important;
        background-size: cover !important;
        font-family: 'Segoe UI', sans-serif;
    }

    .login-wrapper {
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
    }

    .login-card {
        width:380px;
        padding:35px;
        border-radius:18px;
        backdrop-filter:blur(12px);
        background:rgba(255,255,255,0.12);
        border:1px solid rgba(255,255,255,0.25);
        box-shadow:0 8px 32px rgba(0,0,0,0.28);
        text-align:center;
    }

    .login-title {
        font-size:30px;
        font-weight:900;
        color:white;
        margin-bottom:5px;
    }

    .login-subtitle {
        color:#e8e8e8;
        font-size:14px;
        margin-bottom:22px;
    }

    .stTextInput>div>div>input {
        background:rgba(255,255,255,0.2)!important;
        color:white!important;
        border-radius:8px!important;
    }

    .stButton>button {
        width:100%;
        background-color:#1f77b4;
        color:white;
        padding:10px;
        border-radius:8px;
        font-weight:bold;
        border:none;
    }

    .stButton>button:hover {background-color:#0d5f92;}

    .forgot-pass {
        font-size:13px;
        color:#c8defb;
        margin-top:12px;
        text-decoration:underline;
        cursor:pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-wrapper"><div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Queue Management System ✅</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Secure Access Portal</div>', unsafe_allow_html=True)

    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")

    if st.button("Sign In / Register"):
        if not email or not pwd:
            st.warning("⚠ Enter email & password")
        else:
            result = smart_login(email, pwd)
            if result in ("login", "registered"):
                st.session_state.auth = True
                st.session_state.user = email
                st.rerun()
            else:
                st.error("❌ Incorrect Password")

    st.markdown('<p class="forgot-pass">Forgot Password?</p>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# -------------------- MAIN APP --------------------
st.sidebar.success(f"Logged in: {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["Dashboard","User Queue","Staff Console","Logout"])

if menu == "Logout":
    st.session_state.clear()
    st.rerun()

st.markdown("<div class='title'>🎟 Virtual Queue Management System</div>", unsafe_allow_html=True)

# -------------------- DASHBOARD --------------------
if menu=="Dashboard":
    data = load_json(QUEUE_FILE)
    total=len(data)
    wait=sum(1 for x in data if x["status"]=="Waiting")
    prog=sum(1 for x in data if x["status"]=="In Progress")
    done=sum(1 for x in data if x["status"]=="Completed")

    c1,c2,c3,c4=st.columns(4)
    c1.markdown(f"<div class='metric'><h3>Total</h3><h2>{total}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric'><h3>Waiting</h3><h2>{wait}</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric'><h3>Active</h3><h2>{prog}</h2></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric'><h3>Completed</h3><h2>{done}</h2></div>", unsafe_allow_html=True)

    st.markdown("### Recent Activity")
    for p in data[-8:][::-1]:
        st.markdown(
            f"<div class='queue'><b>#{p['token']}</b> {p['name']} - {p['category']}<br>"
            f"⏰ {p['entered']} ➜ {p['start']} ➜ {p['end']}</div>",
            unsafe_allow_html=True
        )

# -------------------- USER QUEUE --------------------
elif menu=="User Queue":
    st.subheader("🧾 Join Queue")

    with st.form("queue_form"):
        name = st.text_input("Full Name")
        age  = st.number_input("Age", 1,120)
        category = st.selectbox("Service Type",["General","Billing","Consultation","Support"])
        notes = st.text_area("Notes / reason")
        go = st.form_submit_button("Get Token")

    if go:
        if not name:
            st.error("⚠ Name required")
        else:
            token = add_to_queue(name,age,category,notes,st.session_state.user)
            st.success(f"✅ Token #{token} created")

    st.markdown("### ⏳ Waiting Queue")
    for p in load_json(QUEUE_FILE):
        if p["status"]=="Waiting":
            st.markdown(
                f"<div class='queue'><b>{p['token']}</b> {p['name']} ({p['age']})<br>⏱ {p['entered']}</div>",
                unsafe_allow_html=True
            )

# -------------------- STAFF CONSOLE --------------------
elif menu=="Staff Console":
    st.subheader("🧑‍⚕️ Staff Panel")
    data = load_json(QUEUE_FILE)

    wait = [p for p in data if p["status"]=="Waiting"]
    progress = [p for p in data if p["status"]=="In Progress"]

    st.write("### Waiting")
    for p in wait:
        c1,c2,c3 = st.columns([3,1,1])
        c1.write(f"#{p['token']} {p['name']} ({p['age']}) - {p['category']}")
        if c2.button("Start", key="start_"+str(p["token"])):
            update_status(p["token"],"In Progress"); st.rerun()
        if c3.button("Cancel", key="cancel_"+str(p["token"])):
            update_status(p["token"],"Cancelled"); st.rerun()

    st.write("### In Progress")
    for p in progress:
        c1,c2=st.columns([3,1])
        c1.write(f"#{p['token']} {p['name']} | Start: {p['start']}")
        if c2.button("Finish", key="finish_"+str(p["token"])):
            update_status(p["token"],"Completed"); st.rerun()
