import streamlit as st
import json, os
from datetime import datetime

# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="Virtual Queue System", page_icon="🎟️", layout="wide")

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

# -------------------- DARK THEME STYLE --------------------
st.markdown("""
<style>
.stApp {background:#0e1117;color:#fff;}
section[data-testid="stSidebar"] {background:#17191f;}
.metric {padding:12px;background:#151821;border:1px solid #222532;border-radius:12px;text-align:center;}
.queue {background:#1a1c23;padding:12px;border-left:5px solid #1f77b4;border-radius:10px;margin-bottom:8px;}
.stButton>button {background:#1f77b4;color:white;border-radius:10px;padding:8px 16px;}
.stButton>button:hover {background:#125f93;}
input,textarea,select {background:#262730!important;color:white!important;}
.title {text-align:center;font-size:30px;font-weight:800;margin-top:5px;}
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION --------------------
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""

# -------------------- SMART LOGIN --------------------
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

    st.markdown(f"""
    <style>
    .login-container{{display:flex;height:100vh;width:100%;}}
    .left-side {{
        flex:1;
        background-image:url("https://raw.githubusercontent.com/Chaitanya081/virtual_queue_system-/main/assets1/login_bg.jpg");
        background-size:cover;
        background-position:center;
    }}
    .right-side {{
        flex:1;background:#0e1117;padding:70px;
        display:flex;flex-direction:column;justify-content:center;
    }}
    .login-title {{
        font-size:32px;font-weight:800;color:white;margin-bottom:20px;
    }}
    </style>

    <div class="login-container">
        <div class="left-side"></div>
        <div class="right-side">
            <div class="login-title">🔐 Login / Register</div>
    """, unsafe_allow_html=True)

    email = st.text_input("Email")
    pwd   = st.text_input("Password", type="password")

    if st.button("Continue ➜"):
        if not email or not pwd:
            st.warning("⚠ Enter email & password")
        else:
            result = smart_login(email, pwd)
            if result in ("login", "registered"):
                st.session_state.auth = True; st.session_state.user = email; st.rerun()
            else:
                st.error("❌ Wrong password")

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# -------------------- SIDEBAR --------------------
st.sidebar.success(f"Logged in: {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["Dashboard","User Queue","Staff Console","Logout"])

if menu == "Logout":
    st.session_state.clear()
    st.rerun()

st.markdown("<div class='title'>🎟 Virtual Queue Management System</div>", unsafe_allow_html=True)

# -------------------- DASHBOARD --------------------
if menu=="Dashboard":
    data = load_json(QUEUE_FILE)
    total = len(data)
    wait  = sum(1 for x in data if x["status"]=="Waiting")
    prog  = sum(1 for x in data if x["status"]=="In Progress")
    done  = sum(1 for x in data if x["status"]=="Completed")

    c1,c2,c3,c4 = st.columns(4)
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
            st.markdown(f"<div class='queue'><b>{p['token']}</b> {p['name']} ({p['age']})<br>⏱ {p['entered']}</div>",
                        unsafe_allow_html=True)

# -------------------- STAFF CONSOLE --------------------
elif menu=="Staff Console":
    st.subheader("🧑‍⚕️ Staff Panel")
    data = load_json(QUEUE_FILE)
    
    wait = [p for p in data if p["status"]=="Waiting"]
    progress  = [p for p in data if p["status"]=="In Progress"]

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
        c1,c2 = st.columns([3,1])
        c1.write(f"#{p['token']} {p['name']} | Start: {p['start']}")
        if c2.button("Finish", key="finish_"+str(p["token"])):
            update_status(p["token"],"Completed"); st.rerun()
