import streamlit as st
import time 

from PIL import Image
from database.db import create_attendance


# Normal function because Streamlit does not allow a dialog inside another dialog
def show_attendance_result(df, logs):
    st.write('Please review attendance before confirming.')
    st.dataframe(df, hide_index=True, width='stretch')

    c1, c2 = st.columns(2)

    with c1:
        if st.button('Discard', width='stretch'):
            st.rerun()

    with c2:
        if st.button('Confirm & save', type='primary', width='stretch'):
            try:
                create_attendance(logs)
                st.toast('Attendance taken')

                # Same session state name used in teacher.py
                st.session_state.attendance_image = []

                st.rerun()

            except Exception as e:
                st.error(f'Sync failed! {e}')


# Only this function should open the dialog
@st.dialog("Attendance Reports")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)