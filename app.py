import streamlit as st
import pandas as pd
import urllib.request
import json
import time
import streamlit.components.v1 as components

# App Setup & Theme Branding
st.set_page_config(page_title="Thornton Thundercats FC", page_icon="⚽", layout="wide")

# 🔌 PASTE YOUR GOOGLE WEB APP URL HERE INSIDE THE QUOTES
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxVA3RcQj8IQAShz3N3fc7KlaQkMzKjcOk2JMTZ-DjBchlUtPwDxVqX_BlHjexTDDaJNA/exec"

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

# --- LOGIN SCREEN SYSTEM ---
if not st.session_state.user:
    st.subheader("🔐 Locker Room Check-In")
    with st.form("login"):
        name = st.text_input("Enter your Locker Room Name (e.g., ClinicalCole):").strip()
        if st.form_submit_button("Sign the Contract") and name:
            st.session_state.user = name
            st.session_state.login_time = time.time()
            send_to_db(name, "Registration", 0, "Signed with the club roster")
            st.rerun()
else:
    # --- DIGITAL CLOCK TIMER SYSTEM ---
    if 'login_time' not in st.session_state:
        st.session_state.login_time = time.time()
    
    elapsed_seconds = int(time.time() - st.session_state.login_time)
    
    timer_html = f"""
    <script>
    var parentDoc = window.parent.document;
    var existingTimer = parentDoc.getElementById("fbisd-timer");
    
    if (!existingTimer) {{
        var timerDiv = parentDoc.createElement("div");
        timerDiv.id = "fbisd-timer";
        timerDiv.style.position = "fixed";
        timerDiv.style.top = "60px";
        timerDiv.style.right = "20px";
        timerDiv.style.backgroundColor = "#0f4d92";
        timerDiv.style.color = "#ffffff";
        timerDiv.style.padding = "10px 20px";
        timerDiv.style.fontSize = "24px";
        timerDiv.style.fontFamily = "'Courier New', Courier, monospace";
        timerDiv.style.fontWeight = "bold";
        timerDiv.style.borderRadius = "8px";
        timerDiv.style.boxShadow = "0 4px 6px rgba(0,0,0,0.2)";
        timerDiv.style.zIndex = "999999";
        timerDiv.innerHTML = "00:00";
        parentDoc.body.appendChild(timerDiv);
        
        let totalSeconds = {elapsed_seconds};
        
        setInterval(function() {{
            totalSeconds++;
            let hours = Math.floor(totalSeconds / 3600);
            let minutes = Math.floor((totalSeconds - (hours * 3600)) / 60);
            let seconds = totalSeconds - (hours * 3600) - (minutes * 60);

            let formattedMinutes = minutes < 10 ? "0" + minutes : minutes;
            let formattedSeconds = seconds < 10 ? "0" + seconds : seconds;
            
            let display = formattedMinutes + ":" + formattedSeconds;
            
            if (hours > 0) {{
                let formattedHours = hours < 10 ? "0" + hours : hours;
                display = formattedHours + ":" + display;
            }}
            
            parentDoc.getElementById("fbisd-timer").innerHTML = display;
        }}, 1000);
    }}
    </script>
    """
    components.html(timer_html, width=0, height=0)

    st.sidebar.markdown(f"### 🏃‍♂️ Squad Member: **{st.session_state.user}**")
    if st.sidebar.button("Leave Training"):
        st.session_state.user = None
        if 'login_time' in st.session_state:
            del st.session_state.login_time
        st.rerun()

    # Link the menu strictly to session state so buttons can control navigation
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "📋 Daily Drills"

    menu = st.sidebar.radio(
        "Tactics Board", 
        ["📋 Daily Drills", "📝 The Hustle Log", "🏆 League Table"],
        key="active_tab"
    )

    # ---------------------------------------------------------
    # MODULE 1: DYNAMIC DRILLS (WITH NEW NAVIGATION SYSTEM)
    # ---------------------------------------------------------
    if menu == "📋 Daily Drills":
        st.header("Today's Tactical Training (45 Minutes)")
        subj = st.selectbox("Select your training session:", ["Math", "Reading", "Science"])
        
        # State Tracking for Question Index
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
            
            # Map columns dynamically
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
            
            # Unique key so the radio button resets when moving to the next question
            ans = st.radio("Pick your shot placement:", ["Select..."] + opts, key=f"ans_{subj}_{st.session_state.q_index}")
            
            if ans != "Select...":
                if ans == str(raw_active[ans_col]):
                    st.success("⚽ GOALLLL!!! Top-bins finish! You read the play perfectly.")
                else:
                    st.error("❌ SAVED BY THE KEEPER! Hit the woodwork.")
                    st.warning(f"📋 **Coach's Video Review Breakdown:** {raw_active[exp_col]}")
            
            st.markdown("---")
            
            # --- NAVIGATION BUTTON ROW ---
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
                if st.button("🏠 End Section", use_container_width=True):
                    st.session_state.active_tab = "🏆 League Table"
                    st.rerun()
            with c4:
                if st.button("✅ End Lesson for Day", use_container_width=True):
                    # Calculate minutes from login time, defaulting to at least 1 minute
                    elapsed_mins = max(1, int((time.time() - st.session_state.login_time) / 60))
                    send_to_db(st.session_state.user, subj, elapsed_mins, f"Completed Daily Lesson Module")
                    st.success(f"Great Hustle! {elapsed_mins} minutes successfully logged to the database!")
                    time.sleep(2) # Give the student 2 seconds to read the success message
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
                st.success("Top team player! Milestone added!")
                
        with c2:
            st.subheader("📚 Scouting Reports")
            book_txt = st.text_input("What book did you devour? (Builds reading muscle!):")
            if st.button("Log Reading Progress") and book_txt:
                send_to_db(st.session_state.user, "Book", 1, book_txt)
                st.success("Expanding your playbook! Tracked successfully.")
                
        with c3:
            st.subheader("💪 Fitness & Conditioning")
            workout_mins = st.number_input("Minutes spent training today:", min_value=0, max_value=300, step=5)
            if st.button("Log Training Minutes") and workout_mins > 0:
                send_to_db(st.session_state.user, "Workout", workout_mins, "Athletic conditioning block")
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
                    if act == "Registration":
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
                        "Study Mins 📚": int(study), 
                        "Chores Done 🧹": int(chores), 
                        "Books Read 📖": int(books), 
                        "Fitness Mins 💪": int(fitness), 
                        "Total League Points 🏆": int(pts)
                    })
            
            if summary:
                res_df = pd.DataFrame(summary).sort_values(by="Total League Points 🏆", ascending=False).reset_index(drop=True)
                st.dataframe(res_df, use_container_width=True)
                st.balloons()
            else:
                st.info("Training roster calculations processing... Complete a match drill or log a chore to update scores!")
