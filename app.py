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
                    # Filter for account creation logs
                    auth_records = df[df.iloc[:, 2].astype(str).str.strip() == "Account_Creation"]
                    
                    login_success = False
                    for _, row in auth_records.iterrows():
                        notes_field = str(row.iloc[3])
                        p_name = str(row.iloc[1])
                        
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
                        auth_records = df[df.iloc[:, 2].astype(str).str.strip() == "Account_Creation"]
                        for _, row in auth_records.iterrows():
                            notes_field = str(row.iloc[3])
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
    # --- DIGITAL CLOCK TIMER SYSTEM ---
    if 'login_time' not in st.session_state:
        st.session_state.login_time = time.time()
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = True
    if 'frozen_seconds' not in st.session_state:
        st.session_state.frozen_seconds = 0
    
    if st.session_state.timer_running:
        elapsed_seconds = int(time.time() - st.session_state.login_time)
    else:
        elapsed_seconds = st.session_state.frozen_seconds
    
    js_is_running = 'true' if st.session_state.timer_running else 'false'
    
    timer_html = f"""
    <script>
    var parentDoc = window.parent.document;
    var existingTimer = parentDoc.getElementById("fbisd-timer");
    var isRunning = {js_is_running};
    
    if (window.fbisdInterval) {{
        clearInterval(window.fbisdInterval);
    }}
    
    if (!existingTimer) {{
        existingTimer = parentDoc.createElement("div");
        existingTimer.id = "fbisd-timer";
        existingTimer.style.position = "fixed";
        existingTimer.style.top = "60px";
        existingTimer.style.right = "20px";
        existingTimer.style.backgroundColor = "#0f4d92";
        existingTimer.style.color = "#ffffff";
        existingTimer.style.padding = "10px 20px";
        existingTimer.style.fontSize = "24px";
        existingTimer.style.fontFamily = "'Courier New', Courier, monospace";
        existingTimer.style.fontWeight = "bold";
        existingTimer.style.borderRadius = "8px";
        existingTimer.style.boxShadow = "0 4px 6px rgba(0,0,0,0.2)";
        existingTimer.style.zIndex = "999999";
        parentDoc.body.appendChild(existingTimer);
    }}
    
    let totalSeconds = {elapsed_seconds};
    
    function updateDisplay(seconds) {{
        let hours = Math.floor(seconds / 3600);
        let minutes = Math.floor((seconds - (hours * 3600)) / 60);
        let secs = seconds % 60;
        let formattedMinutes = minutes < 10 ? "0" + minutes : minutes;
        let formattedSeconds = secs < 10 ? "0" + secs : secs;
        let display = formattedMinutes + ":" + formattedSeconds;
        if (hours > 0) {{
            let formattedHours = hours < 10 ? "0" + hours : hours;
            display = formattedHours + ":" + display;
        }}
        existingTimer.innerHTML = display;
    }}

    updateDisplay(totalSeconds);
    
    if (isRunning) {{
        existingTimer.style.backgroundColor = "#0f4d92"; 
        window.fbisdInterval = setInterval(function() {{
            totalSeconds++;
            updateDisplay(totalSeconds);
        }}, 1000);
    }} else {{
        existingTimer.style.backgroundColor = "#28a745"; 
        existingTimer.innerHTML = "🏁 " + existingTimer.innerHTML;
    }}
    </script>
    """
    components.html(timer_html, width=0, height=0)

    st.sidebar.markdown(f"### 🏃‍♂️ Squad Member: **{st.session_state.user}**")
    if st.sidebar.button("Leave Training / Log Out"):
        st.session_state.user = None
        if 'login_time' in st.session_state:
            del st.session_state.login_time
        st.rerun()

    # --- DYNAMIC NAVIGATION MENU ---
    tabs = ["📋 Daily Drills", "📝 The Hustle Log", "🏆 League Table"]
    
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = tabs[0]

    try:
        tab_index = tabs.index(st.session_state.active_tab)
    except ValueError:
        tab_index = 0

    menu = st.sidebar.radio("Tactics Board", tabs, index=tab_index)
    st.session_state.active_tab = menu

    # ---------------------------------------------------------
    # MODULE 1: DYNAMIC DRILLS 
    # ---------------------------------------------------------
    if menu == "📋 Daily Drills":
        st.header("Today's Tactical Training (45 Minutes)")
        subj = st.selectbox("Select your training session:", ["Math", "Reading", "Science"])
        
        if 'current_subj' not in st.session_state or st.session_state.current_subj != subj:
            st.session_state.current_subj = subj
            st.session_state.q_index = 0
            
        q_df = raw_q_df.copy()
        if not q_df.empty:
            q_df.columns = [str(c).strip().lower() for c in q_df.columns]
            s_col = "subject" if "subject" in q_df.columns else q_df.columns[0]
            q_df[s_col] = q_df[s_col].astype(str).str.strip().str.capitalize()
            pool = q_df[q_df[s_col] == subj.capitalize()]
        else:
            pool = pd.DataFrame()

        if pool.empty:
            st.warning(f"Coaching staff is uploading {subj} drills right now! Check back later.")
        else:
            total_qs = len(pool)
            
            c_col = "coach" if "coach" in pool.columns else pool.columns[1]
            txt_col = "concept_text" if "concept_text" in pool.columns else pool.columns[2]
            q_col = "question" if "question" in pool.columns else pool.columns[3]
            ca_col = "choice_a" if "choice_a" in pool.columns else pool.columns[4]
            cb_col = "choice_b" if "choice_b" in pool.columns else pool.columns[5]
            cc_col = "choice_c" if "choice_c" in pool.columns else pool.columns[6]
            cd_col = "choice_d" if "choice_d" in pool.columns else pool.columns[7]
            ans_col = "correct_answer" if "correct_answer" in pool.columns else pool.columns[8]
            exp_col = "explanation" if "explanation" in pool.columns else pool.columns[9]

            raw_active = pool.iloc[st.session_state.q_index].to_dict()
            
            st.markdown(f"**Drill {st.session_state.q_index + 1} of {total_qs}**")
            
            st.subheader(f"🧠 Chalk Talk with {raw_active[c_col]} (First 15 Minutes)")
            st.info(raw_active[txt_col])
            st.markdown("---")
            
            st.subheader("🎯 Match Time: The Quiz")
            st.write(raw_active[q_col])
            
            opts = [str(raw_active[ca_col]), str(raw_active[cb_col]), str(raw_active[cc_col]), str(raw_active[cd_col])]
            ans = st.radio("Pick your shot placement:", ["Select..."] + opts, key=f"ans_{subj}_{st.session_state.q_index}")
            
            if ans != "Select...":
                if ans == str(raw_active[ans_col]):
                    st.success("⚽ GOALLLL!!! Top-bins finish! You read the play perfectly.")
                else:
                    st.error("❌ SAVED BY THE KEEPER! Hit the woodwork.")
                    st.warning(f"📋 **Coach's Video Review Breakdown:** {raw_active[exp_col]}")
            
            st.markdown("---")
            
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                if st.button("⬅️ Previous", disabled=(st.session_state.q_index == 0), use_container_width=True):
                    st.session_state.q_index -= 1
                    st.rerun()
            with c2:
                if st.button("Next ➡️", disabled=(st.session_state.q_index >= total_qs - 1), use_container_width=True):
                    st.session_state.q_index += 1
                    st.rerun()
            with c3:
                if st.button("🏠 Home", use_container_width=True):
                    st.session_state.active_tab = "📋 Daily Drills"
                    st.session_state.current_subj = None
                    st.rerun()
            with c4:
                if st.button("✅ End Lesson", use_container_width=True):
                    st.session_state.timer_running = False
                    st.session_state.frozen_seconds = int(time.time() - st.session_state.login_time)
                    
                    elapsed_mins = max(1, int(st.session_state.frozen_seconds / 60))
                    send_to_db(st.session_state.user, subj, elapsed_mins, "Completed Daily Lesson Module")
                    load_from_db.clear()
                    
                    st.balloons()
                    st.success(f"🎉 **GOALLL! Incredible effort, {st.session_state.user}!**")
                    st.info(f"🏆 You just banked **{elapsed_mins} minutes** of pure brain-training. A true Thundercat never quits. Take a breather, hydrate, and we'll see you at the next session!")
                    
                    time.sleep(4)
                    st.session_state.active_tab = "🏆 League Table"
                    st.rerun()

    # ---------------------------------------------------------
    # MODULE 2: HUSTLE LOG
    # ---------------------------------------------------------
    elif menu == "📝 The Hustle Log":
        st.header("📋 The Off-Field Hustle Log")
        st.write("True professionals put in work even when the stadium cameras are turned off. Log your stats below!")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("🧹 Cleaning the Pitch")
            chore_txt = st.text_input("What chore did you complete? (e.g., Vacuumed):")
            if st.button("Log Chore Points") and chore_txt:
                send_to_db(st.session_state.user, "Chore", 1, chore_txt)
                load_from_db.clear()
                st.success("Top team player! Milestone added!")
                
        with c2:
            st.subheader("📚 Scouting Reports")
            book_txt = st.text_input("What book did you devour? (Builds reading muscle!):")
            if st.button("Log Reading Progress") and book_txt:
                send_to_db(st.session_state.user, "Book", 1, book_txt)
                load_from_db.clear()
                st.success("Expanding your playbook! Tracked successfully.")
                
        with c3:
            st.subheader("💪 Fitness & Conditioning")
            workout_mins = st.number_input("Minutes spent training today:", min_value=0, max_value=300, step=5)
            if st.button("Log Training Minutes") and workout_mins > 0:
                send_to_db(st.session_state.user, "Workout", workout_mins, "Athletic conditioning block")
                load_from_db.clear()
                st.success("Engine conditioning blocks posted!")

    # ---------------------------------------------------------
    # MODULE 3: LEADERBOARD SYSTEM
    # ---------------------------------------------------------
    elif menu == "🏆 League Table":
        st.header("🏆 The Academy League Table")
        log_df = load_from_db("get_logs")
        
        if log_df.empty or len(log_df.columns) < 4:
            st.info("No stats recorded on the pitch yet. Complete a training drill to break the ice!")
        else:
            p_idx = 1  
            a_idx = 2  
            v_idx = 3  
            
            summary = []
            unique_players = log_df.iloc[:, p_idx].dropna().astype(str).str.strip().unique()
            
            for player in unique_players:
                if player in ["None", "nan", "", "player", "Player", "timestamp", "Timestamp"]: 
                    continue
                if "-" in player and ":" in player or len(player) > 20 and ("202" in player):
                    continue
                
                pdf = log_df[log_df.iloc[:, p_idx].astype(str).str.strip() == player]
                
                study = 0
                chores = 0
                books = 0
                fitness = 0
                
                for _, row in pdf.iterrows():
                    act = str(row.iloc[a_idx]).strip().capitalize()
                    if act in ["Registration", "Account_creation"]:
                        continue
                        
                    try:
                        val = float(row.iloc[v_idx])
                    except:
                        val = 0.0
                        
                    if act in ["Math", "Reading", "Science"]:
                        study += val
                    elif act == "Chore":
                        chores += val
                    elif act == "Book":
                        books += val
                    elif act == "Workout":
                        fitness += val
                
                pts = study + fitness + (chores * 10) + (books * 20)
                
                if pts > 0 or study > 0 or fitness > 0:
                    summary.append({
                        "Player Squad Member 🏃‍♂️": str(player), 
                        "
