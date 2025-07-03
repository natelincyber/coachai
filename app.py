import os
from dotenv import load_dotenv
import streamlit as st
from google import genai
from google.genai import types


load_dotenv()

# Set up model and config using your template
client = genai.Client()
model = "gemini-2.5-flash-preview-04-17"
config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=0)
)

# Initialize session state
if "plan" not in st.session_state:
    st.session_state.plan = None

# App layout
st.set_page_config(page_title="AI Coaching Plan", layout="wide")
st.title("AI Coaching Plan Generator & Daily Check-In")

# Step 1: Generate 2-Week Plan
st.header("Step 1: Paste Coaching Session Summary")
summary = st.text_area("Paste your coaching session summary below:")

if st.button("Generate 2-Week Plan"):
    with st.spinner("Generating plan with Gemini..."):
        plan_prompt = f"""
        You are a personal AI assistant. Based on this coaching session summary, generate a personalized 2-week improvement plan.
        Include specific tasks, exercises, or reflections for each day.

        SESSION SUMMARY:
        {summary}
        """
        response = client.models.generate_content(
            model=model,
            contents=plan_prompt,
            config=config,
        )
        st.session_state.plan = response.text
        st.success("✅ Plan generated!")

# Step 2: Display the plan
if st.session_state.plan:
    st.header("Your 2-Week Plan")
    st.markdown(st.session_state.plan)

    # Daily Check-in
    st.header("Step 2: Daily Check-In")
    day = st.number_input("Select a day (1-14)", min_value=1, max_value=14, step=1)

    daily_plans = st.session_state.plan.split("Day")
    if 0 < day < len(daily_plans):
        day_plan = "Day" + daily_plans[day]

        # Extract goal
        goal_prompt = f"""
        Read this daily plan and summarize the main topic or goal in a few words.

        Daily Plan:
        {day_plan}
        """
        goal_response = client.models.generate_content(
            model=model,
            contents=goal_prompt,
            config=config,
        )
        goal = goal_response.text.strip()

        # Generate specific check-in questions
        checkin_prompt = f"""
        You are running a daily AI check-in with a client.

        Today's goal is: {goal}
        Today's plan: {day_plan}

        Ask the client 2-3 specific reflective questions related to the goal.
        Questions should check how the client is applying what they've learned during their coaching session.
        Be direct, concise, and supportive.
        """
        checkin_response = client.models.generate_content(
            model=model,
            contents=checkin_prompt,
            config=config,
        )

        st.subheader(f"Today's Goal: {goal}")
        st.markdown("**Check-in Questions:**")
        st.markdown(checkin_response.text)

        user_reply = st.text_area("✍️ Your Response to the Check-In:")
        if st.button("Submit Check-In"):
            feedback_prompt = f"""
            A client is working on: {goal}
            Today's plan: {day_plan}

            They answered their check-in with:
            "{user_reply}"

            Give a supportive reflection and 1 suggestion for improvement or reinforcement.
            """
            feedback_response = client.models.generate_content(
                model=model,
                contents=feedback_prompt,
                config=config,
            )
            st.success("✅ Check-in complete!")
            st.markdown("**AI Feedback:**")
            st.markdown(feedback_response.text)
    else:
        st.error("❌ Invalid day number. Please select between 1-14.")
