import streamlit as st
import json, os
from datetime import datetime

# ───────────────────────────── App Config ─────────────────────────────
st.set_page_config(page_title="Virtual Queue Management System", page_icon="🎟️", layout="wide")
USER_FILE  = "users.json"
QUEUE_FILE = "queue_data.json"

# ───────────────────────────── Storage Utils ──────────────────────────
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

# ───────────────────────────── Queue Logic ────────────────────────────
def add_to_queue(name, age, category, notes, email):
    data = load_json(QUEUE_FILE)
    token = (data[-1]["token"] + 1) if data else 1
    now = datetime.now().strftime("%I:%M:%S %p")
    entry = {
        "token": token,
        "name": name.strip(),
        "age": int(age),
        "category": category,
        "notes": notes.strip(),
        "entered": now,         # time joined queue
        "start": "",            # time service started
        "end": "",              # time service finished
        "status": "Waiting",    # Waiting | In Progress | Completed | Cancelled
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

# ───────────────────────────── Dark Theme CSS ─────────────────────────
st.markdown("""
<style>
  .stApp { background:#0e1117; color:#f6f7f9; }
  section[data-testid="stSidebar"]{ background:#17191f; }
  .title{ font-size:32px; font-weight:800; text-align:center; margin:6px 0 12px; }
  .metric-card{ background:#151821; border:1px solid #222532; border-radius:12px; padding:14px; }
  .queue{ background:#1a1c23; border-left:5px solid #1f77b4; border-radius:10px; padding:12px; margin-bottom:8px; }
  .stButton>button{ background:#1f77b4; color:#fff; border:none; border-radius:10px; padding:9px 18px; font-weight:600; }
  .stButton>button:hover{ background:#125f93; }
  input, textarea, select { background:#262730 !important; color:#fff !important; }
</style>
""", unsafe_allow_html=True)

# ───────────────────────────── Session Init ───────────────────────────
ensure_file(USER_FILE, [])
ensure_file(QUEUE_FILE, [])

if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""

# ───────────────────── Smart Login (auto-register) ───────────────────
def smart_login(email, pwd):
    users = load_json(USER_FILE)
    # existing correct creds → login
    for u in users:
        if u["email"].lower() == email.lower() and u["password"] == pwd:
            return "login"
    # email exists but wrong password → block
    if any(u["email"].lower() == email.lower() for u in users):
        return "wrong_password"
    # new email → register and login
    users.append({"email": email, "password": pwd})
    save_json(USER_FILE, users)
    return "registered"

if not st.session_state.auth:
    st.markdown("<div class='title'>🔐 Login / Register</div>", unsafe_allow_html=True)
    with st.form("auth_form", clear_on_submit=False):
        email = st.text_input("Email")
        pwd   = st.text_input("Password", type="password")
        go    = st.form_submit_button("Continue ➜")
    if go:
        if not email or not pwd:
            st.warning("Please enter both email and password.")
        else:
            res = smart_login(email, pwd)
            if res in ("login", "registered"):
                st.session_state.auth = True
                st.session_state.user = email
                st.rerun()
            else:
                st.error("Wrong password for this email.")
    st.stop()

# ───────────────────────────── Main App ───────────────────────────────
st.sidebar.success(f"Logged in as: {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["Dashboard", "User Queue", "Staff Console", "Logout"])

if menu == "Logout":
    st.session_state.clear()
    st.rerun()

st.markdown("<div class='title'>🎟 Virtual Queue Management System</div>", unsafe_allow_html=True)

# ───────────────────────────── Dashboard ──────────────────────────────
if menu == "Dashboard":
    data = load_json(QUEUE_FILE)
    total = len(data)
    waiting = sum(1 for x in data if x["status"] == "Waiting")
    active = sum(1 for x in data if x["status"] == "In Progress")
    done   = sum(1 for x in data if x["status"] == "Completed")

    c1, c2, c3, c4 = st.columns(4)
    for c, label, val in [
        (c1, "Total Tokens", total),
        (c2, "Waiting", waiting),
        (c3, "In Progress", active),
        (c4, "Completed", done),
    ]:
        with c:
            st.markdown(f"<div class='metric-card'><h4>{label}</h4><h2>{val}</h2></div>", unsafe_allow_html=True)

    st.markdown("### Recent Activity")
    if data:
        for p in data[-10:][::-1]:
            st.markdown(
                f"<div class='queue'><b>#{p['token']}</b> — {p['name']} · {p['category']} "
                f"· <b>{p['status']}</b> &nbsp; "
                f"<small>⏰ {p['entered']} {('→ '+p['start']) if p['start'] else ''} "
                f"{('→ '+p['end']) if p['end'] else ''}</small></div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No activity yet. Go to **User Queue** to create your first token.")

# ───────────────────────────── User Queue ─────────────────────────────
elif menu == "User Queue":
    st.subheader("🧾 Join Queue")
    with st.form("queue_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full Name")
        age  = col1.number_input("Age", 1, 120)
        category = col2.selectbox("Service Type", ["General", "Billing", "Consultation", "Support"])
        notes    = col2.text_area("Notes / Reason")
        submit   = st.form_submit_button("Generate Token")
    if submit:
        if not name.strip():
            st.error("Name is required.")
        else:
            token = add_to_queue(name, age, category, notes, st.session_state.user)
            st.success(f"🎫 Token #{token} generated. Please wait to be called.")

    st.markdown("### ⏳ Current Waiting")
    for p in load_json(QUEUE_FILE):
        if p["status"] == "Waiting":
            st.markdown(
                f"<div class='queue'><b>Token {p['token']}</b> — {p['name']} ({p['age']}) · {p['category']}<br>"
                f"⏰ Entered: {p['entered']}<br><i>{p['notes']}</i></div>",
                unsafe_allow_html=True
            )

# ───────────────────────────── Staff Console ─────────────────────────
elif menu == "Staff Console":
    st.subheader("🧑‍💼 Manage Queue")
    data = load_json(QUEUE_FILE)
    if not data:
        st.info("No tokens yet.")
    else:
        cats = ["All"] + sorted({p["category"] for p in data})
        cat = st.selectbox("Filter by category", cats)
        view = [p for p in data if cat == "All" or p["category"] == cat]

        waiting = [p for p in view if p["status"] == "Waiting"]
        active  = [p for p in view if p["status"] == "In Progress"]

        st.markdown("#### 🕒 Waiting")
        if waiting:
            for p in waiting:
                c1, c2, c3 = st.columns([3,1,1])
                c1.write(f"Token {p['token']} — {p['name']} ({p['age']}) · {p['category']} · Entered {p['entered']}")
                if c2.button("Start", key=f"start_{p['token']}"):
                    update_status(p["token"], "In Progress"); st.rerun()
                if c3.button("Cancel", key=f"cancel_{p['token']}"):
                    update_status(p["token"], "Cancelled"); st.rerun()
        else:
            st.info("Nothing waiting.")

        st.markdown("#### ⚙️ In Progress")
        if active:
            for p in active:
                c1, c2 = st.columns([3,1])
                c1.write(f"Token {p['token']} — {p['name']} · Start: {p['start']}")
                if c2.button("Finish", key=f"finish_{p['token']}"):
                    update_status(p["token"], "Completed"); st.rerun()
        else:
            st.info("No active tokens.")

        st.markdown("#### ✅ Completed")
        completed = [p for p in view if p["status"] == "Completed"]
        if completed:
            for p in completed[-30:][::-1]:
                st.write(f"Token {p['token']} — {p['name']} · {p['start']} ➝ {p['end']}")
        else:
            st.info("No completed tokens yet.")
