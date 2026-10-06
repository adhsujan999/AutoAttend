import streamlit as st


def style_background_home():
    st.markdown("""
        <style>
            [data-testid="stColumn"] {
                background: white;
                padding: 25px;
                border-radius: 25px;
                max-width: 300px;
                min-height: 320px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }

            [data-testid="stImage"] {
                display: flex;
                justify-content: center;
                width: 100%;
            }
        </style>
    """, unsafe_allow_html=True)


def style_background_dashboard():
    st.markdown("""
        <style>
            .stApp {
                background: #E0E3FF;
            }
        </style>
    """, unsafe_allow_html=True)


def style_base_layout():
    st.markdown("""
        <style>
            /* Hide Streamlit menu */
            #MainMenu, footer, header {
                visibility: hidden;
            }

            /* Main heading */
            h1 {
                font-size: 2.5rem !important;
                font-weight: 800 !important;
                text-align: center;
            }

            /* Student & Teacher heading */
            h2 {
                font-size: 1.4rem !important;
                font-weight: 800 !important;
            }

            /* Primary button */
            button[kind="primary"] {
                background: #5865F2 !important;
                color: white !important;
                border-radius: 10px !important;
                font-weight: 600 !important;
            }

            /* Material icon */
            .material-symbols-rounded {
                font-family: 'Material Symbols Rounded' !important;
            }
        </style>
    """, unsafe_allow_html=True)