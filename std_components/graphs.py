import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import plotly.graph_objects as go


def render_graphs(user):
    st.set_page_config(layout="wide")

    tab1, tab2 = st.tabs(["🔁 Sankey Diagram", "📊 Radial Progress"])

    # ------------------- TAB 1: FORCE-DIRECTED ----------------------


    # ------------------- TAB 2: SANKEY ----------------------
    with tab1:
        st.subheader("Sankey Diagram: Coach Goal Contributions")
        col1, col2, col3 = st.columns([1, 6, 1])

        with col2:
            labels = [
                "Practice STAR", "Mock Interviews", "Revise Resume",  # Coach Goals
                "Land a Job", "Career Pivot"                           # Main Goals
            ]

            source = [0, 1, 2, 2]  # From coach goals
            target = [3, 3, 3, 4]  # To main goals
            value = [3, 2, 2, 1]   # Contribution weights

            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=labels,
                    color=["#34a853", "#fbbc05", "#4285f4", "#3367d6", "#db4437"]
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                    color=["rgba(52,168,83,0.5)", "rgba(251,188,5,0.5)", "rgba(66,133,244,0.5)", "rgba(66,133,244,0.2)"]
                )
            )])

            fig.update_layout(title_text="Coach Goals ➜ Main Goals", font_size=14)
            st.plotly_chart(fig, use_container_width=True)

    # ------------------- TAB 3: RADIAL ----------------------
    with tab2:
        st.subheader("🎯 Goal Completion Progress")
        col1, col2, col3 = st.columns([1, 6, 1])

        with col2:
            goal_names = ["Practice STAR", "Mock Interviews", "Revise Resume", "Daily Meditation", "Portfolio Site"]
            completion = [80, 50, 90, 30, 70]

            fig = go.Figure()

            for i, (goal, percent) in enumerate(zip(goal_names, completion)):
                fig.add_trace(go.Barpolar(
                    r=[percent],
                    theta=[i * (360 / len(goal_names))],
                    name=goal,
                    marker_color=percent,
                    marker_line_color="white",
                    marker_line_width=2,
                    opacity=0.8
                ))

            fig.update_layout(
                title="Goal Completion (%)",
                template="plotly_dark",
                polar=dict(
                    radialaxis=dict(range=[0, 100], showticklabels=True, ticks=''),
                    angularaxis=dict(
                        direction="clockwise",
                        tickmode="array",
                        tickvals=[i * (360 / len(goal_names)) for i in range(len(goal_names))],
                        ticktext=goal_names
                    ),
                ),
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)
