import streamlit as st
from dotenv import load_dotenv

from utils.roles import ROLES
from utils.db import get_user, create_user, update_user_role, get_all_clients

from std_components.auth import login_screen, onboarding_role_selection
from std_components.client import render_client
from std_components.coach import render_coach
from std_components.sidebar import sidebar

from streamlit_javascript import st_javascript
from zoneinfo import ZoneInfo


def get_tz():
    user_timezone_str = st_javascript("""await (async () => {
        return Intl.DateTimeFormat().resolvedOptions().timeZone;
    })().then(returnValue => returnValue)""")
   
    if not user_timezone_str:
        user_timezone_str = "UTC"

    return ZoneInfo(user_timezone_str)


# --- Setup ---
st.set_page_config(page_title="AI Coaching Assistant", layout="wide")
load_dotenv()


def fetch_all_clients():
    return get_all_clients()


# --- Login UI ---
if not hasattr(st, "user") or not st.user.is_logged_in:
    login_screen()
    st.stop()


# --- Session State Initialization ---
if "current_plan" not in st.session_state:
    st.session_state.current_plan = {}

if "calendar_update_counter" not in st.session_state:
    st.session_state.calendar_update_counter = 1

if "edit_selected_goal" not in st.session_state:
    st.session_state.edit_selected_goal = ""

# Get or create current user
if "current_user" not in st.session_state:
    user = get_user({
        "email": st.user.email,
        "name": st.user.name
    })

    if user is None:
        # Create user with no role yet, mark as first_time_user=True
        user = create_user({
            "email": st.user.email,
            "name": st.user.name,
            "role": None,
            "first_time_user": True,
            "created_at": "..."  # your code for timestamp here
        })

    st.session_state.current_user = user


# --- Onboarding for first-time users ---
if st.session_state.current_user.first_time_user:
    # Render a dedicated onboarding screen for role selection
    onboarding_role_selection(st.user.email, st.user.name)
    st.stop()


# --- Fetch clients list if coach ---
if "all_clients" not in st.session_state and st.session_state.current_user.role == "coach":
    st.session_state.all_clients = get_all_clients()

# --- Get user timezone ---
if "client_tz" not in st.session_state:
    st.session_state.client_tz = get_tz()

# --- Render sidebar ---
sidebar(st.session_state.current_user)

# --- Render dashboards ---
if st.session_state.current_user.role == "coach":
    render_coach(st.session_state.current_user, st.session_state.all_clients)
else:
    render_client(st.session_state.current_user)
