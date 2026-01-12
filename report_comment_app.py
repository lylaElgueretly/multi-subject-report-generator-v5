# =========================================
# MULTI-SUBJECT REPORT COMMENT GENERATOR - Secure Streamlit Version
# Supports Year 5, 7 & 8; Subjects: English, Maths, Science
# =========================================

import random
import streamlit as st
import tempfile
import os
import time
from datetime import datetime, timedelta
import pandas as pd
import io
import re

# ========== DOCX IMPORT WITH FALLBACK ==========
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    Document = None

# ========== SECURITY & PRIVACY SETTINGS ==========
TARGET_CHARS = 499
MAX_FILE_SIZE_MB = 5
MAX_ROWS_PER_UPLOAD = 100
RATE_LIMIT_SECONDS = 10

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="🔒 Secure Report Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== SECURITY INITIALIZATION ==========
if 'app_initialized' not in st.session_state:
    st.session_state.clear()
    st.session_state.app_initialized = True
    st.session_state.upload_count = 0
    st.session_state.last_upload_time = datetime.now()
    st.session_state.generated_files = []

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

    # Try to import Year 5 English variants (optional)
    try:
        from statements_year5_English_variant1 import (
            opening_phrases as opening_5_eng_v1,
            attitude_bank as attitude_5_eng_v1,
            reading_bank as reading_5_eng_v1,
            writing_bank as writing_5_eng_v1,
            reading_target_bank as target_5_eng_v1,
            writing_target_bank as target_write_5_eng_v1,
            closer_bank as closer_5_eng_v1
        )
    except ImportError:
        opening_5_eng_v1 = None
        attitude_5_eng_v1 = None
        reading_5_eng_v1 = None
        writing_5_eng_v1 = None
        target_5_eng_v1 = None
        target_write_5_eng_v1 = None
        closer_5_eng_v1 = None

    try:
        from statements_year5_English_variant2 import (
            opening_phrases as opening_5_eng_v2,
            attitude_bank as attitude_5_eng_v2,
            reading_bank as reading_5_eng_v2,
            writing_bank as writing_5_eng_v2,
            reading_target_bank as target_5_eng_v2,
            writing_target_bank as target_write_5_eng_v2,
            closer_bank as closer_5_eng_v2
        )
    except ImportError:
        opening_5_eng_v2 = None
        attitude_5_eng_v2 = None
        reading_5_eng_v2 = None
        writing_5_eng_v2 = None
        target_5_eng_v2 = None
        target_write_5_eng_v2 = None
        closer_5_eng_v2 = None

    # Year 5 Maths
    from statements_year5_Maths import (
        opening_phrases as opening_5_maths,
        attitude_bank as attitude_5_maths,
        number_bank as number_5_maths,
        problem_solving_bank as problem_5_maths,
        target_bank as target_5_maths,
        closer_bank as closer_5_maths
    )

    # Try to import Year 5 Maths variants (optional)
    try:
        from statements_year5_Maths_variant1 import (
            opening_phrases as opening_5_maths_v1,
            attitude_bank as attitude_5_maths_v1,
            number_bank as number_5_maths_v1,
            problem_solving_bank as problem_5_maths_v1,
            target_bank as target_5_maths_v1,
            closer_bank as closer_5_maths_v1
        )
    except ImportError:
        opening_5_maths_v1 = None
        attitude_5_maths_v1 = None
        number_5_maths_v1 = None
        problem_5_maths_v1 = None
        target_5_maths_v1 = None
        closer_5_maths_v1 = None

    try:
        from statements_year5_Maths_variant2 import (
            opening_phrases as opening_5_maths_v2,
            attitude_bank as attitude_5_maths_v2,
            number_bank as number_5_maths_v2,
            problem_solving_bank as problem_5_maths_v2,
            target_bank as target_5_maths_v2,
            closer_bank as closer_5_maths_v2
        )
    except ImportError:
        opening_5_maths_v2 = None
        attitude_5_maths_v2 = None
        number_5_maths_v2 = None
        problem_5_maths_v2 = None
        target_5_maths_v2 = None
        closer_5_maths_v2 = None

    # Year 5 Science
    from statements_year5_Science import (
        opening_phrases as opening_5_sci,
        attitude_bank as attitude_5_sci,
        science_bank as science_5_sci,
        target_bank as target_5_sci,
        closer_bank as closer_5_sci
    )

    # Try to import Year 5 Science variants (optional)
    try:
        from statements_year5_Science_variant1 import (
            opening_phrases as opening_5_sci_v1,
            attitude_bank as attitude_5_sci_v1,
            science_bank as science_5_sci_v1,
            target_bank as target_5_sci_v1,
            closer_bank as closer_5_sci_v1
        )
    except ImportError:
        opening_5_sci_v1 = None
        attitude_5_sci_v1 = None
        science_5_sci_v1 = None
        target_5_sci_v1 = None
        closer_5_sci_v1 = None

    try:
        from statements_year5_Science_variant2 import (
            opening_phrases as opening_5_sci_v2,
            attitude_bank as attitude_5_sci_v2,
            science_bank as science_5_sci_v2,
            target_bank as target_5_sci_v2,
            closer_bank as closer_5_sci_v2
        )
    except ImportError:
        opening_5_sci_v2 = None
        attitude_5_sci_v2 = None
        science_5_sci_v2 = None
        target_5_sci_v2 = None
        closer_5_sci_v2 = None

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

    # Try to import Year 7 English variants (optional)
    try:
        from statements_year7_English_variant1 import (
            opening_phrases as opening_7_eng_v1,
            attitude_bank as attitude_7_eng_v1,
            reading_bank as reading_7_eng_v1,
            writing_bank as writing_7_eng_v1,
            reading_target_bank as target_7_eng_v1,
            writing_target_bank as target_write_7_eng_v1,
            closer_bank as closer_7_eng_v1
        )
    except ImportError:
        opening_7_eng_v1 = None
        attitude_7_eng_v1 = None
        reading_7_eng_v1 = None
        writing_7_eng_v1 = None
        target_7_eng_v1 = None
        target_write_7_eng_v1 = None
        closer_7_eng_v1 = None

    try:
        from statements_year7_English_variant2 import (
            opening_phrases as opening_7_eng_v2,
            attitude_bank as attitude_7_eng_v2,
            reading_bank as reading_7_eng_v2,
            writing_bank as writing_7_eng_v2,
            reading_target_bank as target_7_eng_v2,
            writing_target_bank as target_write_7_eng_v2,
            closer_bank as closer_7_eng_v2
        )
    except ImportError:
        opening_7_eng_v2 = None
        attitude_7_eng_v2 = None
        reading_7_eng_v2 = None
        writing_7_eng_v2 = None
        target_7_eng_v2 = None
        target_write_7_eng_v2 = None
        closer_7_eng_v2 = None

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

    # Try to import Year 7 Science variants (optional)
    try:
        from statements_year7_science_variant1 import (
            opening_phrases as opening_7_sci_v1,
            attitude_bank as attitude_7_sci_v1,
            science_bank as science_7_sci_v1,
            target_bank as target_7_sci_v1,
            closer_bank as closer_7_sci_v1
        )
    except ImportError:
        opening_7_sci_v1 = None
        attitude_7_sci_v1 = None
        science_7_sci_v1 = None
        target_7_sci_v1 = None
        closer_7_sci_v1 = None

    try:
        from statements_year7_science_variant2 import (
            opening_phrases as opening_7_sci_v2,
            attitude_bank as attitude_7_sci_v2,
            science_bank as science_7_sci_v2,
            target_bank as target_7_sci_v2,
            closer_bank as closer_7_sci_v2
        )
    except ImportError:
        opening_7_sci_v2 = None
        attitude_7_sci_v2 = None
        science_7_sci_v2 = None
        target_7_sci_v2 = None
        closer_7_sci_v2 = None

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

    # Try to import Year 8 English variants (optional)
    try:
        from statements_year8_English_variant1 import (
            opening_phrases as opening_8_eng_v1,
            attitude_bank as attitude_8_eng_v1,
            reading_bank as reading_8_eng_v1,
            writing_bank as writing_8_eng_v1,
            reading_target_bank as target_8_eng_v1,
            writing_target_bank as target_write_8_eng_v1,
            closer_bank as closer_8_eng_v1
        )
    except ImportError:
        opening_8_eng_v1 = None
        attitude_8_eng_v1 = None
        reading_8_eng_v1 = None
        writing_8_eng_v1 = None
        target_8_eng_v1 = None
        target_write_8_eng_v1 = None
        closer_8_eng_v1 = None

    try:
        from statements_year8_English_variant2 import (
            opening_phrases as opening_8_eng_v2,
            attitude_bank as attitude_8_eng_v2,
            reading_bank as reading_8_eng_v2,
            writing_bank as writing_8_eng_v2,
            reading_target_bank as target_8_eng_v2,
            writing_target_bank as target_write_8_eng_v2,
            closer_bank as closer_8_eng_v2
        )
    except ImportError:
        opening_8_eng_v2 = None
        attitude_8_eng_v2 = None
        reading_8_eng_v2 = None
        writing_8_eng_v2 = None
        target_8_eng_v2 = None
        target_write_8_eng_v2 = None
        closer_8_eng_v2 = None

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

    # Try to import Year 8 Science variants (optional)
    try:
        from statements_year8_science_variant1 import (
            opening_phrases as opening_8_sci_v1,
            attitude_bank as attitude_8_sci_v1,
            science_bank as science_8_sci_v1,
            target_bank as target_8_sci_v1,
            closer_bank as closer_8_sci_v1
        )
    except ImportError:
        opening_8_sci_v1 = None
        attitude_8_sci_v1 = None
        science_8_sci_v1 = None
        target_8_sci_v1 = None
        closer_8_sci_v1 = None

    try:
        from statements_year8_science_variant2 import (
            opening_phrases as opening_8_sci_v2,
            attitude_bank as attitude_8_sci_v2,
            science_bank as science_8_sci_v2,
            target_bank as target_8_sci_v2,
            closer_bank as closer_8_sci_v2
        )
    except ImportError:
        opening_8_sci_v2 = None
        attitude_8_sci_v2 = None
        science_8_sci_v2 = None
        target_8_sci_v2 = None
        closer_8_sci_v2 = None

