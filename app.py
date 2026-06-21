import streamlit as st
import pandas as pd
import urllib.request
import json
import time
import hashlib
import streamlit.components.v1 as components

# App Setup & Theme Branding
st.set_page_config(page_title="Thornton Thundercats FC", page_icon="⚽", layout="wide")

# 🔌 PASTE YOUR GOOGLE WEB APP URL HERE INSIDE THE QUOTES
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxVA3RcQj8IQAShz3N3fc7KlaQkMzKjcOk2JMTZ-DjBchlUtPwDxVqX_BlHjexTDDaJNA/exec"

# Security Functions for Password Hashing
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# Use caching to prevent the app from freezing during database loads!
@st.cache_data(ttl=60)
def load_from_db(action="get_logs"):
    if not WEBAPP_URL or "YOUR_GOOGLE" in WEBAPP_URL:
        if action == "get_questions":
            return pd.DataFrame([
                {
                    "subject": "Math", 
                    "coach": "Striker Sam", 
                    "concept_text": "Shot accuracy rate is simply parts of a whole! Divide your shots on target by your total shots taken, then multiply by 100 to find your percentage.", 
                    "question": "Striker Sam takes 20 shots during a match against Katy ISD. 15 of them are directly on target. What is his shot accuracy percentage?", 
                    "choice_a": "60%", "choice_b": "70%", "choice_c": "75%", "choice_d": "80%", 
                    "correct_answer": "75%", 
                    "explanation": "15 out of 20 shots is the fraction 15/20. If you simplify that down, it becomes 3/4. Think of quarters: three quarters equals 75%!"
                },
                {
                    "subject": "Math", 
                    "coach": "Defender Dani", 
                    "concept_text": "Proportions state that two fractions or ratios are completely equal to each other!", 
                    "question": "If the Thundercats offense scores 3 goals every 20 minutes, how many goals will they score in a 60-minute game?", 
                    "choice_a": "6 goals", "choice_b": "9 goals", "choice_c": "12 goals", "choice_d": "15 goals", 
                    "correct_answer": "9 goals", 
                    "explanation": "3/20 = X/60. Multiply by 3! 3 x 3 = 9 goals!"
                }
            ])
        if 'mock_db' not in st.session_state:
            st.session_state.mock_db = []
        return pd.DataFrame(st.session_state.mock_db)
    
    try:
        url = f"{WEBAPP_URL}?action={action}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            raw_data = json.loads(response.read().decode('utf-8'))
        return pd.DataFrame(raw_data)
    except Exception as e:
        return pd.DataFrame()

def send_to_db(player, activity, value, notes):
    if not WEBAPP_URL or "YOUR_GOOGLE" in WEBAPP_URL:
        if 'mock_db' not in st.session_state:
            st.session_state.mock_db = []
        st.session_state.mock_db.append({"player": player, "activity": activity, "value": value, "notes": notes})
        return True
    try:
        payload = {"player": player, "activity": activity, "value": value, "notes": notes}
        req = urllib.request.Request(
            WEBAPP_URL, 
            data=json.dumps(payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response:
            return True
    except:
        return False

if 'user' not in st.session_state:
    st.session_state.user = None

# --- HEADER APP BANNER ---
st.title("⚽ Thornton Thundercats FC: Summer Academic Cup")
st.write("Welcome to the Academy! Train your brain with our All-Pro coaches, log your daily hustle, and dominate the district league standings.")

raw_q_df = load_from_db("get_questions")

# --- LOGIN & REGISTRATION SYSTEM ---
if not st.session_state.user:
    st.subheader("🔐 Locker Room Check-In")
    
    tab1, tab2 = st.tabs(["📋 Log In (Returning Players)", "📝 Sign Up (New Players)"])
    
    # 1. LOG IN TAB
    with tab1:
        with st.form("login_form"):
            st.write("Welcome back! Enter your credentials to hit the pitch.")
            log_email = st.text_input("Email Address").strip().lower()
            log_pass = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Log In")
            
            if submit_login and log_email and log_pass:
                df = load_from_db("get_logs")
                
                if df.empty or len(df.columns) < 4:
                    st.error("Database connection error or no users registered yet.")
                else:
                    # Filter for account creation logs (bulletproof string matching)
                    auth_records = df[df.iloc[:, 2].astype(str).str.strip().str.lower() == "account_creation"]
                    
                    login_success = False
                    for _, row in auth_records.iterrows():
                        # Bulletproof search: scan the entire row for our security marker
                        notes_field = ""
                        for item in row.values:
                            if isinstance(item, str) and "::" in item:
                                notes_field = item
                                break
                                
                        p_name = str(row.iloc[1]) # Player name is always index 1
                        
                        if "::" in notes_field:
                            stored_email, stored_hash = notes_field.split("::", 1)
                            if stored_email == log_email and check_hashes(log_pass, stored_hash):
                                st.session_state.user = p_name
                                st.session_state.login_time = time.time()
                                st.session_state.timer_running = True
                                st.session_state.frozen_seconds = 0
                                st.rerun()
                                login_success = True
                                break
                    
                    if not login_success:
                        st.error("❌ Incorrect email or password. Check your spelling or sign a new contract!")

    # 2. SIGN UP TAB
    with tab2:
        with st.form("signup_form"):
            st.write("First time here? Sign your rookie contract below!")
            new_email = st.text_input("Email Address").strip().lower()
            new_name = st.text_input("Player Name (Shows on Leaderboard)").strip()
            new_pass = st.text_input("Create a Password", type="password")
            submit_signup = st.form_submit_button("Sign the Contract")
            
            if submit_signup:
                if not new_email or not new_name or len(new_pass) < 4:
                    st.warning("Please fill out all fields. Passwords must be at least 4 characters!")
                else:
                    df = load_from_db("get_logs")
                    email_exists = False
                    name_exists = False
                    
                    if not df.empty and len(df.columns) >= 4:
                        auth_records = df[df.iloc[:, 2].astype(str).str.strip().str.lower() == "account_creation"]
                        for _, row in auth_records.iterrows():
                            # Bulletproof search: scan the entire row for our security marker
                            notes_field = ""
                            for item in row.values:
                                if isinstance(item, str) and "::" in item:
                                    notes_field = item
                                    break
                                    
                            p_name = str(row.iloc[1])
                            
                            if "::" in notes_field:
                                stored_email, _ = notes_field.split("::", 1)
                                if stored_email == new_email:
                                    email_exists = True
                                if p_name.lower() == new_name.lower():
                                    name_exists = True
                                    
                    if email_exists:
                        st.error("⚠️ An account with this email already exists. Head over to the Log In tab!")
                    elif name_exists:
                        st.error("⚠️ This Player Name is already taken. Pick a unique nickname for the squad!")
                    else:
                        hashed_p = make_hashes(new_pass)
                        # We securely store the email and hashed password inside the 'notes' column
                        send_to_db(new_name, "Account_Creation", 0, f"{new_email}::{hashed_p}")
                        st.success(f"✅ Contract signed! Welcome to the squad, {new_name}. You can now use the 'Log In' tab to enter the facility.")
                        load_from_db.clear() # Clear cache so they can immediately log in

else:
