import streamlit as st

from utils.models import User, Goal
from utils.db import update_user_goals

def render_goals(client: User, user: User):
    if not client.currentPlan or not client.currentPlan.goals:
        st.info("No current plan available.")
        return

    goals_data = client.currentPlan.goals  # This is now a dict: Dict[str, Goal]

    importance_colors = {
        "high": "#FF6B6B",
        "medium": "#FFA94D",
        "low": "#69DB7C"
    }

    goals_by_importance = {
        "high": [],
        "medium": [],
        "low": []
    }

    for goal in goals_data.values():
        goals_by_importance[goal.importance.lower()].append(goal)

    col_high, col_medium, col_low = st.columns(3)

    for label, col in zip(["high", "medium", "low"], [col_high, col_medium, col_low]):
        with col:
            st.markdown(f"#### {label.capitalize()} Importance")
            for idx, goal in enumerate(goals_by_importance[label]):
                title_key = f"title_{goal.id}_{idx}"
                task_key = f"task_{goal.id}_{idx}"
                importance_key = f"importance_{goal.id}_{idx}"
                save_key = f"save_{goal.id}_{idx}"

                st.markdown("---")

                if user.role == "coach":
                    new_title = st.text_input("Goal Title", value=goal.title, key=title_key)
                    new_task = st.text_area("Goal Task", value=goal.task, key=task_key)
                    new_importance = st.selectbox("Importance", options=["high", "medium", "low"],
                                                index=["high", "medium", "low"].index(goal.importance.lower()),
                                                key=importance_key)

                    col_save, col_delete = st.columns([1, 1])

                    with col_save:
                        if st.button("💾 Save", key=save_key):
                            updated_goal = Goal(
                                id=goal.id,
                                title=new_title,
                                task=new_task,
                                importance=new_importance
                            )
                            client.currentPlan.goals[goal.id] = updated_goal
                            update_user_goals(client.email, client.currentPlan.model_dump())
                            st.success("Goal updated.")
                            st.rerun()

                    with col_delete:
                        if st.button("🗑️ Delete", key=f"delete_{goal.id}_{idx}"):
                            del client.currentPlan.goals[goal.id]
                            update_user_goals(client.email, client.currentPlan.model_dump())
                            st.warning("Goal deleted.")
                            st.rerun()
                else:
                    color = importance_colors[label]
                    col.markdown(f"""
                        <div style="border:1px solid #ccc; border-radius:8px; padding:12px; margin-bottom:10px;">
                            <h5 style="margin:0;">{goal.title}</h5>
                            <p style="margin:4px 0 8px 0;">{goal.task}</p>
                            <span style="color:white; background-color:{color}; padding:4px 10px; border-radius:20px;">
                                {label.capitalize()} Importance
                            </span>
                        </div>
                    """, unsafe_allow_html=True)
