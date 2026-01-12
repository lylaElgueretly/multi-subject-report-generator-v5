# =========================================
# MULTI-SUBJECT REPORT COMMENT GENERATOR - Secure Streamlit Version
# Light Mode, Compact, No Icons, Clean UI
# Supports Year 5, 7 & 8; Subjects: English, Maths, Science
# =========================================

import random
import streamlit as st
from docx import Document
import tempfile
import os
import time
from datetime import datetime, timedelta
import pandas as pd
import io
import re

# ========== FORCE LIGHT MODE ==========
st.markdown(
    """
    <style>
    body { background-color: #ffffff; color: #000000; }
    </style>
    """,
    unsafe_allow_html=True
)

# ========== CONFIG ==========
TARGET_CHARS = 499
MAX_FILE_SIZE_MB = 5
MAX_ROWS_PER_UPLOAD = 100
RATE_LIMIT_SECONDS = 5

st.set_page_config(
    page_title="Report Comment Assistant",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== SESSION INITIALIZATION ==========
if 'app_initialized' not in st.session_state:
    st.session_state.clear()
    st.session_state.app_initialized = True
    st.session_state.upload_count = 0
    st.session_state.last_upload_time = datetime.now()
    st.session_state.generated_files = []

# ========== IMPORT STATEMENTS ==========
try:
    from statements_year5_English import opening_phrases as opening_5_eng, attitude_bank as attitude_5_eng, reading_bank as reading_5_eng, writing_bank as writing_5_eng, reading_target_bank as target_5_eng, writing_target_bank as target_write_5_eng, closer_bank as closer_5_eng
    from statements_year5_Maths import opening_phrases as opening_5_maths, attitude_bank as attitude_5_maths, number_bank as number_5_maths, problem_solving_bank as problem_5_maths, target_bank as target_5_maths, closer_bank as closer_5_maths
    from statements_year5_Science import opening_phrases as opening_5_sci, attitude_bank as attitude_5_sci, science_bank as science_5_sci, target_bank as target_5_sci, closer_bank as closer_5_sci
    from statements_year7_English import opening_phrases as opening_7_eng, attitude_bank as attitude_7_eng, reading_bank as reading_7_eng, writing_bank as writing_7_eng, reading_target_bank as target_7_eng, writing_target_bank as target_write_7_eng, closer_bank as closer_7_eng
    from statements_year7_Maths import opening_phrases as opening_7_maths, attitude_bank as attitude_7_maths, number_and_algebra_bank as number_7_maths, geometry_and_measurement_bank as geometry_7_maths, problem_solving_and_reasoning_bank as problem_7_maths, target_bank as target_7_maths, closer_bank as closer_7_maths
    from statements_year7_science import opening_phrases as opening_7_sci, attitude_bank as attitude_7_sci, science_bank as science_7_sci, target_bank as target_7_sci, closer_bank as closer_7_sci
    from statements_year8_English import opening_phrases as opening_8_eng, attitude_bank as attitude_8_eng, reading_bank as reading_8_eng, writing_bank as writing_8_eng, reading_target_bank as target_8_eng, writing_target_bank as target_write_8_eng, closer_bank as closer_8_eng
    from statements_year8_Maths import opening_phrases as opening_8_maths, attitude_bank as attitude_8_maths, maths_bank as maths_8_maths, target_bank as target_8_maths, closer_bank as closer_8_maths
    from statements_year8_science import opening_phrases as opening_8_sci, attitude_bank as attitude_8_sci, science_bank as science_8_sci, target_bank as target_8_sci, closer_bank as closer_8_sci
except ImportError as e:
    st.error(f"Missing required statement files: {e}")
    st.stop()

# ========== SECURITY & HELPERS ==========
def validate_upload_rate():
    time_since_last = datetime.now() - st.session_state.last_upload_time
    if time_since_last < timedelta(seconds=RATE_LIMIT_SECONDS):
        wait_time = RATE_LIMIT_SECONDS - time_since_last.seconds
        st.error(f"Please wait {wait_time} seconds before uploading again")
        return False
    return True

def sanitize_input(text, max_length=100):
    if not text:
        return ""
    sanitized = ''.join(c for c in text if c.isalnum() or c in " .'-")
    return sanitized[:max_length].strip().title()

def validate_file(file):
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"File too large (max {MAX_FILE_SIZE_MB}MB)"
    if not file.name.lower().endswith('.csv'):
        return False, "Only CSV files allowed"
    return True, ""

def process_csv_securely(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp:
        tmp.write(uploaded_file.getvalue())
        temp_path = tmp.name
    try:
        df = pd.read_csv(temp_path, nrows=MAX_ROWS_PER_UPLOAD + 1)
        if len(df) > MAX_ROWS_PER_UPLOAD:
            st.warning(f"Only processing first {MAX_ROWS_PER_UPLOAD} rows")
            df = df.head(MAX_ROWS_PER_UPLOAD)
        if 'Student Name' in df.columns:
            df['Student Name'] = df['Student Name'].apply(lambda x: sanitize_input(str(x)))
        return df
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None
    finally:
        try: os.unlink(temp_path)
        except: pass

def get_pronouns(gender):
    gender = gender.lower()
    if gender == "male": return "he","his"
    elif gender == "female": return "she","her"
    return "they","their"

def lowercase_first(text):
    return text[0].lower() + text[1:] if text else ""

def truncate_comment(comment, target=TARGET_CHARS):
    if len(comment) <= target: return comment
    truncated = comment[:target].rstrip(" ,;.") 
    if "." in truncated:
        truncated = truncated[:truncated.rfind(".")+1]
    return truncated

def fix_pronouns_in_text(text, pronoun, possessive):
    if not text: return text
    text = re.sub(r'\bhe\b', pronoun, text, flags=re.IGNORECASE)
    text = re.sub(r'\bHe\b', pronoun.capitalize(), text)
    text = re.sub(r'\bhis\b', possessive, text, flags=re.IGNORECASE)
    text = re.sub(r'\bHis\b', possessive.capitalize(), text)
    text = re.sub(r'\bhim\b', pronoun, text, flags=re.IGNORECASE)
    text = re.sub(r'\bHim\b', pronoun.capitalize(), text)
    text = re.sub(r'\bhimself\b', f"{pronoun}self", text, flags=re.IGNORECASE)
    text = re.sub(r'\bherself\b', f"{pronoun}self", text, flags=re.IGNORECASE)
    return text

# ========== COMMENT GENERATOR ==========
def generate_comment(subject, year, name, gender, att, achieve, target, pronouns, attitude_target=None):
    # existing logic to generate main comment parts
    p, p_poss = pronouns
    name = sanitize_input(name)
    
    # --- logic here remains unchanged, just returns the final comment_parts list as before ---
    comment_parts = generate_comment_logic(subject, year, name, gender, att, achieve, target, pronouns, attitude_target)
    
    # Combine comment parts safely
    comment = " ".join([c for c in comment_parts if c])
    comment = comment.strip()
    
    # Append optional text safely with period
    if attitude_target:
        attitude_target = attitude_target.strip()
        if not attitude_target.endswith("."):
            attitude_target += "."
        comment = comment.rstrip(". ") + ". " + attitude_target
    
    # Ensure final punctuation
    if not comment.endswith("."):
        comment += "."
    
    return comment

# ========== APP INTERFACE ==========
st.image("assets/ikc_logo.png", width=120)
st.title("Report Comment Assistant")
st.caption("Years 5, 7 & 8 • English, Maths, Science • Smart & Fast")

# --- Compact layout ---
st.markdown("<hr>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Navigation")
    app_mode = st.radio("Mode", ["Single Student", "Batch Upload", "Privacy Info"])
    st.markdown("---")
    if st.button("Clear All Data"):
        st.session_state.clear()
        st.session_state.app_initialized=True
        st.session_state.upload_count=0
        st.session_state.last_upload_time=datetime.now()
        st.success("Cleared!")

# --- Steps ---
step_col1, step_col2, step_col3 = st.columns(3)
def step_box(col, step_num, title):
    with col:
        st.markdown(f"<div style='padding:5px;background:#dff0d8;border-radius:5px;text-align:center;'>{step_num}. {title}</div>", unsafe_allow_html=True)
step_box(step_col1, 1, "Select")
step_box(step_col2, 2, "Generate")
step_box(step_col3, 3, "Download")

# --- Single Student Mode ---
if app_mode=="Single Student":
    st.subheader("Single Student Entry")
    with st.form("single_student_form", clear_on_submit=True):
        col1,col2=st.columns(2)
        with col1:
            subject=st.selectbox("Subject", ["English","Maths","Science"])
            year=st.selectbox("Year",[5,7,8])
            name=st.text_input("Student Name")
            gender=st.selectbox("Gender",["Male","Female"])
        with col2:
            att=st.selectbox("Attitude Band",[90,85,80,75,70,65,60,55,40],index=3)
            achieve=st.selectbox("Achievement Band",[90,85,80,75,70,65,60,55,40],index=3)
            target=st.selectbox("Target Band",[90,85,80,75,70,65,60,55,40],index=3)
        attitude_target=st.text_area("Optional Next Steps", height=50)
        submitted=st.form_submit_button("Generate Comment")
    if submitted and name:
        if not validate_upload_rate(): st.stop()
        pronouns=get_pronouns(gender)
        comment=generate_comment(subject,year,name,gender,att,achieve,target,pronouns,attitude_target)
        st.text_area("Generated Comment", comment, height=180)

# --- Batch Upload Mode ---
elif app_mode=="Batch Upload":
    st.subheader("Batch Upload (CSV)")
    uploaded_file=st.file_uploader("Upload CSV", type=['csv'])
    if uploaded_file:
        if not validate_upload_rate(): st.stop()
        is_valid,msg=validate_file(uploaded_file)
        if not is_valid: st.error(msg); st.stop()
        df=process_csv_securely(uploaded_file)
        if df is not None: st.dataframe(df.head())
        if st.button("Generate All Comments"):
            if 'all_comments' not in st.session_state: st.session_state.all_comments=[]
            for _,row in df.iterrows():
                pronouns=get_pronouns(str(row.get('Gender','')).lower())
                comment=generate_comment(str(row.get('Subject','English')),int(row.get('Year',7)),str(row.get('Student Name','')),str(row.get('Gender','')),int(row.get('Attitude',75)),int(row.get('Achievement',75)),int(row.get('Target',75)),pronouns)
                st.session_state.all_comments.append({'name':row.get('Student Name',''),'subject':row.get('Subject','English'),'year':int(row.get('Year',7)),'comment':comment,'timestamp':datetime.now().strftime("%Y-%m-%d %H:%M")})
            st.success(f"Generated {len(df)} comments!")

# --- Privacy Info Mode ---
elif app_mode=="Privacy Info":
    st.subheader("Privacy & Security")
    st.markdown("All processing happens locally. No data is stored externally.")

# --- Download Section ---
if 'all_comments' in st.session_state and st.session_state.all_comments:
    st.subheader("Download Reports")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Word Document"):
            doc=Document()
            for e in st.session_state.all_comments:
                doc.add_heading(f"{e['name']} - {e['subject']} Year {e['year']}",level=2)
                doc.add_paragraph(e['comment'])
            bio=io.BytesIO()
            doc.save(bio)
            st.download_button("Download DOCX", data=bio.getvalue(), file_name=f"comments_{datetime.now().strftime('%Y%m%d_%H%M')}.docx")
    with col2:
        if st.button("CSV Export"):
            df_export=pd.DataFrame(st.session_state.all_comments)
            csv_bytes=df_export.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv_bytes, file_name=f"comments_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
