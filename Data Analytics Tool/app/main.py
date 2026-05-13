import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

login_page = st.Page("pages/login.py", title="Login", default=True)
logout_page = st.Page("pages/logout.py", title="Logout")
home_page = st.Page("pages/Home.py", title="Home")
dashboard_page = st.Page("pages/Dashboard.py", title="Dashboard")
dist_summary = st.Page("pages/Distributor Summary.py", title="Distributor Summary")
seller_summary = st.Page("pages/Seller Summary.py", title="Seller Summary")
seasonality = st.Page("pages/Seasonality.py", title="Seasonality")


if st.session_state.logged_in:
    pages = [home_page, dashboard_page, dist_summary, seller_summary, seasonality, logout_page]
else:
    pages = [login_page]


current_page = st.navigation(pages, position="top")

current_page.run()