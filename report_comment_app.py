# =========================================
# MULTI-SUBJECT REPORT COMMENT GENERATOR
# Clean Minimal Version
# Supports Year 5, 7 & 8; Subjects: English, Maths, Science
# =========================================

import streamlit as st
import sys
import os

# Try to import required packages
try:
    import docx
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    st.error("'pandas' package not installed")
    st.stop()

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

# Import standard libraries
import random
import tempfile
import time
from datetime import datetime, timedelta
import io
import re

# ========== SETTINGS ==========
TARGET_CHARS = 499
MAX_FILE_SIZE_MB = 5
MAX_ROWS_PER_UPLOAD = 100

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Report Comment Generator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== INITIALIZE SESSION STATE ==========
if 'app_initialized' not in st.session_state:
    st.session_state.clear()
    st.session_state.app_initialized = True
    st.session_state.all_comments = []
    st.session_state.current_data = None

# ========== HELPER FUNCTIONS ==========
def sanitize_input(text, max_length=100):
    """Clean user input"""
    if not text:
        return ""
    sanitized = ''.join(c for c in text if c.isalnum() or c in " .'-")
    return sanitized[:max_length].strip().title()

def get_pronouns(gender):
    gender = gender.lower()
    if gender == "male":
        return "he", "his"
    elif gender == "female":
        return "she", "her"
    return "they", "their"

def lowercase_first(text):
    return text[0].lower() + text[1:] if text else ""

def fix_pronouns_in_text(text, pronoun, possessive):
    """Fix gender pronouns"""
    if not text:
        return text
    
    text = re.sub(r'\bhe\b', pronoun, text, flags=re.IGNORECASE)
    text = re.sub(r'\bHe\b', pronoun.capitalize(), text)
    text = re.sub(r'\bhis\b', possessive, text, flags=re.IGNORECASE)
    text = re.sub(r'\bHis\b', possessive.capitalize(), text)
    text = re.sub(r'\bhim\b', pronoun, text, flags=re.IGNORECASE)
    
    return text

def truncate_comment(comment, target=TARGET_CHARS):
    if len(comment) <= target:
        return comment
    truncated = comment[:target].rstrip(" ,;.")
    if "." in truncated:
        truncated = truncated[:truncated.rfind(".")+1]
    return truncated

def apply_british_spelling(text):
    """Convert American spelling to British spelling"""
    if not text:
        return text
    
    replacements = {
        r'\borganized\b': 'organised',
        r'\brealized\b': 'realised',
        r'\bcolor\b': 'colour',
        r'\blabor\b': 'labour',
        r'\bhonor\b': 'honour',
        r'\bbehavior\b': 'behaviour',
        r'\bfavorite\b': 'favourite',
        r'\bcenter\b': 'centre',
        r'\bmeter\b': 'metre',
        r'\banalyze\b': 'analyse',
        r'\borganize\b': 'organise',
        r'\brealize\b': 'realise',
        r'\bdefense\b': 'defence',
        r'\blicense\b': 'licence',
    }
    
    for american, british in replacements.items():
        text = re.sub(american, british, text, flags=re.IGNORECASE)
    
    return text

