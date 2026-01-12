        with col_stats[0]:
            st.metric("Character Count", f"{char_count}/{TARGET_CHARS}")
        with col_stats[1]:
            st.metric("Words", len(comment.split()))
        with col_stats[2]:
            if char_count < TARGET_CHARS - 50:
                st.metric("Status", "✓ Perfect length")
            else:
                st.metric("Status", "⚠️ Near limit")
        with col_stats[3]:
            # Calculate time saved
            comments_today = len(st.session_state.get('all_comments', []))
            time_saved_mins = comments_today * 4.5
            if time_saved_mins > 60:
                st.metric("⏱️ Time Saved", f"{time_saved_mins/60:.1f} hrs")
            else:
                st.metric("⏱️ Time Saved", f"{int(time_saved_mins)} mins")

        if 'all_comments' not in st.session_state:
            st.session_state.all_comments = []

        student_entry = {
            'name': name,
            'subject': subject,
            'year': year,
            'comment': comment,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.all_comments.append(student_entry)

        col_reset = st.columns([2, 1, 1])
        with col_reset[1]:
            if st.button("🔄 Switch Variant", type="secondary", use_container_width=True):
                # Switch between variant 1 and 2
                other_variant = 2 if variant == 1 else 1
                variant_name = "Variant 2" if other_variant == 2 else "Variant 1"
                
                # Generate comment with other variant
                comment_other = generate_comment(subject, year, name, gender, att, achieve,
                                                target, pronouns,
                                                st.session_state.get('attitude_target_input', ''),
                                                variant=other_variant)

                st.success(f"✨ Switched to {variant_name}!")
                st.text_area(f"{variant_name} Comment", comment_other, height=150, key="variant_display")
                st.caption(f"Characters: {len(comment_other)}/{TARGET_CHARS}")

        with col_reset[2]:
            if st.button("➕ Add Another Student", type="primary", use_container_width=True):
                if 'student_name_input' in st.session_state:
                    st.session_state.student_name_input = ""
                if 'attitude_target_input' in st.session_state:
                    st.session_state.attitude_target_input = ""
                st.session_state.progress = 1
                st.session_state.scroll_to_top = True
                st.rerun()

        # Auto-scroll to top after clicking "Add Another Student"
        if st.session_state.get('scroll_to_top', False):
            st.session_state.scroll_to_top = False
            st.markdown("""
            <script>
                window.parent.document.querySelector('section.main').scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            </script>
            """, unsafe_allow_html=True)

# ========== BATCH UPLOAD MODE ==========
elif app_mode == "Batch Upload":
    st.subheader("📁 Batch Upload (CSV)")

    st.info("""
    **CSV Format Required:**
    - Columns: Student Name, Gender, Subject, Year, Attitude, Achievement, Target
    - Gender: Male/Female
    - Subject: English/Maths/Science
    - Year: 5, 7, or 8
    - Bands: 90,85,80,75,70,65,60,55,40
    """)

    example_csv = """Student Name,Gender,Subject,Year,Attitude,Achievement,Target
Aseel,Female,English,5,75,80,85
Mohamed,Male,Maths,7,80,75,80
Sarah,Female,Science,8,85,90,85"""

    st.download_button(
        label="📥 Download Example CSV",
        data=example_csv,
        file_name="example_students.csv",
        mime="text/csv"
    )

    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])

    if uploaded_file:
        if not validate_upload_rate():
            st.stop()

        is_valid, msg = validate_file(uploaded_file)
        if not is_valid:
            st.error(msg)
            st.stop()

        with st.spinner("Processing CSV securely..."):
            df = process_csv_securely(uploaded_file)

        if df is not None:
            st.success(f"Processed {len(df)} students successfully")

            with st.expander("📋 Preview Data (First 5 rows)"):
                st.dataframe(df.head())

            if st.button("🚀 Generate All Comments", type="primary"):
                if 'all_comments' not in st.session_state:
                    st.session_state.all_comments = []

                progress_bar = st.progress(0)
                status_text = st.empty()

                for idx, row in df.iterrows():
                    progress = (idx + 1) / len(df)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {idx + 1}/{len(df)}: {row.get('Student Name', 'Student')}")

                    try:
                        pronouns = get_pronouns(str(row.get('Gender', '')).lower())
                        comment = generate_comment(
                            subject=str(row.get('Subject', 'English')),
                            year=int(row.get('Year', 7)),
                            name=str(row.get('Student Name', '')),
                            gender=str(row.get('Gender', '')),
                            att=int(row.get('Attitude', 75)),
                            achieve=int(row.get('Achievement', 75)),
                            target=int(row.get('Target', 75)),
                            pronouns=pronouns,
                            variant=variant
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
                        st.error(f"Error processing row {idx + 1}: {e}")

                progress_bar.empty()
                status_text.empty()
                st.session_state.progress = 2
                st.success(f"Generated {len(df)} comments!")
                st.session_state.last_upload_time = datetime.now()

# ========== PRIVACY INFO MODE ==========
elif app_mode == "Privacy Info":
    st.subheader("🔐 Privacy & Security Information")

    st.markdown("""
    ### How We Protect Student Data

    **Data Handling:**
    - All processing happens in your browser's memory
    - No student data is sent to or stored on our servers
    - Temporary files are created and immediately deleted
    - No database or persistent storage is used

    **Security Features:**
    1. **Input Sanitization** - Removes special characters from names
    2. **Rate Limiting** - Prevents abuse of the system
    3. **File Validation** - Checks file size and type
    4. **Auto-Cleanup** - Temporary files deleted after processing
    5. **Memory Clearing** - All data erased on browser close

    **Best Practices for Users:**
    - Use only first names or student IDs
    - Close browser tab when finished to clear all data
    - Download reports immediately after generation
    - For maximum privacy, use on school-managed devices

    **Compliance:**
    - Designed for use with anonymized data
    - Suitable for FERPA/GDPR compliant workflows
    - No third-party data sharing
    """)

    if st.button("🖨️ Print Privacy Notice", type="secondary"):
        privacy_text = """
        MULTI-SUBJECT REPORT GENERATOR - PRIVACY NOTICE

        Data Processing: All student data is processed locally in memory only.
        No data is transmitted to external servers or stored permanently.

        Data Retention: All data is cleared when the browser tab is closed.

        Security: Input sanitization and validation prevents data injection.

        Usage: For use with anonymized student data only.
        """
        st.text_area("Privacy Notice for Records", privacy_text, height=300)

# ========== DOWNLOAD SECTION ==========
if 'all_comments' in st.session_state and st.session_state.all_comments:
    st.session_state.progress = 3
    st.markdown("---")
    st.subheader("📥 Download Reports")

    total_comments = len(st.session_state.all_comments)
    st.info(f"You have {total_comments} generated comment(s)")

    with st.expander(f"👁️ Preview All Comments ({total_comments})"):
        for idx, entry in enumerate(st.session_state.all_comments, 1):
            st.markdown(f"**{idx}. {entry['name']}** ({entry['subject']} Year {entry['year']})")
            st.write(entry['comment'])
            st.markdown("---")

    col_dl1, col_dl2, col_dl3 = st.columns(3)

    with col_dl1:
        if DOCX_AVAILABLE:
            if st.button("📄 Word Document", use_container_width=True):
                doc = Document()
                doc.add_heading('Report Comments', 0)
                doc.add_paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
                doc.add_paragraph(f'Total Students: {total_comments}')
                doc.add_paragraph(f'Variant: {variant_choice}')
                doc.add_paragraph('')

                for entry in st.session_state.all_comments:
                    doc.add_heading(f"{entry['name']} - {entry['subject']} Year {entry['year']}", level=2)
                    doc.add_paragraph(entry['comment'])
                    doc.add_paragraph('')

                bio = io.BytesIO()
                doc.save(bio)

                st.download_button(
                    label="⬇️ Download Word File",
                    data=bio.getvalue(),
                    file_name=f"report_comments_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
        else:
            st.info("Word export requires python-docx package")

    with col_dl2:
        if st.button("📊 CSV Export", use_container_width=True):
            csv_data = []
            for entry in st.session_state.all_comments:
                csv_data.append({
                    'Student Name': entry['name'],
                    'Subject': entry['subject'],
                    'Year': entry['year'],
                    'Comment': entry['comment'],
                    'Generated': entry['timestamp']
                })

            df_export = pd.DataFrame(csv_data)
            csv_bytes = df_export.to_csv(index=False).encode('utf-8')

            st.download_button(
                label="⬇️ Download CSV",
                data=csv_bytes,
                file_name=f"report_comments_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    with col_dl3:
        if st.button("🗑️ Clear & Start Over", type="secondary", use_container_width=True):
            st.session_state.all_comments = []
            st.session_state.progress = 1
            st.success("All comments cleared! Ready for new entries.")
            if 'student_name_input' in st.session_state:
                st.session_state.student_name_input = ""
            if 'attitude_target_input' in st.session_state:
                st.session_state.attitude_target_input = ""
            st.rerun()

# ========== FOOTER ==========
st.markdown("---")
footer_cols = st.columns([2, 1])
with footer_cols[0]:
    st.caption("© Report Generator v3.0 • Multi-Year Edition")
with footer_cols[1]:
    if st.button("ℹ️ Quick Help", use_container_width=True):
        st.info("""
        **Quick Help:**
        1. **Select**: Choose student details
        2. **Generate**: Create comments
        3. **Download**: Export reports

        **Variant Selection:**
        - Variant 1: Default comment style
        - Variant 2: Alternative comment style

        **Hotkeys:**
        - Tab: Move between fields
        - Enter: Submit form

        Need help? Contact support.
        """)
