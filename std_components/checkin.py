import datetime
import streamlit as st


from utils.db import add_checkin_context_entry, get_llm_context
from utils.llm import llm_async



def render_checkin(client):
    st.subheader("✅ Today's Goals")

    plan = st.session_state.current_plan
    today = datetime.datetime.now().date()
    events = plan.events or []

    todays_goals = []
    for event in events:
        try:
            event_start = datetime.datetime.fromisoformat(event.start)
            event_end = datetime.datetime.fromisoformat(event.end)
        except ValueError:
            continue

        if event_start.date() == today:
            goal = plan.goals.get(event.id)
            if goal:
                todays_goals.append({
                    "id": goal.id,
                    "title": goal.title,
                    "task": goal.task,
                    "importance": goal.importance,
                    "start": event_start.strftime("%I:%M %p"),
                    "end": event_end.strftime("%I:%M %p")
                })

    if not todays_goals:
        st.info("You have no scheduled goals for today.")
    else:
        importance_colors = {
            "high": "#FF6B6B",
            "medium": "#FFA94D",
            "low": "#69DB7C"
        }

        for goal in sorted(todays_goals, key=lambda g: g["start"]):
            color = importance_colors[goal["importance"]]
            chat_key = f"chat_{goal['id']}"
            show_key = f"show_chat_{goal['id']}"

            # Create two columns: one for content, one for the embedded-looking button
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"""
                    <div style="border:1px solid #ccc; border-radius:8px; padding:12px; margin-bottom:10px;">
                        <h5 style="margin:0;">{goal["title"]}</h5>
                        <p style="margin:4px 0 8px 0;">{goal["task"]}</p>
                        <span style="color:white; background-color:{color}; padding:4px 10px; border-radius:20px;">
                            {goal["importance"].capitalize()} Importance
                        </span>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                # Align the button vertically with the card
                st.write("")  # spacer
                st.write("")
                st.write("")

                if st.button("💬 Chat", key=chat_key):
                    st.session_state[show_key] = True

        if st.session_state.get(show_key, False):
            with st.expander(f"💬 Chat with Coach about '{goal['title']}'", expanded=True):
                history_key = f"chat_history_{goal['id']}"
                input_key = f"input_{goal['id']}"
                send_key = f"send_{goal['id']}"
                init_key = f"init_chat_{goal['id']}"

                # Initialize chat history and system prompt
                if history_key not in st.session_state:
                    st.session_state[history_key] = []

                # On first open, run LLM to generate questions based on goal/task
                if not st.session_state.get(init_key):
                    day_plan = f"{goal['title']} — {goal['task']}"
                    full_context = get_llm_context(client.email)

                    goal_prompt = f"""
                    You are running a daily AI check-in with a client.

                    Client Goal: {goal['title']}
                    Today's Plan: {day_plan}

                    Context from the client’s ongoing goals and progress:
                    {full_context}

                    Ask 2–3 reflective questions based on today's goal *and* their broader progress.
                    Be specific, supportive, and concise.
                    """

                    with st.spinner("Coach is preparing your check-in questions..."):
                        response = llm_async(goal_prompt, None)
                        question_text = str(response).strip() if not hasattr(response, 'output') else response.output.strip()
                    st.session_state[history_key].append(("Coach", question_text))
                    st.session_state[init_key] = True

                # Display existing messages
                for sender, message in st.session_state[history_key]:
                    st.markdown(f"**{sender}:** {message}")

                # Get user input
                chat_input = st.text_area("✍️ Your response:", key=input_key)
                pending_key = f"pending_send_{goal['id']}"

                # Button sets a flag to send on next rerun
                if st.button("Send", key=send_key) and chat_input:
                    st.session_state[pending_key] = chat_input

                # Process pending message
                if pending_key in st.session_state:
                    pending_msg = st.session_state[pending_key]

                    # Prevent reprocessing on rerun
                    del st.session_state[pending_key]

                    # Add user response
                    st.session_state[history_key].append(("You", pending_msg))

                    full_context = get_llm_context(client.email)

                    # Generate LLM feedback
                    feedback_prompt = f"""
                    The client is working on the goal: {goal['title']}
                    Task: {goal['task']}

                    Context from the client’s goal history:
                    {full_context}

                    They answered their check-in with:
                    "{pending_msg}"

                    Reflect supportively. Give 1 encouragement based on their effort and 1 actionable suggestion based on their broader progress.
                    """

                    with st.spinner("Coach is thinking..."):
                        reply = llm_async(feedback_prompt, None)
                        reply_text = str(reply).strip() if not hasattr(reply, 'output') else reply.output.strip()
                        st.session_state[history_key].append(("Coach", reply_text))
                        add_checkin_context_entry(
                            user_email=client.email,
                            goal_id=goal["id"],
                            goal_type="coach",  # or "main" if needed
                            user_msg=pending_msg,
                            coach_msg=reply_text,
                        )

                    # Force rerun to show the updated response
                    st.rerun()