def process_csv_securely(uploaded_file):
    """Process CSV file"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp:
        tmp.write(uploaded_file.getvalue())
        temp_path = tmp.name
    
    try:
        df = pd.read_csv(temp_path, nrows=MAX_ROWS_PER_UPLOAD + 1)
        if len(df) > MAX_ROWS_PER_UPLOAD:
            df = df.head(MAX_ROWS_PER_UPLOAD)
        if 'Student Name' in df.columns:
            df['Student Name'] = df['Student Name'].apply(lambda x: sanitize_input(str(x)))
        return df
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

# ========== IMPORT STATEMENTS ==========
try:
    # Year 5 English
    from statements_year5_English import (
        opening_phrases as opening_5_eng,
        attitude_bank as attitude_5_eng,
        reading_bank as reading_5_eng,
        writing_bank as writing_5_eng,
        reading_target_bank as target_5_eng,
        writing_target_bank as target_write_5_eng,
        closer_bank as closer_5_eng
    )
    
    # Year 5 Maths
    from statements_year5_Maths import (
        opening_phrases as opening_5_maths,
        attitude_bank as attitude_5_maths,
        number_bank as number_5_maths,
        problem_solving_bank as problem_5_maths,
        target_bank as target_5_maths,
        closer_bank as closer_5_maths
    )
    
    # Year 5 Science
    from statements_year5_Science import (
        opening_phrases as opening_5_sci,
        attitude_bank as attitude_5_sci,
        science_bank as science_5_sci,
        target_bank as target_5_sci,
        closer_bank as closer_5_sci
    )
    
    # Year 7 English
    from statements_year7_English import (
        opening_phrases as opening_7_eng,
        attitude_bank as attitude_7_eng,
        reading_bank as reading_7_eng,
        writing_bank as writing_7_eng,
        reading_target_bank as target_7_eng,
        writing_target_bank as target_write_7_eng,
        closer_bank as closer_7_eng
    )
    
    # Year 7 Maths
    from statements_year7_Maths import (
        opening_phrases as opening_7_maths,
        attitude_bank as attitude_7_maths,
        number_and_algebra_bank as number_7_maths,
        geometry_and_measurement_bank as geometry_7_maths,
        problem_solving_and_reasoning_bank as problem_7_maths,
        target_bank as target_7_maths,
        closer_bank as closer_7_maths
    )
    
    # Year 7 Science
    from statements_year7_science import (
        opening_phrases as opening_7_sci,
        attitude_bank as attitude_7_sci,
        science_bank as science_7_sci,
        target_bank as target_7_sci,
        closer_bank as closer_7_sci
    )
    
    # Year 8 English
    from statements_year8_English import (
        opening_phrases as opening_8_eng,
        attitude_bank as attitude_8_eng,
        reading_bank as reading_8_eng,
        writing_bank as writing_8_eng,
        reading_target_bank as target_8_eng,
        writing_target_bank as target_write_8_eng,
        closer_bank as closer_8_eng
    )
    
    # Year 8 Maths
    from statements_year8_Maths import (
        opening_phrases as opening_8_maths,
        attitude_bank as attitude_8_maths,
        maths_bank as maths_8_maths,
        target_bank as target_8_maths,
        closer_bank as closer_8_maths
    )
    
    # Year 8 Science
    from statements_year8_science import (
        opening_phrases as opening_8_sci,
        attitude_bank as attitude_8_sci,
        science_bank as science_8_sci,
        target_bank as target_8_sci,
        closer_bank as closer_8_sci
    )
    
except ImportError as e:
    st.error(f"Missing statement files: {e}")
    st.info("Make sure all statement files are in the same directory")
    st.stop()

# ========== COMMENT GENERATOR ==========
def get_statement_banks(subject, year):
    """Get appropriate statement banks"""
    if year == 5 and subject == "English":
        return (opening_5_eng, attitude_5_eng, reading_5_eng, writing_5_eng,
               target_5_eng, target_write_5_eng, closer_5_eng)
    elif year == 5 and subject == "Maths":
        return (opening_5_maths, attitude_5_maths, number_5_maths, None,
               target_5_maths, None, closer_5_maths)
    elif year == 5 and subject == "Science":
        return (opening_5_sci, attitude_5_sci, science_5_sci, None,
               target_5_sci, None, closer_5_sci)
    elif year == 7 and subject == "English":
        return (opening_7_eng, attitude_7_eng, reading_7_eng, writing_7_eng,
               target_7_eng, target_write_7_eng, closer_7_eng)
    elif year == 7 and subject == "Maths":
        return (opening_7_maths, attitude_7_maths, number_7_maths, None,
               target_7_maths, None, closer_7_maths)
    elif year == 7 and subject == "Science":
        return (opening_7_sci, attitude_7_sci, science_7_sci, None,
               target_7_sci, None, closer_7_sci)
    elif year == 8 and subject == "English":
        return (opening_8_eng, attitude_8_eng, reading_8_eng, writing_8_eng,
               target_8_eng, target_write_8_eng, closer_8_eng)
    elif year == 8 and subject == "Maths":
        return (opening_8_maths, attitude_8_maths, maths_8_maths, None,
               target_8_maths, None, closer_8_maths)
    elif year == 8 and subject == "Science":
        return (opening_8_sci, attitude_8_sci, science_8_sci, None,
               target_8_sci, None, closer_8_sci)
    return None

def generate_comment(subject, year, name, gender, att, achieve, target, attitude_target=""):
    """Generate report comment"""
    p, p_poss = get_pronouns(gender)
    name = sanitize_input(name)
    
    banks = get_statement_banks(subject, year)
    if not banks:
        return "Error: Statement banks not found"
    
    opening_bank, attitude_bank, achievement_bank, writing_bank, target_bank, writing_target_bank, closer_bank = banks
    
    # Build comment
    if subject == "English":
        opening = random.choice(opening_bank)
        attitude_text = fix_pronouns_in_text(attitude_bank[att], p, p_poss)
        attitude_sentence = f"{opening} {name} {attitude_text}"
        if not attitude_sentence.endswith('.'):
            attitude_sentence += '.'
        
        reading_text = fix_pronouns_in_text(achievement_bank[achieve], p, p_poss)
        if reading_text[0].islower():
            reading_text = f"{p} {reading_text}"
        reading_sentence = f"In reading, {reading_text}"
        if not reading_sentence.endswith('.'):
            reading_sentence += '.'
        
        writing_text = fix_pronouns_in_text(writing_bank[achieve], p, p_poss)
        if writing_text[0].islower():
            writing_text = f"{p} {writing_text}"
        writing_sentence = f"In writing, {writing_text}"
        if not writing_sentence.endswith('.'):
            writing_sentence += '.'
        
        reading_target_text = fix_pronouns_in_text(target_bank[target], p, p_poss)
        reading_target_sentence = f"For the next term, {p} should {lowercase_first(reading_target_text)}"
        if not reading_target_sentence.endswith('.'):
            reading_target_sentence += '.'
        
        writing_target_text = fix_pronouns_in_text(writing_target_bank[target], p, p_poss)
        writing_target_sentence = f"Additionally, {p} should {lowercase_first(writing_target_text)}"
        if not writing_target_sentence.endswith('.'):
            writing_target_sentence += '.'
        
        closer_sentence = random.choice(closer_bank)
        
    elif subject == "Maths":
        opening = random.choice(opening_bank)
        attitude_text = fix_pronouns_in_text(attitude_bank[att], p, p_poss)
        attitude_sentence = f"{opening} {name} {attitude_text}"
        if not attitude_sentence.endswith('.'):
            attitude_sentence += '.'
        
        achievement_text = fix_pronouns_in_text(achievement_bank[achieve], p, p_poss)
        if achievement_text[0].islower():
            achievement_text = f"{p} {achievement_text}"
        reading_sentence = achievement_text
        if not reading_sentence.endswith('.'):
            reading_sentence += '.'
        
        target_text = fix_pronouns_in_text(target_bank[target], p, p_poss)
        reading_target_sentence = f"For the next term, {p} should {lowercase_first(target_text)}"
        if not reading_target_sentence.endswith('.'):
            reading_target_sentence += '.'
        
        writing_sentence = ""
        writing_target_sentence = ""
        closer_sentence = random.choice(closer_bank)
        
    else:  # Science
        opening = random.choice(opening_bank)
        attitude_text = fix_pronouns_in_text(attitude_bank[att], p, p_poss)
        attitude_sentence = f"{opening} {name} {attitude_text}"
        if not attitude_sentence.endswith('.'):
            attitude_sentence += '.'
        
        science_text = fix_pronouns_in_text(achievement_bank[achieve], p, p_poss)
        if science_text[0].islower():
            science_text = f"{p} {science_text}"
        reading_sentence = science_text
        if not reading_sentence.endswith('.'):
            reading_sentence += '.'
        
        target_text = fix_pronouns_in_text(target_bank[target], p, p_poss)
        reading_target_sentence = f"For the next term, {p} should {lowercase_first(target_text)}"
        if not reading_target_sentence.endswith('.'):
            reading_target_sentence += '.'
        
        writing_sentence = ""
        writing_target_sentence = ""
        closer_sentence = random.choice(closer_bank)
    
    # Optional attitude target
    if attitude_target and attitude_target.strip():
        attitude_target = sanitize_input(attitude_target)
        attitude_target_sentence = f"{lowercase_first(attitude_target)}"
        if not attitude_target_sentence.endswith('.'):
            attitude_target_sentence += '.'
    else:
        attitude_target_sentence = ""
    
    # Assemble comment
    comment_parts = [
        attitude_sentence,
        reading_sentence,
        writing_sentence,
        reading_target_sentence,
        writing_target_sentence,
        closer_sentence,
        attitude_target_sentence
    ]
    
    comment = " ".join([c for c in comment_parts if c])
    comment = comment.strip()
    
    if not comment.endswith('.'):
        comment += '.'
    
    comment = comment.replace('..', '.')
    comment = truncate_comment(comment, TARGET_CHARS)
    
    # Apply British spelling
    comment = apply_british_spelling(comment)
    
    return comment

# ========== APP LAYOUT ==========
# Simple minimal CSS
st.markdown("""
<style>
    /* Remove all decorations */
    [data-testid="stDecoration"] {
        display: none;
    }
    
    /* Clean buttons */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background-color: #FFC107;
        color: black;
        border: none;
    }
    
    /* Clean form */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], 
    .stTextArea textarea {
        border: 1px solid #ddd;
        border-radius: 4px;
    }
    
    /* Simple metrics */
    .stMetric {
        background-color: transparent;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Navigation")
    app_mode = st.radio(
        "",
        ["Single Student", "Batch Upload", "View Comments"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    if st.button("Clear All Data", use_container_width=True, type="secondary"):
        st.session_state.clear()
        st.session_state.app_initialized = True
        st.session_state.all_comments = []
        st.session_state.current_data = None
        st.success("Data cleared")
        st.rerun()

# Main content
st.title("Report Comment Generator")
st.markdown("Generate comments for Years 5, 7, 8 • English, Maths, Science")

# ========== SINGLE STUDENT MODE ==========
if app_mode == "Single Student":
    st.markdown("---")
    st.markdown("### Enter Student Details")
    
    # Simple form
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.selectbox("Subject", ["English", "Maths", "Science"])
        year = st.selectbox("Year", [5, 7, 8])
        name = st.text_input("Student Name", placeholder="First name")
    
    with col2:
        gender = st.selectbox("Gender", ["Male", "Female"])
        att = st.selectbox("Attitude Band", options=[90,85,80,75,70,65,60,55,40], index=3)
        achieve = st.selectbox("Achievement Band", options=[90,85,80,75,70,65,60,55,40], index=3)
    
    target = st.selectbox("Target Band", options=[90,85,80,75,70,65,60,55,40], index=3)
    
    attitude_target = st.text_area(
        "Optional Next Steps",
        placeholder="E.g., continue to participate actively...",
        height=60
    )
    
    # Generate button
    if st.button("Generate Comment", use_container_width=True):
        if not name.strip():
            st.error("Please enter a student name")
        else:
            # Store current data
            st.session_state.current_data = {
                'subject': subject,
                'year': year,
                'name': name,
                'gender': gender,
                'att': att,
                'achieve': achieve,
                'target': target,
                'attitude_target': attitude_target
            }
            
            # Generate comment
            with st.spinner("Generating..."):
                comment = generate_comment(
                    subject=subject,
                    year=year,
                    name=name,
                    gender=gender,
                    att=att,
                    achieve=achieve,
                    target=target,
                    attitude_target=attitude_target
                )
                
                st.session_state.current_comment = comment
    
    # Display comment if generated
    if hasattr(st.session_state, 'current_comment') and st.session_state.current_comment:
        st.markdown("---")
        st.markdown("### Generated Comment")
        
        # Display comment
        st.text_area("", st.session_state.current_comment, height=150, label_visibility="collapsed")
        
        # Action buttons in a row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Copy", use_container_width=True):
                st.code(st.session_state.current_comment, language=None)
                st.success("Ready to copy!")
        
        with col2:
            if st.button("Generate Variant", use_container_width=True, type="secondary"):
                # Generate new variant with different random selection
                data = st.session_state.current_data
                new_comment = generate_comment(
                    subject=data['subject'],
                    year=data['year'],
                    name=data['name'],
                    gender=data['gender'],
                    att=data['att'],
                    achieve=data['achieve'],
                    target=data['target'],
                    attitude_target=data['attitude_target']
                )
                st.session_state.current_comment = new_comment
                st.rerun()
        
        with col3:
            if st.button("Save & New", use_container_width=True):
                # Save current comment
                if st.session_state.current_data:
                    student_entry = {
                        'name': st.session_state.current_data['name'],
                        'subject': st.session_state.current_data['subject'],
                        'year': st.session_state.current_data['year'],
                        'comment': st.session_state.current_comment,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    st.session_state.all_comments.append(student_entry)
                
                # Clear for new student
                st.session_state.current_comment = None
                st.session_state.current_data = None
                st.rerun()
        
        # Character count
        char_count = len(st.session_state.current_comment)
        st.caption(f"Characters: {char_count}/{TARGET_CHARS} • Words: {len(st.session_state.current_comment.split())}")

# ========== BATCH UPLOAD MODE ==========
elif app_mode == "Batch Upload":
    st.markdown("---")
    st.markdown("### Upload CSV File")
    
    st.info("""
    **CSV Format:**  
    Student Name, Gender, Subject, Year, Attitude, Achievement, Target  
    Example: John, Male, English, 7, 75, 80, 85
    """)
    
    # Example CSV
    example_csv = """Student Name,Gender,Subject,Year,Attitude,Achievement,Target
Sarah,Female,English,5,75,80,85
John,Male,Maths,7,80,75,80
Emma,Female,Science,8,85,90,85"""
    
    st.download_button(
        "Download Example CSV",
        example_csv,
        "example_students.csv",
        "text/csv",
        use_container_width=True
    )
    
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
    
    if uploaded_file:
        if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            st.error(f"File too large (max {MAX_FILE_SIZE_MB}MB)")
        else:
            with st.spinner("Processing file..."):
                df = process_csv_securely(uploaded_file)
            
            if df is not None:
                st.success(f"Loaded {len(df)} students")
                
                if st.button("Generate All Comments", use_container_width=True):
                    progress_bar = st.progress(0)
                    
                    for idx, row in df.iterrows():
                        progress = (idx + 1) / len(df)
                        progress_bar.progress(progress)
                        
                        try:
                            comment = generate_comment(
                                subject=str(row.get('Subject', 'English')),
                                year=int(row.get('Year', 7)),
                                name=str(row.get('Student Name', '')),
                                gender=str(row.get('Gender', '')),
                                att=int(row.get('Attitude', 75)),
                                achieve=int(row.get('Achievement', 75)),
                                target=int(row.get('Target', 75))
                            )
                            
                            student_entry = {
                                'name': sanitize_input(str(row.get('Student Name', ''))),
                                'subject': str(row.get('Subject', 'English')),
                                'year': int(row.get('Year', 7)),
                                'comment': comment,
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                            st.session_state.all_comments.append(student_entry)
                            
                        except Exception as e:
                            st.error(f"Error with row {idx + 1}: {e}")
                    
                    progress_bar.empty()
                    st.success(f"Generated {len(df)} comments")

# ========== VIEW COMMENTS MODE ==========
elif app_mode == "View Comments":
    st.markdown("---")
    st.markdown("### Saved Comments")
    
    if not st.session_state.all_comments:
        st.info("No comments saved yet. Generate some comments first.")
    else:
        st.markdown(f"**Total: {len(st.session_state.all_comments)} comments**")
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            if DOCX_AVAILABLE and st.button("Export to Word", use_container_width=True):
                doc = Document()
                doc.add_heading('Report Comments', 0)
                doc.add_paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
                doc.add_paragraph(f'Total: {len(st.session_state.all_comments)}')
                doc.add_paragraph('')
                
                for entry in st.session_state.all_comments:
                    doc.add_heading(f"{entry['name']} - {entry['subject']} Year {entry['year']}", level=2)
                    doc.add_paragraph(entry['comment'])
                    doc.add_paragraph('')
                
                bio = io.BytesIO()
                doc.save(bio)
                
                st.download_button(
                    "Download .docx",
                    bio.getvalue(),
                    f"comments_{datetime.now().strftime('%Y%m%d')}.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            elif not DOCX_AVAILABLE:
                st.button("Word Export (Disabled)", disabled=True, use_container_width=True)
                st.caption("Install 'docx' package")
        
        with col2:
            if st.button("Export to CSV", use_container_width=True):
                csv_data = []
                for entry in st.session_state.all_comments:
                    csv_data.append({
                        'Student': entry['name'],
                        'Subject': entry['subject'],
                        'Year': entry['year'],
                        'Comment': entry['comment']
                    })
                
                df_export = pd.DataFrame(csv_data)
                csv_bytes = df_export.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    "Download .csv",
                    csv_bytes,
                    f"comments_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
        
        # Display comments
        st.markdown("---")
        for idx, entry in enumerate(st.session_state.all_comments, 1):
            with st.expander(f"{idx}. {entry['name']} - {entry['subject']} Year {entry['year']}"):
                st.write(entry['comment'])
                st.caption(f"Generated: {entry['timestamp']}")
        
        # Clear button
        if st.button("Clear All Comments", type="secondary", use_container_width=True):
            st.session_state.all_comments = []
            st.rerun()

# ========== FOOTER ==========
st.markdown("---")
st.caption("Report Generator • Secure Local Processing • No Data Storage")
