import streamlit as st 
from components.header import header_home
from ui.base_layout import style_background_dashboard, style_background_home, style_base_layout

def home_screen():
    header_home()
    style_base_layout()
    style_background_home()
    style_background_dashboard()

    st.markdown("""
        <style>
            [data-testid="stImage"] {
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                height: 150px;
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="xxlarge")

    with col1:
        st.header("I am Student.")
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRp0QLAUI3Q0WQjl7-IOn5EBkXEu14MkwaO5cpoGYM6VQ&s=10" , width=120)
        if st.button('Student Portel',type="primary",icon=":material/arrow_forward:", icon_position="right"):
            st.session_state['login_type'] = 'student'
            st.rerun()

    with col2:
        st.header("I am Teacher.")
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQr57Bdpds-UMb7ifLRZZZKk-wwB-oTLrChhzU8feiGgw&s=10" , width=120)
        if st.button('Teacher Portel',type="primary",icon=":material/arrow_forward:", icon_position="right"):
            st.session_state['login_type'] = 'teacher'
            st.rerun()