except ImportError as e:
    st.error(f"Missing required statement files: {e}")
    st.stop()

# ========== SECURITY FUNCTIONS ==========
def validate_upload_rate():
    """Prevent rapid-fire uploads/abuse"""
    time_since_last = datetime.now() - st.session_state.last_upload_time
    if time_since_last < timedelta(seconds=RATE_LIMIT_SECONDS):
        wait_time = RATE_LIMIT_SECONDS - time_since_last.seconds
        st.error(f"Please wait {wait_time} seconds before uploading again")
        return False
    return True

def sanitize_input(text, max_length=100):
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    sanitized = ''.join(c for c in text if c.isalnum() or c in " .'-")
    return sanitized[:max_length].strip().title()

def validate_file(file):
    """Validate uploaded file size and type"""
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"File too large (max {MAX_FILE_SIZE_MB}MB)"
    if not file.name.lower().endswith('.csv'):
        return False, "Only CSV files allowed"
    return True, ""

def process_csv_securely(uploaded_file):
    """Process CSV with auto-cleanup of temp files"""
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
        try:
            os.unlink(temp_path)
        except:
            pass

# ========== HELPER FUNCTIONS ==========
def get_variant_statements(subject, year, variant):
    """
    Get the appropriate statement banks based on subject, year, and variant.
    Returns tuple of (opening, attitude, reading/science, writing, reading_target, writing_target, closer)
    Returns None if variant doesn't exist - will fall back to original.
    """
    # Year 5 variants
    if year == 5:
        if subject == "English":
            if variant == 1 and opening_5_eng_v1 is not None:
                return (opening_5_eng_v1, attitude_5_eng_v1, reading_5_eng_v1, writing_5_eng_v1,
                       target_5_eng_v1, target_write_5_eng_v1, closer_5_eng_v1)
            elif variant == 2 and opening_5_eng_v2 is not None:
                return (opening_5_eng_v2, attitude_5_eng_v2, reading_5_eng_v2, writing_5_eng_v2,
                       target_5_eng_v2, target_write_5_eng_v2, closer_5_eng_v2)
            else:
                return (opening_5_eng, attitude_5_eng, reading_5_eng, writing_5_eng,
                       target_5_eng, target_write_5_eng, closer_5_eng)
        
        elif subject == "Maths":
            if variant == 1 and opening_5_maths_v1 is not None:
                return (opening_5_maths_v1, attitude_5_maths_v1, number_5_maths_v1, None,
                       target_5_maths_v1, None, closer_5_maths_v1)
            elif variant == 2 and opening_5_maths_v2 is not None:
                return (opening_5_maths_v2, attitude_5_maths_v2, number_5_maths_v2, None,
                       target_5_maths_v2, None, closer_5_maths_v2)
            else:
                return (opening_5_maths, attitude_5_maths, number_5_maths, None,
                       target_5_maths, None, closer_5_maths)
        
        elif subject == "Science":
            if variant == 1 and opening_5_sci_v1 is not None:
                return (opening_5_sci_v1, attitude_5_sci_v1, science_5_sci_v1, None,
                       target_5_sci_v1, None, closer_5_sci_v1)
            elif variant == 2 and opening_5_sci_v2 is not None:
                return (opening_5_sci_v2, attitude_5_sci_v2, science_5_sci_v2, None,
                       target_5_sci_v2, None, closer_5_sci_v2)
            else:
                return (opening_5_sci, attitude_5_sci, science_5_sci, None,
                       target_5_sci, None, closer_5_sci)
    
    # Year 7 variants
    elif year == 7:
        if subject == "English":
            if variant == 1 and opening_7_eng_v1 is not None:
                return (opening_7_eng_v1, attitude_7_eng_v1, reading_7_eng_v1, writing_7_eng_v1,
                       target_7_eng_v1, target_write_7_eng_v1, closer_7_eng_v1)
            elif variant == 2 and opening_7_eng_v2 is not None:
                return (opening_7_eng_v2, attitude_7_eng_v2, reading_7_eng_v2, writing_7_eng_v2,
                       target_7_eng_v2, target_write_7_eng_v2, closer_7_eng_v2)
            else:
                return (opening_7_eng, attitude_7_eng, reading_7_eng, writing_7_eng,
                       target_7_eng, target_write_7_eng, closer_7_eng)

        elif subject == "Science":
            if variant == 1 and opening_7_sci_v1 is not None:
                return (opening_7_sci_v1, attitude_7_sci_v1, science_7_sci_v1, None,
                       target_7_sci_v1, None, closer_7_sci_v1)
            elif variant == 2 and opening_7_sci_v2 is not None:
                return (opening_7_sci_v2, attitude_7_sci_v2, science_7_sci_v2, None,
                       target_7_sci_v2, None, closer_7_sci_v2)
            else:
                return (opening_7_sci, attitude_7_sci, science_7_sci, None,
                       target_7_sci, None, closer_7_sci)
    
    # Year 8 variants
    elif year == 8:
        if subject == "English":
            if variant == 1 and opening_8_eng_v1 is not None:
                return (opening_8_eng_v1, attitude_8_eng_v1, reading_8_eng_v1, writing_8_eng_v1,
                       target_8_eng_v1, target_write_8_eng_v1, closer_8_eng_v1)
            elif variant == 2 and opening_8_eng_v2 is not None:
                return (opening_8_eng_v2, attitude_8_eng_v2, reading_8_eng_v2, writing_8_eng_v2,
                       target_8_eng_v2, target_write_8_eng_v2, closer_8_eng_v2)
            else:
                return (opening_8_eng, attitude_8_eng, reading_8_eng, writing_8_eng,
                       target_8_eng, target_write_8_eng, closer_8_eng)

        elif subject == "Science":
            if variant == 1 and opening_8_sci_v1 is not None:
                return (opening_8_sci_v1, attitude_8_sci_v1, science_8_sci_v1, None,
                       target_8_sci_v1, None, closer_8_sci_v1)
            elif variant == 2 and opening_8_sci_v2 is not None:
                return (opening_8_sci_v2, attitude_8_sci_v2, science_8_sci_v2, None,
                       target_8_sci_v2, None, closer_8_sci_v2)
            else:
                return (opening_8_sci, attitude_8_sci, science_8_sci, None,
                       target_8_sci, None, closer_8_sci)
    
    # Return None for subjects without variants (will use original in generate_comment)
    return None

