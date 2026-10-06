import streamlit as st
import time

from database.config import supabase
from PIL import Image

@st.dialog('Capture or Add Photos')

def add_photos_dialog():
    st.write('Add classroom photos to scan for attendance')

    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab = 'camera'
    tab1, tab2 = st.columns(2)

    with tab1:
        type_camera = "primary" if st.session_state.photo_tab == 'camera' else 'tertiary'
        if st.button('camera', type=type_camera, width='stretch'):
            st.session_state.photo_tab = 'camera'

    with tab1:
        type_camera = "primary" if st.session_state.photo_tab == 'upload' else 'tertiary'
        if st.button('Upload Photos', type=type_camera, width='stretch'):
            st.session_state.photo_tab = 'upload'


    if st.session_state.photo_tab  == 'camera':
        cam_photo = st.camera_input('Take Snapshot', key='dialog_cam')
        if cam_photo:
            st.session_state.attendance_image.append(Image.open(cam_photo))
            st.toast('Photo captured')
            st.rerun()

    if st.session_state.photo_tab  == 'upload':
        uploaded_files = st.file_uploader('Choose image files', type=['jpg', 'png', 'jepg'], accept_multiple_files=True, key = 'dialog_cam')

        if uploaded_files:
            for f in uploaded_files:
                st.session_state.attndance_images.append(Image.open(f))
                st.toast("Photo Uploaded SuccessFully")
                st.rerun()

    st.divider()
    if st.button('Done', type='primary', width='stretch'):
        st.rerun()
