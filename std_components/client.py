import streamlit as st

from std_components.calendar_display import render_calendar
from std_components.client_transcript import render_newgoals
from std_components.goals_display import render_goals
from std_components.checkin import render_checkin
from std_components.main_goal import render_maingoal
from std_components.graphs import render_graphs
from utils.models import User

def render_client(user: User):
    st.title("🧘 Your Coaching Plan")

    plan = user.currentPlan

    # Always render the tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏁 Your Goals", "📄 Plan Goals", "📅 Calendar", 
        "✅ Today's Goals", "🎯 Main Goal Progress", "🧭 My Journey"
    ])

    with tab1:
        st.subheader("🎯 Goals for this Session")
        render_goals(user, user)

    with tab2:
        render_newgoals(user)


    with tab3:
        st.subheader("🗓️ Schedule Your Plan")
        if plan and plan.goals:
            first_goal = next(iter(plan.goals.values()))
            st.session_state.edit_selected_goal = first_goal.title
        else:
            st.session_state.edit_selected_goal = None
        st.session_state.current_plan = plan
        render_calendar(user)

    with tab4:
        render_checkin(user)

    with tab5:
        render_maingoal(user)

    with tab6:
        render_graphs(user)