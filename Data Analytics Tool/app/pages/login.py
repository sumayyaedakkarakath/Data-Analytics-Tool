import streamlit as st
from pathlib import Path

# 1. Page Config
st.set_page_config(page_title="Login | Data Analytics Tool", layout="wide", initial_sidebar_state="collapsed")
page_col = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #EDEDED;
}
.stAppHeader {
    background-color: #00488e;
}
.stAppHeader * {
    color: white !important;
}

/* Hide Streamlit header */
[data-testid="stHeader"] {
    display: none;
}
</style>
"""
st.markdown(page_col, unsafe_allow_html=True)



import base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


img_path = Path(__file__).parent / "dashboard illustration.png"
img_base64 = get_base64_image(img_path)


st.markdown("""
    <style>
        /* Remove top padding and header */
        [data-testid="stHeader"] 
        .block-container {padding: 0 !important; max-width: 100% !important;}
        [data-testid="column"] {display: flex; align-items: center; justify-content: center;}

        /* Left Branding Panel */
        .left-panel {
            background-color: #02388F; /* Dark Navy like your first image */
            color: white;
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 40px;
            text-align: center;
        }

        /* Right Form Panel */
        .right-panel {
            width: 100%;
            padding: 10% 15%;
        }
        
        /* Adjusting Streamlit's default widget spacing */
        .stTextInput, .stButton {
            margin-bottom: -10px;
        }
    </style>
    """, unsafe_allow_html=True)


col1, col2 = st.columns([1.2, 1])
def check_login(username, password):
    return username == "admin" and password == "password"


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


with col1:

    st.markdown(f'''
        <div class="left-panel">
            <img src="data:image/png;base64,{img_base64}">
        </div>
    ''', unsafe_allow_html=True)
        

with col2:

    st.markdown('<div class="right-panel">', unsafe_allow_html=True)

    st.title("Login to Data Analytics tool")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.rerun()

        else:
            st.error("Invalid credentials")