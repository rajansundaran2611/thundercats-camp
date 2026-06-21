import streamlit as st
import pandas as pd
import urllib.request
import json
import time
import streamlit.components.v1 as components

# App Setup & Theme Branding
st.set_page_config(page_title="Thornton Thundercats FC", page_icon="⚽", layout="wide")

# 🔌 PASTE YOUR GOOGLE WEB APP URL HERE INSIDE THE QUOTES
# (If left empty or as-is, the app runs in temporary local Demo Mode)
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
            st.session_state.login_time = time.time() # Start the session timer
            send_to_db(name, "Registration", 0, "Signed with the club roster")
            st.rerun()
else:
   # --- DIGITAL CLOCK TIMER SYSTEM ---
    if 'login_time' not in st.session_state:
        st.session_state.login_time = time.time()
    
    elapsed_seconds = int(time.time() - st.session_state.login_time)
    
    # Notice the double braces {{ }} which stops Python from crashing!
    timer_html = f"""
    <script>
    // Access the main Streamlit window
    var parentDoc = window.parent.document;
    var existingTimer = parentDoc.getElementById("fbisd-timer");
    
    // Only create the clock if it doesn't already exist
    if (!existingTimer) {{
        var timerDiv = parentDoc.createElement("div");
        timerDiv.id = "fbisd-timer";
        timerDiv.style.position = "fixed";
        timerDiv.style.top = "60px"; // Pushed down slightly below the Streamlit header
        timerDiv.style.right = "20px";
        timerDiv.style.backgroundColor = "#0f4d92"; // FBISD Blue
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
        
        let totalSeconds = {elapsed_seconds}; // This is the only single-brace variable!
        
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
    
    # Execute the code silently in the background
    components.html(timer_html, width=0, height=0)
    # --- END DIGITAL CLOCK TIMER ---
    
    st.sidebar.markdown(f"### 🏃‍♂️ Squad Member: **{st.session_state.user}**")
    if st.sidebar.button("Leave Training"):
        st.session_state.user = None
        if 'login_time' in st.session_state:
            del st.session_state.login_time
        st.rerun()

    menu = st.sidebar.radio("Tactics Board", ["📋 Daily Drills", "📝 The Hustle Log", "🏆 League Table"])

    # ---------------------------------------------------------
    # MODULE 1: DYNAMIC DRILLS (15-Min Talk + 30-Min Scrimmage)
    # ---------------------------------------------------------
    if menu == "📋 Daily Drills":
        st.header("Today's Tactical Training (45 Minutes)")
        subj = st.selectbox("Select your training session:", ["Math", "Reading", "Science"])
        
        if raw_q_df.empty:
            st.info("⚽ Running in Local Academy Mode. Pulling varsity drills below!")
            if subj == "Math":
                active_q = {
                    "coach": "Striker Sam",
                    "concept_text": "Proportions state that two fractions or ratios are completely equal to each other! Set them up side-by-side to solve for hidden numbers on the pitch.",
                    "question": "If the Thundercats offense scores 3 goals every 20 minutes of possession, how many goals will they score in a full 60-minute game?",
                    "choice_a": "6 goals", "choice_b": "9 goals", "choice_c": "12 goals", "choice_d": "15 goals",
                    "correct_answer": "9 goals",
                    "explanation": "Set up your fraction: 3/20 = X/60. Since a 60-minute game is exactly 3 times longer than 20 minutes, we multiply our goals by 3 as well! 3 x 3 = 9 goals!"
                }
            elif subj == "Reading":
                active_q = {
                    "coach": "Goalkeeper Grace",
                    "concept_text": "Context clues are hidden hints written right inside a sentence. They let you unlock the mystery meaning of difficult vocabulary words without ever needing a dictionary!",
                    "question": "Read this short tape: 'After conceding a heartbreaking goal in the 90th minute to lose the championship, Lucas was completely downcast, collapsing onto the grass with his head buried in his hands as tears streaked through the dirt on his face.' What does downcast mean?",
                    "choice_a": "Elated and Excited", "choice_b": "Sad and Depressed", "choice_c": "Aggressive and Angry", "choice_d": "Exhausted",
                    "correct_answer": "Sad and Depressed",
                    "explanation": "Look at Lucas's clear body language clues! He has his 'head buried in his hands' and 'tears streaking down his face.' Players don't cry or hang their heads when they are excited or aggressive—they do it when they feel downcast, which means sad or depressed!"
                }
            else:
                active_q = {
                    "coach": "Defender Dani",
                    "concept_text": "Newton's First Law of Motion (Inertia) states that an object in motion stays in motion at a constant speed, and an object at rest stays at rest, unless acted upon by an outside force!",
                    "question": "When you pass a soccer ball across a grass field, it eventually slows down and stops. What is the name of the outside force rubbing against the ball that stops it?",
                    "choice_a": "Gravity", "choice_b": "Friction", "choice_c": "Inertia", "choice_d": "Acceleration",
                    "correct_answer": "Friction",
                    "explanation": "As the soccer ball rolls, the blades of grass rub against it. This surface resistance is called friction, and it acts as the outside force that steals the ball's kinetic energy and slows it to a stop!"
                }
        else:
            q_df = raw_q_df.copy()
            q_df.columns = [str(c).strip().lower() for c in q_df.columns]
            
            s_col = "subject" if "subject" in q_df.columns else q_df.columns[0]
            c_col = "coach" if "coach" in q_df.columns else q_df.columns[1]
            txt_col = "concept_text" if "concept_text" in q_df.columns else q_df.columns[2]
            q_col = "question" if "question" in q_df.columns else q_df.columns[3]
            ca_col = "choice_a" if "choice_a" in q_df.columns else q_df.columns[4]
            cb_col = "choice_b" if "choice_b" in q_df.columns else q_df.columns[5]
            cc_col = "choice_c" if "choice_c" in q_df.columns else q_df.columns[6]
            cd_col = "choice_d" if "choice_d" in q_df.columns else q_df.columns[7]
            ans_col = "correct_answer" if "correct_answer" in q_df.columns else q_df.columns[8]
            exp_col = "explanation" if "explanation" in q_df.columns else q_df.columns[9]

            q_df[s_col] = q_df[s_col].astype(str).str.strip().str.capitalize()
            pool = q_df[q_df[s_col] == subj.capitalize()]
            
            if pool.empty:
                st.warning(f"Coaching staff is uploading questions to the '{subj}' sheet row pool now. Pulling standard drill instead!")
                pool = pd.DataFrame([{"coach": "Striker Sam", "concept_text": "Basics review", "question": "What is 10 x 10?", "choice_a": "50", "choice_b": "100", "choice_c": "150", "choice_d": "200", "correct_answer": "100", "explanation": "10 times 10 is 100!"}])
                c_col, txt_col, q_col, ca_col, cb_col, cc_col, cd_col, ans_col, exp_col = "coach", "concept_text", "question", "choice_a", "choice_b", "choice_c", "choice_d", "correct_answer", "explanation"

            if f"drill_{subj}" not in st.session_state:
                st.session_state[f"drill_{subj}"] = pool.sample(n=1).iloc[0].to_dict()
            
            raw_active = st.session_state[f"drill_{subj}"]
            active_q = {
                "coach": raw_active[c_col], "concept_text": raw_active[txt_col], "question": raw_active[q_col],
                "choice_a": raw_active[ca_col], "choice_b": raw_active[cb_col], "choice_c": raw_active[cc_col], "choice_d": raw_active[cd_col],
                "correct_answer": raw_active[ans_col], "explanation": raw_active[exp_col]
            }

        st.subheader(f"🧠 Chalk Talk with {active_q['coach']} (First 15 Minutes)")
        st.info(active_q['concept_text'])
        st.markdown("---")
        
        st.subheader("🎯 Match Time: The 30-Minute Post-Game Quiz")
        st.write(active_q['question'])
        
        opts = [str(active_q['choice_a']), str(active_q['choice_b']), str(active_q['choice_c']), str(active_q['choice_d'])]
        ans = st.radio("Pick your shot placement:", ["Select..."] + opts)
        
        if ans != "Select...":
            if ans == str(active_q['correct_answer']):
                st.success("⚽ GOALLLL!!! Top-bins finish! You read the play perfectly.")
                if st.button("Log 45 Minutes on Your Academy Record"):
                    send_to_db(st.session_state.user, subj, 45, f"Passed {active_q['coach']} drill session")
                    if f"drill_{subj}" in st.session_state:
                        del st.session_state[f"drill_{subj}"]
                    st.success("Training time saved to team database! Check the league standings.")
                    st.rerun()
            else:
                st.error("❌ SAVED BY THE KEEPER! Hit the woodwork.")
                st.warning(f"📋 **Coach's Video Review Breakdown:** {active_q['explanation']}")

    # ---------------------------------------------------------
    # MODULE 2: HUSTLE LOG (Chores, Reading, Conditioning)
    # ---------------------------------------------------------
    elif menu == "📝 The Hustle Log":
        st.header("📋 The Off-Field Hustle Log")
        st.write("True professionals put in work even when the stadium cameras are turned off. Log your stats below!")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("🧹 Cleaning the Pitch (Chores)")
            chore_txt = st.text_input("What chore did you complete? (e.g., Loaded the dishwasher, vacuumed):")
            if st.button("Log Chore Points") and chore_txt:
                send_to_db(st.session_state.user, "Chore", 1, chore_txt)
                st.success("Top team player! Chore milestone added to the database!")
                
        with c2:
            st.subheader("📚 Scouting Reports (Reading)")
            book_txt = st.text_input("What book or chapter did you devour? (Builds reading muscle!):")
            if st.button("Log Reading Progress") and book_txt:
                send_to_db(st.session_state.user, "Book", 1, book_txt)
                st.success("Expanding your playbook! Book mileage tracked successfully.")
                
        with c3:
            st.subheader("💪 Fitness & Conditioning")
            workout_mins = st.number_input("Minutes spent training/practicing today:", min_value=0, max_value=300, step=5)
            if st.button("Log Training Minutes") and workout_mins > 0:
                send_to_db(st.session_state.user, "Workout", workout_mins, "Athletic fitness conditioning block")
                st.success("Engine conditioning blocks posted!")

    # ---------------------------------------------------------
    # MODULE 3: LEADERBOARD SYSTEM (100% Position-Based Fix)
    # ---------------------------------------------------------
    elif menu == "🏆 League Table":
        st.header("🏆 The Academy League Table")
        log_df = load_from_db("get_logs")
        
        if log_df.empty or len(log_df.columns) < 4:
            st.info("No stats recorded on the pitch yet. Complete a training drill to break the ice!")
        else:
            # 🎯 PURE GEOMETRIC MAP: We bypass string names entirely and use number index positions!
            # Column 0 = Timestamp | Column 1 = Player | Column 2 = Activity | Column 3 = Value
            p_idx = 1  
            a_idx = 2  
            v_idx = 3  
            
            summary = []
            
            # Extract unique values from Column 1 (Player Name)
            unique_players = log_df.iloc[:, p_idx].dropna().astype(str).str.strip().unique()
            
            for player in unique_players:
                # 🛑 CRITICAL FILTER: Instantly filter out headers, metadata, or formatting artifacts
                if player in ["None", "nan", "", "player", "Player", "timestamp", "Timestamp"]: 
                    continue
                
                # Check if the text value in Column 1 looks like a timestamp/date instead of a name
                if "-" in player and ":" in player or len(player) > 20 and ("202" in player):
                    continue
                
                # Isolate rows belonging strictly to this single player
                pdf = log_df[log_df.iloc[:, p_idx].astype(str).str.strip() == player]
                
                # Setup specific category sums
                study = 0
                chores = 0
                books = 0
                fitness = 0
                
                # Process row calculations individually
                for _, row in pdf.iterrows():
                    act = str(row.iloc[a_idx]).strip().capitalize()
                    
                    # ❌ EXCLUDE REGISTRATION: If activity is Registration, ignore it!
                    if act == "Registration":
                        continue
                        
                    # Safely extract score metric value
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
                
                # Gamified scoring point formula execution
                pts = study + fitness + (chores * 10) + (books * 20)
                
                # Only display players who have actual minutes or points earned
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
