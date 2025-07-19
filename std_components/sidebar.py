import streamlit as st

def sidebar(user):
    st.sidebar.success(f"✅ Welcome {user.name}!")
    st.sidebar.write(f"🧑 Role: {user.role}")
    st.sidebar.button("Log out", on_click=st.logout)