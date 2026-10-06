import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

from ui.base_layout import style_background_dashboard, style_base_layout

from database.db import check_teacher_exists, teacher_login, create_teacher, get_teacher_subject, get_attendance_for_teacher

from database.config import supabase
from components.dialog import create_subject_dialog
from components.subject_card import subject_card
from components.header import header_dashboard
from components.share_subjects import share_subject_dialog
from components.dialog_add_photos import add_photos_dialog
from components.dialog_attendance_results import attendance_result_dialog
from components.dialog_voice_attendance import voice_attendance_dialog

from pipelines.face_pipeline import predict_attendance


# Main teacher screen controller
def teacher_screen():
    style_base_layout()
    style_background_dashboard()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif "teacher_login_type" not in st.session_state or st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()


# Teacher dashboard after successful login
def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns([2, 1], vertical_alignment="center")

    with c1:
        header_dashboard()
        st.markdown("""
            <h2 style="font-size:24px;font-weight:700;margin-top:5px;margin-bottom:0;">
                AI &amp; Computer Engineering
            </h2>
        """, unsafe_allow_html=True)

    with c2:
        st.header(f"""Welcome, {teacher_data['name']}""")
        if st.button("Logout", key="loginbackbtn", shortcut="control+backspace"):
            st.session_state["is_logged_in"] = False
            del st.session_state.teacher_data
            st.rerun()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == "take_attendance" else "tertiary"
        if st.button("Take Attendance", type=type1, width="stretch", icon=":material/how_to_reg:"):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == "manage_subjects" else "tertiary"
        if st.button("Manage Subject", type=type2, width="stretch", icon=":material/menu_book:"):
            st.session_state.current_teacher_tab = "manage_subjects"
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == "take_records" else "tertiary"
        if st.button("Take Records", type=type3, width="stretch", icon=":material/history:"):
            st.session_state.current_teacher_tab = "take_records"
            st.rerun()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "take_records":
        teacher_tab_take_records()


# Take attendance using photos or voice
def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    st.header("Take AI Attendance.")

    # Initialize uploaded attendance photos
    if "attendance_image" not in st.session_state:
        st.session_state.attendance_image = []

    subjects = get_teacher_subject(teacher_id)
    if not subjects:
        st.warning("You haven't created any subjects yet! please create one to begin!")
        return

    subject_options = {f"{s['name']} - {s['subject_code']}": s["subject_id"] for s in subjects}
    col1, col2 = st.columns([3,1], vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox("Select your Subjects", options=list(subject_options.keys()))
    with col2:
        if st.button("Add Photos", type="primary", icon=":material/photo_library:", width="stretch",):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]
    st.divider()

    if st.session_state.attendance_image:
        st.header("Add Photos")
        gallery_image = st.columns(4)

        # Display uploaded images in four columns
        for idx, img in enumerate(st.session_state.attendance_image):
            with gallery_image[idx % 4]:
                st.image(img, width="stretch", caption=f"photo {idx + 1}")

    has_photos = bool(st.session_state.attendance_image)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Clear All photos", width="stretch", type="tertiary",
                     icon=":material/delete:", disabled=not has_photos):
            st.session_state.attendance_image = []
            st.rerun()

    with c2:
        if st.button("Run Face Analysis", width="stretch", type="secondary",
                     icon=":material/analytics:", disabled=not has_photos):
            with st.spinner("Deep scanning classroom photos...."):
                all_detected_id = {}

                # Detect students from every uploaded image
                for idx, img in enumerate(st.session_state.attendance_image):
                    img_np = np.array(img.convert("RGB"))
                    detected, _, _ = predict_attendance(img_np)
                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)
                            all_detected_id.setdefault(student_id, []).append(f"photos {idx + 1}")

                enrolled_res = supabase.table("subject_students").select(
                    "*, students(*)"
                ).eq("subject_id", selected_subject_id).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning("No students enrolled in this course")
                else:
                    results, attendance_to_log = [], []
                    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    for node in enrolled_students:
                        student = node["students"]
                        sources = all_detected_id.get(int(student["student_id"]), [])
                        is_present = len(sources) > 0

                        results.append({
                            "Name": student["name"],
                            "ID": student["student_id"],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "Present" if is_present else "Absent"
                        })

                        attendance_to_log.append({
                            "student_id": student['student_id'],
                            "subject_id": selected_subject_id,
                            "timestamp": current_date,
                            "is_present": bool(is_present)
                        })

                    # Show final attendance result
                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button("Use Voice Attendance", type="primary", width="stretch", icon=":material/mic:"):
            voice_attendance_dialog(selected_subject_id)


