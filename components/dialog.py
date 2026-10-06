import streamlit as st 
from database.db import create_subject

@st.dialog("Create New Subjects")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of the new subjects")

    sub_id = st.text_input("Enter the subject code", placeholder="CS1001")
    sub_name = st.text_input("Enter the subject name", placeholder="Introduction to computer vision")
    sub_section = st.text_input("Section", placeholder="A")

    if st.button("Create Subject Now", type="primary", width="stretch"):
        if sub_id and sub_name and sub_section:
            try:
                create_subject(sub_id, sub_name, sub_section, teacher_id)
                st.toast("Subject Created Sucessfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

        else:
            st.warning("Please fill all the fields")