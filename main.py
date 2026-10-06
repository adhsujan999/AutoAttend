import streamlit as st 

from Screens.teacher_screens import teacher_screen
from Screens.home_screens import home_screen
from Screens.student_screens import student_screen

from components.dialog_auto_enroll import auto_enroll_dialog
def app():
    st.set_page_config(
        page_title="AttendX-Making Attendance faster using AI",
        page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4NbFrV1HuaJRstxXG-s2J0np1nx0Sx26q9RnrUbntpQ&s=10"
    )
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None 

    match st.session_state['login_type']:

        case 'teacher':
            teacher_screen()

        case 'student':
            student_screen()

        case None:
            home_screen()

    join_code = st.query_params.get('join-code')

    if join_code:
        if st.session_state.login_type != 'student':
            st.session_state.login_type ='student'
            st.rerun()

        if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
            auto_enroll_dialog(join_code)


app()