from typing import List
import streamlit as st
import plotly.graph_objects as go
import streamlit_vis_network

from utils.models import Goal, User
from utils.semantics import assign_parent_id


def render_graphs(user : User):
    st.set_page_config(layout="wide")
    tab1, tab2, tab3 = st.tabs(["🔁 Sankey Diagram", "📊 Radial Progress", "📚 Knowledge Graph"])

    # Extract all goals
    sub_goals : List[Goal] = list(user.currentPlan.goals.values())
    main_goals : List[Goal] = list(user.main_goals.values())

    sub_goals = assign_parent_id(sub_goals, main_goals)
    

    # Map goal ids to labels and positions
    id_to_index = {}
    labels = []
    colors = []

    # Main goals go to the right in Sankey
    for i, goal in enumerate(sub_goals + main_goals):
        id_to_index[goal.id] = i
        labels.append(goal.title)
        colors.append("#4285f4" if goal.importance != "mainGoal" else "#db4437")

    # ------------------- TAB 1: SANKEY ----------------------
    with tab1:
        st.subheader("Coach Goal Contributions")
        col1, col2, col3 = st.columns([1, 6, 1])

        with col2:
            # Build links: sub-goal ➜ main-goal
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

            fig.update_layout(title_text="Coach Goals ➜ Main Goals", font_size=14)
            st.plotly_chart(fig, use_container_width=True)

    # ------------------- TAB 2: RADIAL ----------------------
    with tab2:
        st.subheader("🎯 Goal Completion Progress")
        col1, col2, col3 = st.columns([1, 6, 1])

        with col2:
            goal_names = [g.title for g in sub_goals + main_goals]
            # TODO add progress completion
            completion = [60 for _ in sub_goals + main_goals] 

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

    # ------------------- TAB 3: KNOWLEDGE GRAPH ----------------------
    with tab3:
        st.subheader("📚 Goal Relationships")
        col1, col2, col3 = st.columns([1, 6, 1])

        with col2:
            # Create nodes
            nodes = [
                {
                    "id": g.id,
                    "label": g.title,
                    "size": 40 if g.importance == "mainGoal" else 20,
                    "color": "#db4437" if g.importance == "mainGoal" else "#4285f4"
                }
                for g in sub_goals + main_goals
            ]

            # Create edges
            edges = [
                {"from": g.id, "to": g.parent_id, "label": "supports"}
                for g in sub_goals if g.parent_id
            ]



            options = {
                "nodes": {
                    "shape": "dot",
                    "scaling": {"min": 10, "max": 50},
                },
                "edges": {
                    "arrows": {"to": {"enabled": True}},
                    "font": {"align": "middle"},
                },
                "physics": {
                    "enabled": True,
                    "stabilization": {"iterations": 1000},
                },
                "interaction": {
                    "zoomView": False,
                    "dragNodes": True,
                    "dragView": True,
                    "hover": True,
                },
                "height": "600px",
            }

            selection = streamlit_vis_network.streamlit_vis_network(
                nodes=nodes,
                edges=edges,
                options=options
            )

            if selection:
                selected_nodes, selected_edges, positions = selection
                if selected_nodes:
                    st.write("Selected node:", selected_nodes)
                elif selected_edges:
                    st.write("Selected edge:", selected_edges)
