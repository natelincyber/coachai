from typing import List
import streamlit as st
import plotly.graph_objects as go
import streamlit_vis_network

from utils.db import update_user_goals
from utils.models import Goal, User
from utils.semantics import assign_parent_id

# Get current theme info
theme = st.get_option("theme.base")
is_dark = theme == "dark"
text_color = "black" if is_dark else "white"
bg_color = "rgba(0,0,0,0)"  # Transparent to match parent background

def render_graphs(user: User):
    st.set_page_config(layout="wide")

    # Track updates
    if "goals_updated" not in st.session_state:
        st.session_state["goals_updated"] = False

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔁 Sankey Diagram",
        "📊 Radial Progress",
        "📚 Knowledge Graph",
        "⚙️ Edit Goals"
    ])

    # Extract and assign goals
    sub_goals: List[Goal] = list(user.currentPlan.goals.values())
    main_goals: List[Goal] = list(user.main_goals.values())
    sub_goals = assign_parent_id(user, sub_goals, main_goals)

    # Run each graph as a fragment
    with tab1:
        draw_sankey(sub_goals, main_goals)

    with tab2:
        draw_radial_progress(sub_goals, main_goals)

    with tab3:
        draw_knowledge_graph(sub_goals, main_goals)

    with tab4:
        edit_goals(user, sub_goals, main_goals)

# ------------------- GRAPH FRAGMENTS ----------------------

def draw_sankey(sub_goals, main_goals):
    st.subheader("Coach Goal Contributions")
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        all_goals = sub_goals + main_goals
        id_to_index = {g.id: i for i, g in enumerate(all_goals)}
        labels = [g.title for g in all_goals]
        colors = ["#4285f4" if g.importance != "mainGoal" else "#db4437" for g in all_goals]

        source, target, value, link_colors = [], [], [], []
        for g in sub_goals:
            if g.parent_id and g.parent_id in id_to_index:
                source.append(id_to_index[g.id])
                target.append(id_to_index[g.parent_id])
                value.append(1)
                link_colors.append("rgba(66,133,244,0.5)")

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color=colors
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color=link_colors
            )
        )])
        fig.update_layout(
            title_text="Coach Goals ➜ Main Goals",
            font=dict(color=text_color),
            paper_bgcolor=bg_color,
            plot_bgcolor=bg_color,
        )
        st.plotly_chart(fig, use_container_width=True)

def draw_radial_progress(sub_goals, main_goals):
    st.subheader("🎯 Goal Completion Progress")
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        goals = sub_goals + main_goals
        fig = go.Figure()
        for i, g in enumerate(goals):
            fig.add_trace(go.Barpolar(
                r=[g.progress],
                theta=[i * (360 / len(goals))],
                name=g.title,
                marker_color=g.progress,
                marker_line_color="white",
                marker_line_width=2,
                opacity=0.8
            ))

        fig.update_layout(
            paper_bgcolor=bg_color,
            plot_bgcolor=bg_color,
            template="plotly_white" if is_dark else "plotly_dark",
            height=800,
            width=800,
            polar=dict(
                radialaxis=dict(
                    range=[0, 100],
                    showticklabels=True,
                    tickfont=dict(color=text_color)
                ),
                angularaxis=dict(
                    direction="clockwise",
                    tickmode="array",
                    tickvals=[i * (360 / len(goals)) for i in range(len(goals))],
                    ticktext=[g.title for g in goals],
                    tickfont=dict(color=text_color)
                )
            ),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

def draw_knowledge_graph(sub_goals, main_goals):
    st.subheader("📚 Goal Relationships")
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        nodes = [
            {
                "id": g.id,
                "label": g.title,
                "size": 40 if g.importance == "mainGoal" else 20,
                "color": "#db4437" if g.importance == "mainGoal" else "#4285f4",
                "font": {"color": text_color}
            } for g in sub_goals + main_goals
        ]
        edges = [{"from": g.id, "to": g.parent_id, "label": None} for g in sub_goals if g.parent_id]

        options = {
            "nodes": {
                "shape": "dot",
                "scaling": {"min": 10, "max": 50},
                "font": {"color": text_color}
            },
            "edges": {
                "arrows": {"to": {"enabled": True}},
                "font": {"align": "middle", "color": text_color}
            },
            "physics": {"enabled": True, "stabilization": {"iterations": 1000}},
            "interaction": {"zoomView": False, "dragNodes": True, "dragView": True, "hover": True},
            "height": "600px",
        }

        selection = streamlit_vis_network.streamlit_vis_network(
            nodes=nodes,
            edges=edges,
            options=options
        )

        if selection:
            selected_nodes, selected_edges, _ = selection
            if selected_nodes:
                st.write("Selected node:", selected_nodes)
            elif selected_edges:
                st.write("Selected edge:", selected_edges)

def edit_goals(user: User, sub_goals: List[Goal], main_goals: List[Goal]):
    st.subheader("⚙️ Edit Goal Relationships & Progress")
    editable_goals = sub_goals + main_goals
    main_goal_options = [g for g in main_goals]

    for goal in editable_goals:
        with st.expander(f"✏️ {goal.title}"):
            col1, col2 = st.columns([3, 2])
            updated = False

            with col1:
                if goal.importance != "mainGoal":
                    current_title = next((mg.title for mg in main_goal_options if mg.id == goal.parent_id), "None")
                    new_parent = st.selectbox(
                        "Assign Parent Goal",
                        options=["None"] + [mg.title for mg in main_goal_options],
                        index=(["None"] + [mg.title for mg in main_goal_options]).index(current_title),
                        key=f"parent_select_{goal.id}"
                    )
                    new_parent_id = next((mg.id for mg in main_goal_options if mg.title == new_parent), None) if new_parent != "None" else None

                    if new_parent_id != goal.parent_id:
                        goal.parent_id = new_parent_id
                        updated = True

            with col2:
                new_progress = st.slider(
                    "Set Completion (%)",
                    min_value=0,
                    max_value=100,
                    value=goal.progress if hasattr(goal, "progress") else 0,
                    key=f"progress_slider_{goal.id}"
                )

                if new_progress != goal.progress:
                    goal.progress = new_progress
                    updated = True

            if updated:
                update_user_goals(user.email, goal)
                st.success("✅ Changes saved.")
                st.session_state["goals_updated"] = True
                st.rerun()
