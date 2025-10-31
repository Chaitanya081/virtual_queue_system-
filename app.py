import streamlit as st
import json, os
from datetime import datetime

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Queue Management System", page_icon="🎟️", layout="wide")

# ✅ Remove default Streamlit padding, toolbar & white space
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.block-container {padding: 0 !important; margin: 0 !important;}
</style>
""", unsafe_allow_html=True)

USER_FILE = "users.json"
QUEUE_FILE = "queue_data.json"

# -------------------- STORAGE FUNCTIONS --------------------
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
        "token": token, "name": name, "age": int(age),
        "category": category, "notes": notes, "entered": now,
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

# -------------------- LOGIN LOGIC --------------------
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

# -------------------- SESSION --------------------
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""

# -------------------- LOGIN PAGE --------------------
if not st.session_state.auth:

    st.markdown("""
    <style>
    body, .stApp {
        background: url("https://raw.githubusercontent.com/Chaitanya081/virtual_queue_system-/main/assets1/login_bg.jpg")
        no-repeat center center fixed !important;
        background-size: cover !important;
        font-family: 'Segoe UI', sans-serif;
    }

    .login-wrapper {
        height:100vh; width:100%;
        display:flex; justify-content:center; align-items:center;
    }

    .login-card {
        width:420px; padding:35px;
        background:rgba(255,255,255,0.75);
        border-radius:12px; text-align:center;
        backdrop-filter:blur(10px);
        box-shadow:0 8px 25px rgba(0,0,0,0.25);
    }

    .login-title {
        font-size:30px; font-weight:900; color:#004b8d; margin-bottom:20px;
    }

    input {
        color:black !important;
    }

    .stTextInput>div>div>input {
        background:#ffffff !important;
        height:45px; border-radius:6px;
        font-size:15px; color:black !important;
    }

    .stButton>button {
        width:100%; background:#0e8e6c;
        color:white; padding:12px; border-radius:6px;
        font-weight:600; border:none;
    }

    .stButton>button:hover { background:#0b775a; }

    .footer {
        position:fixed; bottom:10px; width:100%;
        text-align:center; color:white; font-size:13px;
        text-shadow:1px 1px 2px black;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-wrapper"><div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Queue Management System</div>', unsafe_allow_html=True)

    email = st.text_input("Email", placeholder="Enter your email")
    pwd = st.text_input("Password", placeholder="Enter password", type="password")

    if st.button("Login"):
        if not email or not pwd:
            st.warning("⚠ Enter email & password")
        else:
            result = smart_login(email, pwd)
            if result in ("login","registered"):
                st.session_state.auth = True
                st.session_state.user = email
                st.rerun()
            else:
                st.error("❌ Incorrect password")

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown('<div class="footer">© 2024 Queue Management System</div>', unsafe_allow_html=True)
    st.stop()

# -------------------- SIDEBAR --------------------
st.sidebar.success(f"Logged in as: {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["Dashboard", "User Queue", "Staff Console", "Logout"])

if menu == "Logout":
    st.session_state.clear(); st.rerun()

st.markdown("<h2 style='text-align:center;'>🎟 Virtual Queue Management System</h2>", unsafe_allow_html=True)

# -------------------- DASHBOARD --------------------
if menu == "Dashboard":
    data = load_json(QUEUE_FILE)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total",len(data))
    c2.metric("Waiting",sum(1 for x in data if x["status"]=="Waiting"))
    c3.metric("In Progress",sum(1 for x in data if x["status"]=="In Progress"))
    c4.metric("Completed",sum(1 for x in data if x["status"]=="Completed"))

    st.write("### Recent Tokens")
    for p in data[-10:][::-1]:
        st.info(f"#{p['token']}  | {p['name']} | {p['category']} | {p['status']}")

# -------------------- USER MODE --------------------
elif menu == "User Queue":
    st.subheader("🧾 Get Token")

    with st.form("token_form"):
        name = st.text_input("Full Name")
        age = st.number_input("Age",1,120)
        category = st.selectbox("Service",["General","Consultation","Billing"])
        notes = st.text_area("Reason / Notes")
        submit = st.form_submit_button("Get Token")

    if submit:
        token = add_to_queue(name, age, category, notes, st.session_state.user)
        st.success(f"✅ Token #{token} Created")

    st.write("### Current Queue")
    for p in load_json(QUEUE_FILE):
        if p["status"]=="Waiting":
            st.warning(f"#{p['token']} - {p['name']} ({p['age']} yrs)")

# -------------------- STAFF MODE --------------------
elif menu == "Staff Console":
    st.subheader("🧑‍⚕️ Staff Console")

    data = load_json(QUEUE_FILE)

    st.write("### Waiting")
    for p in [x for x in data if x["status"]=="Waiting"]:
        c1,c2,c3 = st.columns([3,1,1])
        c1.write(f"#{p['token']} - {p['name']} ({p['age']} yrs)")
        if c2.button("Start", key=f"s{p['token']}"):
            update_status(p["token"],"In Progress"); st.rerun()
        if c3.button("Cancel", key=f"c{p['token']}"):
            update_status(p["token"],"Cancelled"); st.rerun()

    st.write("### In Progress")
    for p in [x for x in data if x["status"]=="In Progress"]:
        c1,c2 = st.columns([3,1])
        c1.write(f"#{p['token']} | {p['name']} | Start: {p['start']}")
        if c2.button("Finish", key=f"f{p['token']}"):
            update_status(p["token"],"Completed"); st.rerun()
