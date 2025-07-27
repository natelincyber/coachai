import streamlit as st
from utils.models import Goal
from utils.db import add_main_goal, edit_main_goal, delete_main_goal, get_llm_context
from utils.llm import llm_async

def render_maingoal(user):
    st.subheader("🎯 Main Goals")

    # Ensure main_goals dict exists
    if user.main_goals is None:
        user.main_goals = {}

    main_goals = user.main_goals

    if main_goals:
        for goal_id, goal in main_goals.items():
            with st.expander(f"Main Goal: {goal.title}", expanded=False):
                edited_title = st.text_input("Title", value=goal.title, key=f"title_{goal_id}")
                edited_task = st.text_area("Task Description", value=goal.task, key=f"task_{goal_id}")

                col1, col2, col3 = st.columns([1, 1, 1])

                with col1:
                    if st.button("Save Changes", key=f"save_{goal_id}"):
                        if edited_title != goal.title or edited_task != goal.task:
                            updated_goal = Goal(
                                id=goal.id,
                                title=edited_title,
                                task=edited_task,
                                importance="mainGoal"
                            )
                            edit_main_goal(user.email, updated_goal)
                            user.main_goals[goal_id] = updated_goal
                            st.success("Main goal updated.")
                            st.rerun()

                with col2:
                    if st.button("Delete Goal", key=f"delete_{goal_id}"):
                        delete_main_goal(user.email, goal.id)
                        del user.main_goals[goal_id]
                        st.success("Main goal deleted.")
                        st.rerun()

                with col3:
                    chat_key = f"chat_main_{goal_id}"
                    show_key = f"show_chat_main_{goal_id}"

                    if st.button("💬 Chat", key=chat_key):
                        st.session_state[show_key] = True

                if st.session_state.get(show_key, False):
                    with st.expander(f"💬 Chat about your Main Goal: '{goal.title}'", expanded=True):
                        history_key = f"chat_history_main_{goal_id}"
                        input_key = f"input_main_{goal_id}"
                        send_key = f"send_main_{goal_id}"
                        init_key = f"init_chat_main_{goal_id}"

                        if history_key not in st.session_state:
                            st.session_state[history_key] = []

                        if not st.session_state.get(init_key):
                            full_context = get_llm_context(user.email)

                            system_prompt = f"""
                            You are the AI coach guiding a client on their long-term main goal.

                            Current Main Goal:
                            {goal.title} — {goal.task}

                            Context from all other goals and check-ins:
                            {full_context}

                            Ask 2-3 focused reflective questions to help the client assess and deepen their progress toward this main goal.
                            Be concise, motivational, and specific.
                            """

                            with st.spinner("Coach is preparing your reflection questions..."):
                                response = llm_async(system_prompt, None)
                                question_text = str(response).strip() if not hasattr(response, 'output') else response.output.strip()
                            st.session_state[history_key].append(("Coach", question_text))
                            st.session_state[init_key] = True

                        for sender, message in st.session_state[history_key]:
                            st.markdown(f"**{sender}:** {message}")

                        chat_input = st.text_area("✍️ Your response:", key=input_key)
                        pending_key = f"pending_send_main_{goal_id}"

                        if st.button("Send", key=send_key) and chat_input:
                            st.session_state[pending_key] = chat_input

                        if pending_key in st.session_state:
                            pending_msg = st.session_state[pending_key]
                            del st.session_state[pending_key]

                            st.session_state[history_key].append(("You", pending_msg))

                            full_context = get_llm_context(user)

                            feedback_prompt = f"""
                            The client is working on their main goal:
                            {goal.title} — {goal.task}

                            Context from other goals:
                            {full_context}

                            Their response was:
                            "{pending_msg}"

                            Provide 1 thoughtful encouragement and 1 practical next step they could take, grounded in their broader goal progress.
                            """

                            with st.spinner("Coach is thinking..."):
                                reply = llm_async(feedback_prompt, None)
                                reply_text = str(reply).strip() if not hasattr(reply, 'output') else reply.output.strip()
                                st.session_state[history_key].append(("Coach", reply_text))

                            from utils.db import add_checkin_context_entry
                            add_checkin_context_entry(
                                user_email=user.email,
                                goal_id=goal.id,
                                goal_type="main",
                                user_msg=pending_msg,
                                coach_msg=reply_text
                            )

                            st.rerun()
    else:
        st.info("No main goal has been set yet.")

    st.divider()

    st.subheader("➕ Add a New Main Goal")

    with st.form("main_goal_form"):
        new_title = st.text_input("Main Goal Title")
        new_task = st.text_area("Describe the main goal task")
        submitted = st.form_submit_button("Add Main Goal")

        if submitted:
            if new_title and new_task:
                new_goal = Goal(
                    title=new_title,
                    task=new_task,
                    importance="mainGoal"
                )
                add_main_goal(user.email, new_goal)

                if user.main_goals is None:
                    user.main_goals = {}
                user.main_goals[new_goal.id] = new_goal

                st.success("Main goal added successfully.")
                st.rerun()
            else:
                st.error("Please fill in both the title and task.")
