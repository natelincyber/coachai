import streamlit as st

from std_components.calendar_display import render_calendar
from std_components.goals_display import render_goals
from std_components.checkin import render_checkin
from std_components.main_goal import render_maingoal
from std_components.graphs import render_graphs

def render_client(user):
    st.title("🧘 Your Coaching Plan")

    if user.currentPlan:

        plan = user.currentPlan

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏁 Coach Goals", "📅 Calendar", "✅ Today's Goals", "🎯 Main Goal Progress", "🧭 My Journey"])

        with tab1:
            st.subheader("🎯 Goals for this Session")

            # Load goals from user's current plan
            goals_data = plan.goals

            if not goals_data:
                st.info("Your coach hasn't set any goals yet.")
            else:
                render_goals(user, user)

        with tab2:
            st.subheader("🗓️ Schedule Your Plan")
            first_goal = next(iter(plan.goals.values()))
            st.session_state.edit_selected_goal = first_goal.title
            st.session_state.current_plan = plan
            render_calendar(user)

        with tab3:
            render_checkin(user)

        with tab4:
            render_maingoal(user)
        with tab5:
            render_graphs(user)

    else:
        st.warning("⚠️ Your coach hasn't uploaded a plan for you yet.")