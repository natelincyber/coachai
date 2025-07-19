import streamlit as st

from custom_calendar import calendar
from utils.constants import CALENDAR_OPTIONS, TIME_INTERVAL
from utils.db import get_user, save_user_events

from datetime import datetime, timedelta, time, timezone
def parse_utc_time(utc_str):
    try:
        return datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    except:
        return datetime.now()

def format_12h(dt: datetime):
    return dt.strftime("%I:%M %p").lstrip("0")

def to_local(dt: datetime) -> datetime:
    return dt.astimezone(st.session_state.client_tz)

def to_utc(dt: datetime) -> datetime:
    return dt.astimezone(datetime.timezone.utc)

     

def render_calendar(client):
    form_placeholder = st.empty()
    plan = st.session_state.current_plan
    goals = plan.goals
    if "calendar_events" not in st.session_state or not st.session_state.calendar_events:
        st.session_state.calendar_events = [e.model_dump() for e in plan.events]


    calendar_return = calendar(
        events=st.session_state.calendar_events,
        options=CALENDAR_OPTIONS,
        key=f"goal_calendar_{st.session_state['calendar_update_counter']}"
    )

    goal_list = list(goals.values())  # Convert to list once for reuse
    goal_titles = [g.title for g in goal_list]

    if calendar_return:
        cb_type = calendar_return.get("callback")

        if cb_type in ["select", "dateClick"]:
            if cb_type == "select":
                start = calendar_return["select"]["start"]
                end = calendar_return["select"]["end"]

                start_dt = datetime.fromisoformat(start).replace(tzinfo=timezone.utc).astimezone(st.session_state.client_tz)
                end_dt = datetime.fromisoformat(end).replace(tzinfo=timezone.utc).astimezone(st.session_state.client_tz)

            elif cb_type == "dateClick":
                start_dt = datetime.fromisoformat(calendar_return["dateClick"]["date"]).replace(tzinfo=timezone.utc).astimezone(st.session_state.client_tz)
                end_dt = start_dt + timedelta(minutes=TIME_INTERVAL)

                # assign start/end in ISO format for consistent use below
                start = start_dt.isoformat()
                end = end_dt.isoformat()

            with form_placeholder.form("schedule_goal_form", clear_on_submit=True):
                # Use the timezone-aware start_dt and end_dt (already assigned above)
                st.markdown(f"**Schedule goal from:** `{start_dt.strftime('%A, %B %d, %Y — %I:%M %p')}` → `{end_dt.strftime('%I:%M %p')}`")
                selected_title = st.selectbox("Choose goal to schedule", goal_titles)
                submit = st.form_submit_button("Add to Calendar")

            if submit:
                goal = next((g for g in goal_list if g.title == selected_title), None)
                if goal:
                    start_utc = start_dt.astimezone(timezone.utc)
                    end_utc = end_dt.astimezone(timezone.utc)

                    # Check if an event with the same id already exists
                    existing_event = next((e for e in st.session_state.calendar_events if e["id"] == goal.id), None)
                    if existing_event:
                        st.warning(f"Event for '{goal.title}' is already scheduled. Please edit or delete the existing event instead.")
                    else:
                        event = {
                            "id": goal.id,
                            "title": goal.title,
                            "start": start_utc.isoformat(),
                            "end": end_utc.isoformat(),
                            "backgroundColor": (
                                "#0d6efd" if goal.importance == "high"
                                else "#198754" if goal.importance == "medium"
                                else "#6c757d"
                            ),
                            "borderColor": "#000",
                            "textColor": "#fff",
                            "extendedProps": {"importance": goal.importance}
                        }

                        st.session_state.calendar_events.append(event)
                        st.session_state["calendar_update_counter"] += 1
                        save_user_events(client.email, st.session_state.calendar_events)
                        st.session_state.current_user = get_user({
                            "email": st.user.email,
                            "name": st.user.name,
                            "role": 'client'
                        })
                        st.rerun()

        elif cb_type == "eventClick":
            if "hide_event_editor" not in st.session_state or not st.session_state.hide_event_editor:
                event = calendar_return["eventClick"]["event"]
                goal = next((g for g in goal_list if g.id == event["id"]), None)

                if "editing_event" not in st.session_state:
                    st.session_state.editing_event = {
                        "id": event["id"],
                        "title": event["title"],
                        "start": event["start"],
                        "end": event["end"],
                        "selected_goal": goal.title if goal else goal_titles[0] if goal_titles else None
                    }

                with form_placeholder.container():
                    st.subheader(f"✏️ Edit Scheduled Goal")
                    
                    new_selection = st.selectbox(
                        "Change goal",
                        goal_titles,
                        index=goal_titles.index(st.session_state.editing_event["selected_goal"])
                        if st.session_state.editing_event["selected_goal"] in goal_titles
                        else 0,
                        key="event_goal_select"
                    )

                    if new_selection != st.session_state.editing_event["selected_goal"]:
                        st.session_state.editing_event["selected_goal"] = new_selection
                        st.rerun()

                    selected_goal = next((g for g in goal_list if g.title == st.session_state.editing_event["selected_goal"]), None)
                    if selected_goal:
                        st.markdown(f"**Description:** {selected_goal.task}")
                    else:
                        st.warning("No goal selected")

                    # Time inputs
                    col1, col2 = st.columns(2)

                    for label, time_key, container in [("Start", "start", col1), ("End", "end", col2)]:
                        with container:
                            dt = parse_utc_time(st.session_state.editing_event[time_key])
                            st.subheader(f"{label} Time")
                            tcol1, tcol2, tcol3 = st.columns([2,2,1])

                            with tcol1:
                                hour = st.selectbox("Hour", list(range(1,13)), index=(dt.hour % 12 or 12) - 1, key=f"{time_key}_hour")
                            with tcol2:
                                minute = st.selectbox("Minute", [f"{m:02d}" for m in range(0,60)], index=dt.minute, key=f"{time_key}_minute")
                            with tcol3:
                                ampm = st.selectbox("AM/PM", ["AM","PM"], index=0 if dt.hour < 12 else 1, key=f"{time_key}_ampm")

                            hour_24 = hour % 12 + (12 if ampm == "PM" else 0)
                            new_dt = datetime.combine(dt.date(), time(hour_24, int(minute)))
                            st.session_state.editing_event[time_key] = new_dt.isoformat()
                            st.caption(f"Selected: {format_12h(new_dt)}")

                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("💾 Update"):
                            if selected_goal:
                                updated_event = {
                                    "id": selected_goal.id,
                                    "title": selected_goal.title,
                                    "start": st.session_state.editing_event["start"],
                                    "end": st.session_state.editing_event["end"],
                                    "backgroundColor": (
                                        "#0d6efd" if selected_goal.importance == "high"
                                        else "#198754" if selected_goal.importance == "medium"
                                        else "#6c757d"
                                    ),
                                    "borderColor": "#000",
                                    "textColor": "#fff",
                                    "extendedProps": {"importance": selected_goal.importance}
                                }
                                st.session_state.calendar_events[:] = [e for e in st.session_state.calendar_events if e["id"] != event["id"]] + [updated_event]
                                st.session_state["calendar_update_counter"] += 1
                                st.session_state.hide_event_editor = True
                                del st.session_state.editing_event
                                save_user_events(client.email, st.session_state.calendar_events)
                                st.session_state.current_user = get_user({
                                    "email": st.user.email,
                                    "name": st.user.name,
                                    "role": 'client' # only used to validate coaches, null falls back to client
                                })
                                st.rerun()
                    with col2:
                        if st.button("🗑 Delete"):
                            st.session_state.calendar_events[:] = [e for e in st.session_state.calendar_events if e["id"] != event["id"]]
                            st.session_state["calendar_update_counter"] += 1
                            st.session_state.hide_event_editor = True
                            del st.session_state.editing_event
                            save_user_events(client.email, st.session_state.calendar_events)
                            st.session_state.current_user = get_user({
                                "email": st.user.email,
                                "name": st.user.name,
                                "role": 'client' # only used to validate coaches, null falls back to client
                            })
                            st.rerun()
                    with col3:
                        if st.button("✖️ Cancel"):
                            st.session_state.hide_event_editor = True
                            del st.session_state.editing_event
                            st.rerun()
            else:
                del st.session_state.hide_event_editor
