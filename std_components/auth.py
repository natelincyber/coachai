import streamlit as st
from utils.db import update_user_role, get_user

def login_screen():
    st.set_page_config(page_title="Login | Coaching Assistant", page_icon="🔐", layout="centered")

    # CSS Styles
    st.markdown("""
        <style>
            .title {
                font-size: 2.5em;
                font-weight: bold;
                text-align: center;
                margin-bottom: 0.2em;
            }
            .subtitle {
                font-size: 1.2em;
                text-align: center;
                margin-bottom: 2em;
                color: var(--text-color);
            }
            .benefit-box {
                background-color: var(--background-color);
                color: var(--text-color);
                padding: 1em;
                border-radius: 12px;
                margin: 0.5em 0;
                font-size: 1em;
                border: 1px solid rgba(120, 120, 120, 0.08);
                box-shadow: 0 1px 2px rgba(0,0,0,0.03);
                text-align: center;
            }
            .footer {
                text-align: center;
                font-size: 0.85em;
                color: var(--text-color);
                margin-top: 3em;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="title">🔐 Private Coaching Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Please log in to access your personalized dashboard</div>', unsafe_allow_html=True)

    # Centering the checkbox and login button horizontally
    col_left, col_center, col_right = st.columns([8, 4, 6])
    with col_center:
        # Create two columns: one for checkbox, one for button, side by side
        if st.button("Log in", key="login_button"):
            st.login()

    st.markdown('<hr>', unsafe_allow_html=True)

    st.markdown('<div class="footer">Your data is private and secure. Only you and your coach have access.</div>', unsafe_allow_html=True)


def onboarding_role_selection(user_email: str, user_name: str):
    st.title("Welcome to the Coaching Assistant!")
    st.write(f"Hi **{user_name}**, please select your role to get started:")

    role = st.radio(
        "Select your role:",
        options=["Client", "Coach"],
        index=0
    )

    if st.button("Confirm Role"):
        selected_role = role.lower()
        try:
            update_user_role(user_email, selected_role)
            st.success(f"Role set to '{selected_role}'. Redirecting...")
            st.session_state.current_user = get_user({"email":st.user.email})

            # Optionally reload app or redirect, e.g.
            st.rerun()
        except Exception as e:
            st.error(f"Failed to update role: {e}")