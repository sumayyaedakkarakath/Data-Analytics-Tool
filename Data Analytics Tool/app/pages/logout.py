import streamlit as st

st.session_state.logged_in = False

for key in ["dataset_1", "dataset_2"]:
    st.session_state.pop(key, None)

st.rerun()