def get_pronouns(gender):
    gender = gender.lower()
    if gender == "male":
        return "he", "his"
    elif gender == "female":
        return "she", "her"
    return "they", "their"

def lowercase_first(text):
    return text[0].lower() + text[1:] if text else ""

def truncate_comment(comment, target=TARGET_CHARS):
    if len(comment) <= target:
        return comment
    truncated = comment[:target].rstrip(" ,;.")
    if "." in truncated:
        truncated = truncated[:truncated.rfind(".")+1]
    return truncated

def fix_pronouns_in_text(text, pronoun, possessive):
    """Fix gender pronouns in statement text using word boundaries"""
    if not text:
        return text

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
def generate_comment(subject, year, name, gender, att, achieve, target, pronouns, attitude_target=None, variant=0):
    """
    Generate a report comment.

    Args:
        variant (int): 0 = original, 1 = variant1, 2 = variant2
    """
    p, p_poss = pronouns
    name = sanitize_input(name)

    # Try to get variant statements
    variant_statements = get_variant_statements(subject, year, variant)
    
    if variant_statements is not None:
        opening_bank, attitude_bank, reading_bank, writing_bank, reading_target_bank, writing_target_bank, closer_bank = variant_statements
    else:
        # Fall back to original statements
        if year == 5:
            if subject == "English":
                opening_bank = opening_5_eng
                attitude_bank = attitude_5_eng
                reading_bank = reading_5_eng
                writing_bank = writing_5_eng
                reading_target_bank = target_5_eng
                writing_target_bank = target_write_5_eng
                closer_bank = closer_5_eng
            elif subject == "Maths":
                opening_bank = opening_5_maths
                attitude_bank = attitude_5_maths
                reading_bank = number_5_maths
                writing_bank = None
                reading_target_bank = target_5_maths
                writing_target_bank = None
                closer_bank = closer_5_maths
            else:  # Science
                opening_bank = opening_5_sci
                attitude_bank = attitude_5_sci
                reading_bank = science_5_sci
                writing_bank = None
                reading_target_bank = target_5_sci
                writing_target_bank = None
                closer_bank = closer_5_sci
        
        elif year == 7:
            if subject == "English":
                opening_bank = opening_7_eng
                attitude_bank = attitude_7_eng
                reading_bank = reading_7_eng
                writing_bank = writing_7_eng
                reading_target_bank = target_7_eng
                writing_target_bank = target_write_7_eng
                closer_bank = closer_7_eng
            elif subject == "Maths":
                opening_bank = opening_7_maths
                attitude_bank = attitude_7_maths
                reading_bank = number_7_maths
                writing_bank = None
                reading_target_bank = target_7_maths
                writing_target_bank = None
                closer_bank = closer_7_maths
            else:  # Science
                opening_bank = opening_7_sci
                attitude_bank = attitude_7_sci
                reading_bank = science_7_sci
                writing_bank = None
                reading_target_bank = target_7_sci
                writing_target_bank = None
                closer_bank = closer_7_sci
        
        else:  # year == 8
            if subject == "English":
                opening_bank = opening_8_eng
                attitude_bank = attitude_8_eng
                reading_bank = reading_8_eng
                writing_bank = writing_8_eng
                reading_target_bank = target_8_eng
                writing_target_bank = target_write_8_eng
                closer_bank = closer_8_eng
            elif subject == "Maths":
                opening_bank = opening_8_maths
                attitude_bank = attitude_8_maths
                reading_bank = maths_8_maths
                writing_bank = None
                reading_target_bank = target_8_maths
                writing_target_bank = None
                closer_bank = closer_8_maths
            else:  # Science
                opening_bank = opening_8_sci
                attitude_bank = attitude_8_sci
                reading_bank = science_8_sci
                writing_bank = None
                reading_target_bank = target_8_sci
                writing_target_bank = None
                closer_bank = closer_8_sci

    # Generate comment using the selected banks
    opening = random.choice(opening_bank)
    attitude_text = fix_pronouns_in_text(attitude_bank[att], p, p_poss)
    attitude_sentence = f"{opening} {name} {attitude_text}"
    if not attitude_sentence.endswith('.'):
        attitude_sentence += '.'

    # Reading/Science section
    if reading_bank:
        reading_text = fix_pronouns_in_text(reading_bank[achieve], p, p_poss)
        if reading_text[0].islower():
            reading_text = f"{p} {reading_text}"
        
        if subject == "English":
            reading_sentence = f"In reading, {reading_text}"
        else:
            reading_sentence = reading_text
        
        if not reading_sentence.endswith('.'):
            reading_sentence += '.'
    else:
        reading_sentence = ""

    # Writing section (only for English)
    if writing_bank:
        writing_text = fix_pronouns_in_text(writing_bank[achieve], p, p_poss)
        if writing_text[0].islower():
            writing_text = f"{p} {writing_text}"
        writing_sentence = f"In writing, {writing_text}"
        if not writing_sentence.endswith('.'):
            writing_sentence += '.'
    else:
        writing_sentence = ""

    # Targets
    if reading_target_bank:
        reading_target_text = fix_pronouns_in_text(reading_target_bank[target], p, p_poss)
        reading_target_sentence = f"For the next term, {p} should {lowercase_first(reading_target_text)}"
        if not reading_target_sentence.endswith('.'):
            reading_target_sentence += '.'
    else:
        reading_target_sentence = ""

    if writing_target_bank:
        writing_target_text = fix_pronouns_in_text(writing_target_bank[target], p, p_poss)
        writing_target_sentence = f"Additionally, {p} should {lowercase_first(writing_target_text)}"
        if not writing_target_sentence.endswith('.'):
            writing_target_sentence += '.'
    else:
        writing_target_sentence = ""

    # Closer
    closer_sentence = random.choice(closer_bank) if closer_bank else ""

    # Optional attitude target
    if attitude_target:
        attitude_target = sanitize_input(attitude_target)
        attitude_target_sentence = f"{lowercase_first(attitude_target)}"
        if not attitude_target_sentence.endswith('.'):
            attitude_target_sentence += '.'
        attitude_target_sentence = attitude_target_sentence.replace('..', '.')
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

    # Fix punctuation
    if not comment.endswith('.'):
        comment += '.'
    comment = comment.replace('..', '.')

    comment = truncate_comment(comment, TARGET_CHARS)

    # Double-check ending punctuation after truncation
    if not comment.endswith('.'):
        comment = comment.rstrip(' ,;') + '.'
    comment = comment.replace('..', '.')

    return comment

