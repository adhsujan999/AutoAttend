import streamlit as st

def header_home():

    logo_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4NbFrV1HuaJRstxXG-s2J0np1nx0Sx26q9RnrUbntpQ&s=10"

    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:30px;">
            <img src="{logo_url}" style="height:150px;" />
            <h2 style="text-align:center; color:#000000;">Department of AI & Computer Engineering</h2>
        </div>
    """, unsafe_allow_html=True)


def header_dashboard():

    logo_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4NbFrV1HuaJRstxXG-s2J0np1nx0Sx26q9RnrUbntpQ&s=10"

    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src="{logo_url}" style="height:100px;" />
        </div>
    """, unsafe_allow_html=True)