import streamlit as st
from utils.db import update_client_coach
from utils.models import User

# Modal dialog
@st.dialog("Change Coach")
def change_coach_dialog(user: User):
    st.subheader("🔁 Change Your Coach")
    all_coaches = [c.email for c in st.session_state.all_coaches if c.email != user.current_coach]
    if not all_coaches:
        st.info("No other coaches available.")
        return
    selected = st.selectbox("Choose a new coach", options=all_coaches, index=None, key="modal_coach_select")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirm"):
            st.session_state.current_user.current_coach = selected
            update_client_coach(st.session_state.current_user.email, selected)
            # Use st.rerun() instead of fragment-specific rerun
            st.rerun()
    with col2:
        if st.button("❌ Cancel"):
            pass  # Close dialog, do nothing

# Callback function to handle coach selection
def on_coach_select():
    selected_coach = st.session_state.select_initial_coach
    if selected_coach and selected_coach != st.session_state.current_user.current_coach:
        st.session_state.current_user.current_coach = selected_coach
        update_client_coach(st.session_state.current_user.email, selected_coach)

# Sidebar fragment that can rerun independently
@st.fragment
def coach_sidebar_fragment(user: User):
    current_coach = st.session_state.current_user.current_coach
    if current_coach:
        st.write(f"Your coach: {current_coach}")
        if st.button("🔁 Change Coach", key="change_coach_btn"):
            change_coach_dialog(user)
    else:
        st.warning("You don't have a coach yet!")
        all_coaches = [c.email for c in st.session_state.all_coaches]
        client_coach = st.selectbox(
            "Select your coach", 
            options=all_coaches, 
            index=None, 
            key="select_initial_coach",
            on_change=on_coach_select  # Use callback for immediate response
        )

def sidebar(user: User) -> None:
    st.sidebar.button("Log out", on_click=st.logout)
    st.sidebar.success(f"✅ Welcome {user.name}!")
    st.sidebar.write(f"🧑 Role: {user.role}")
    if user.role != "coach":
        with st.sidebar:
            coach_sidebar_fragment(user)
    # Remove the trigger logic as it's not needed with the fix above