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
            raw_data =
