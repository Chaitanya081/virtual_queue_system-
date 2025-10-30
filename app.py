import streamlit as st
import json, os
from datetime import datetime

# ------------------------- CONFIG -------------------------
st.set_page_config(page_title="Virtual Queue System", page_icon="🎟️", layout="wide")

USER_FILE = "users.json"
QUEUE_FILE = "queue_data.json"

# ------------------------- UTIL FUNCTIONS -------------------------
def load(path):
    return json.load(open(path)) if os.path.exists(path) else []

def save(path, data):
    json.dump(data, open(path, "w"), indent=4)

def register(email, pwd):
    users = load(USER_FILE)
    if any(u["email"] == email for u in users):
        return False, "⚠ Email already exists"
    users.append({"email": email, "password": pwd})
    save(USER_FILE, users)
    return True, "✅ Registration successful!"

def login(email, pwd):
    return any(u["email"] == email and u["password"] == pwd for u in load(USER_FILE))

def add_to_queue(name, age, category, notes, email):
    data = load(QUEUE_FILE)
    token = len(data) + 1
    entry={
        "token": token, "name": name, "age": age, "category": category, "notes": notes,
        "entered": datetime.now().strftime("%I:%M:%S %p"),
        "start": "", "end": "", "status": "Waiting", "user": email
    }
    data.append(entry)
    save(QUEUE_FILE, data)
    return token

def update_status(token, status):
    data = load(QUEUE_FILE)
    for p in data:
        if p["token"] == token:
            if status=="In Progress": p["start"]=datetime.now().strftime("%I:%M:%S %p")
            if status=="Completed": p["end"]=datetime.now().strftime("%I:%M:%S %p")
            p["status"]=status
    save(QUEUE_FILE, data)

# ------------------------- DARK THEME STYLE -------------------------
st.markdown("""
<style>
.stApp { background:#0e1117; color:white; }
section[data-testid="stSidebar"] {background:#17191f;}
.stButton>button {background:#1f77b4;color:white;border-radius:8px;}
input,textarea,select {background:#262730!important;color:white!important;}
.queue {background:#1a1c23;padding:10px;border-radius:8px;
border-left:5px solid #1f77b4;margin-bottom:8px;}
.title{font-size:32px;text-align:center;font-weight:800;margin-bottom:10px}
</style>
""",unsafe_allow_html=True)

# ------------------------- SESSION -------------------------
if "auth" not in st.session_state: st.session_state.auth=False
if "user" not in st.session_state: st.session_state.user=""

# ------------------------- LOGIN / REGISTER -------------------------
if not st.session_state.auth:
    st.markdown("<div class='title'>🔐 Login / Register</div>",unsafe_allow_html=True)
    mode=st.radio("Select Mode",["Login","Register"])
    email=st.text_input("Email")
    pwd=st.text_input("Password",type="password")

    if mode=="Register":
        if st.button("Create Account"):
            ok,msg=register(email,pwd)
            st.success(msg) if ok else st.error(msg)
    else:
        if st.button("Login"):
            if login(email,pwd):
                st.session_state.auth=True; st.session_state.user=email; st.rerun()
            else: st.error("❌ Wrong email or password")
    st.stop()

# ------------------------- MAIN APP -------------------------
st.sidebar.success(f"✅ Logged in: {st.session_state.user}")

menu=st.sidebar.radio("Menu",["User Queue","Staff Console","Logout"])

if menu=="Logout":
    st.session_state.auth=False; st.rerun()

st.markdown("<div class='title'>🎟 Virtual Queue Management System</div>",unsafe_allow_html=True)

# ------------------------- USER QUEUE PAGE -------------------------
if menu=="User Queue":
    st.subheader("🧾 Join Queue")

    with st.form("f"):
        c1,c2=st.columns(2)
        name=c1.text_input("Name")
        age=c1.number_input("Age",1,120)
        category=c2.selectbox("Service Type",["General","Billing","Consultation","Support"])
        notes=c2.text_area("Notes")
        submit=st.form_submit_button("Generate Token")

        if submit:
            if name:
                t=add_to_queue(name,age,category,notes,st.session_state.user)
                st.success(f"🎫 Token #{t} generated")
            else: st.error("Enter name")

    st.subheader("⏳ Waiting")
    for p in load(QUEUE_FILE):
        if p["status"]=="Waiting":
            st.markdown(f"""
            <div class='queue'>
            <b>Token {p['token']}</b> - {p['name']} ({p['age']})<br>
            🕒 Entered: {p['entered']}<br>
            <i>{p['notes']}</i>
            </div>
            """,unsafe_allow_html=True)

# ------------------------- STAFF PAGE -------------------------
elif menu=="Staff Console":
    st.subheader("🧑‍💼 Manage Queue")

    data=load(QUEUE_FILE)
    waiting=[p for p in data if p["status"]=="Waiting"]
    active=[p for p in data if p["status"]=="In Progress"]

    st.write("🕒 **Waiting**")
    for p in waiting:
        c1,c2,c3=st.columns([3,1,1])
        c1.write(f"Token {p['token']} - {p['name']}")
        if c2.button("Start",key=f"s{p['token']}"):
            update_status(p["token"],"In Progress"); st.rerun()
        if c3.button("Cancel",key=f"c{p['token']}"):
            update_status(p["token"],"Cancelled"); st.rerun()

    st.write("⚙ **In Progress**")
    for p in active:
        c1,c2=st.columns([3,1])
        c1.write(f"Token {p['token']} - {p['name']} | Start: {p['start']}")
        if c2.button("Finish",key=f"f{p['token']}"):
            update_status(p["token"],"Completed"); st.rerun()

    st.write("✅ **Completed**")
    for p in data:
        if p["status"]=="Completed":
            st.write(f"Token {p['token']} - {p['name']} | {p['start']} ➝ {p['end']}")