# ========== STREAMLIT APP LAYOUT ==========

# Sidebar
with st.sidebar:
    st.title("📚 Navigation")

    app_mode = st.radio(
        "Choose Mode",
        ["Single Student", "Batch Upload", "Privacy Info"]
    )

    st.markdown("---")
    st.markdown("### 🔒 Privacy Features")
    st.info("""
    - No data stored on servers
    - All processing in memory
    - Auto-deletion of temp files
    - Input sanitization
    - Rate limiting enabled
    """)

    if st.button("🔄 Clear All Data", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.session_state.app_initialized = True
        st.session_state.upload_count = 0
        st.session_state.last_upload_time = datetime.now()
        st.success("All data cleared!")
        st.rerun()

    st.markdown("---")
    st.caption("v3.0 • Multi-Year Edition")

# Main content
col1, col2 = st.columns([1, 4])

with col1:
    try:
        st.image("logo.png", use_column_width=True)
    except:
        st.markdown("""
        <div style='text-align: center;'>
            <div style='font-size: 72px;'>📚</div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.title("Multi-Subject Report Comment Generator")
    st.caption("~499 characters • Years 5, 7 & 8 • English, Maths, Science")

st.warning("""
**PRIVACY NOTICE:** All data is processed in memory only. No files are stored on our servers.
Close browser tab to completely erase all data.
""", icon="🔒")

# Progress tracker
st.subheader("🎯 Three Easy Steps")

if 'progress' not in st.session_state:
    st.session_state.progress = 1

step_col1, step_col