# Manage teacher subjects
def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    col1, col2 = st.columns(2)

    with col1:
        st.header("Manage Subject", width="stretch")
    with col2:
        if st.button("Create New Subjects", width="stretch"):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subject(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [("👨‍🎓", "Students", sub["total_students"]),
                     ("📚", "Classes", sub["total_classes"])]

            def share_btn():
                if st.button(f"Share Code: {sub['name']}", key=f"Share_{sub['subject_code']}",
                             icon=":material/share:"):
                    share_subject_dialog(sub["name"], sub["subject_code"])
                st.space()

            subject_card(name=sub["name"], code=sub["subject_code"],
                         section=sub["section"], stats=stats, footer_callback=share_btn)
    else:
        st.info("No Subject Founds.")


def teacher_tab_take_records():
    st.header("Take Attendance Records.")
    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        return 

    data = []

    for r in records:
        ts = r.get('timestamp')

        data.append({
            "ts_group": ts.split(".") [0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
            "Subject": r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present', False))
        })

        df = pd.DataFrame(data)

        summary = (
            df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
            .agg(
                Present_Count = ('is_present', 'sum'),
                Total_Count = ('is_present', 'count')
            ).reset_index()
        )

        summary['Attendance Stats'] = (
            "🙋‍♀️" + " " + summary['Present_Count'].astype(str) + " /" 
            + summary['Total_Count'].astype(str) + 'Students'
        )

        display_df = (summary.sort_values(by='ts_group', ascending=False)
                      [['Time', 'Subject', 'Subject Code', 'Attendance Stats']]
                      )

        st.dataframe(display_df, width='stretch', hide_index=True)






# Handle teacher login
def login_teacher(username, password):
    if not username or not password:
        return False

    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role = "teacher"
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False


# Display teacher login page
def teacher_screen_login():
    c1, c2 = st.columns([2, 1], vertical_alignment="center")
    with c1:
        header_dashboard()
        st.markdown("""<h2 style="font-size:24px;font-weight:700;">
            AI &amp; Computer Engineering</h2>""", unsafe_allow_html=True)

    with c2:
        if st.button("Go back to Home", key="loginbackbtn", shortcut="control+backspace"):
            st.session_state["login_type"] = None
            st.rerun()

    st.header("Login using password", text_alignment="center")
    st.space()
    teacher_username = st.text_input("Enter username", placeholder="Enter username")
    teacher_pass = st.text_input("Enter Password", type="password", placeholder="Enter password")
    st.divider()
    btnc1, btnc2 = st.columns(2, vertical_alignment="center", gap="xxlarge")

    with btnc1:
        if st.button("Login", icon=":material/passkey:", shortcut="control+enter", width="stretch"):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("welcome back!")
                st.rerun()
            else:
                st.error("Check Your username or password!")

    with btnc2:
        if st.button("Register Instead", icon=":material/passkey:", width="stretch"):
            st.session_state.teacher_login_type = "register"
            st.rerun()


# Handle teacher registration
def register_techer(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_name or not teacher_username or not teacher_pass:
        return False, "All fields are required"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken"
    if teacher_pass != teacher_pass_confirm:
        return False, "Password doesn't match"

    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Sucessfully Created! , login Now"
    except Exception:
        return False, "Unexpected Error!"


# Display teacher registration page
def teacher_screen_register():
    c1, c2 = st.columns([2, 1], vertical_alignment="center")
    with c1:
        header_dashboard()
        st.markdown("""<h2 style="font-size:24px;font-weight:700;">
            AI &amp; Computer Engineering</h2>""", unsafe_allow_html=True)

    with c2:
        if st.button("Go back to Home", key="loginbackbtn", shortcut="control+backspace"):
            st.session_state["login_type"] = None
            st.rerun()

    st.header("Register your teacher profile", text_alignment="center")
    teacher_username = st.text_input("Enter username", placeholder="Enter username")
    teacher_name = st.text_input("Enter name", placeholder="Enter name")
    teacher_pass = st.text_input("Enter Password", type="password", placeholder="Enter password")
    teacher_pass_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
    st.divider()
    btnc1, btnc2 = st.columns(2, vertical_alignment="center", gap="xxlarge")

    with btnc1:
        if st.button("Register", icon=":material/passkey:", shortcut="control+enter", width="stretch"):
            success, message = register_techer(
                teacher_username, teacher_name, teacher_pass, teacher_pass_confirm
            )
            if success:
                st.success(message)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)

    with btnc2:
        if st.button("Login Instead", icon=":material/passkey:", width="stretch"):
            st.session_state.teacher_login_type = "login"
            st.rerun()