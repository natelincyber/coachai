import streamlit as st

from std_components.goals_display import render_goals
from utils.db import get_user, new_user_goals, update_user_goals
from utils.llm import llm_async
from utils.models import Goal, GoalsLiteOnly, Plan, User
from utils.utils import convert_goals, load_file

def render_newgoals(user: User):

    st.subheader("📄 Plan Goals")

    selected_client = user.email
    num_days = st.number_input("How many days should the plan last?", min_value=1, max_value=30, value=14, step=1)
    summary = st.text_area("Paste session summary:", value=load_file("sample_transcript.txt"))

    if st.button("Generate 2-Week Plan"):
        with st.spinner("Generating..."):
            prompt = f"""
            You are a personal AI assistant helping a coach design a {num_days}-day improvement plan for a client.

            Based on the following coaching session summary, identify 5 distinct goals the client should work on, and label each with an importance level: 
            - 1 high importance goal
            - 2 medium importance goals
            - 2 low importance goals

            Each goal should include a short, clear title and an actionable task (reflection, exercise, behavior, etc.).


            SESSION SUMMARY:
            {summary}
            """
            goals = convert_goals(llm_async(prompt, GoalsLiteOnly).output)


            plan = Plan()
            plan.goals = goals
            
            new_user_goals(
                selected_client,
                {
                    **plan.model_dump()
                }
            )

            st.success(f"✅ Plan created and saved for {selected_client}")

            st.subheader("📅 Generated 2-Week Plan")

    st.divider()
    with st.expander("➕ Create New Goal"):
        with st.form(key="new_goal_form", clear_on_submit=True):
            new_title = st.text_input("Title")
            new_task = st.text_area("Task / Description")
            new_importance = st.selectbox("Importance", options=["high", "medium", "low"])

            col1, col2 = st.columns([1, 1])
            submit = col1.form_submit_button("Update Goal ✅")
            cancel = col2.form_submit_button("Cancel ❌")

            if submit:
                if not new_title or not new_task:
                    st.warning("Title and task cannot be empty.")
                else:

                    new_goal = Goal(title=new_title, task=new_task, importance=new_importance)
                    full_client = get_user({"email": selected_client, "name": st.user.name, "role": "client"})

                    if not full_client.currentPlan:
                        st.error("User has no existing plan. Generate a plan first.")
                    else:
                        update_user_goals(selected_client, new_goal)
                        st.success(f"Goal '{new_title}' added.")
                        st.rerun()

            elif cancel:
                st.info("Goal creation cancelled.")

    client = get_user({"email": selected_client, "name": st.user.name, "role": "client"})
    if client.currentPlan:
        render_goals(client, user, edit=True)
    else:
        st.info(f"No plan uploaded yet for {selected_client}.")