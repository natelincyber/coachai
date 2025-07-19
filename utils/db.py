import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
from utils.models import CheckinSummary, Goal, User
from typing import Dict, List
from google.cloud.firestore_v1.base_query import FieldFilter
import streamlit as st

# Private global variable for Firestore client
_db = None

def _init_firebase():
    global _db
    if not firebase_admin._apps:
        # try:
        #     cred = credentials.Certificate("secrets/firebase_secret.json")
        # except:
        cred = dict(st.secrets["firebase"]['fb_secret'])
        firebase_admin.initialize_app(cred)
    
    if _db is None:
        _db = firestore.client()
    
    return _db

_init_firebase()

# -------------------- Firestore Access Functions -------------------- #

def get_user(user_info: dict) -> User:
    doc_ref = _db.collection("users").document(user_info["email"])
    doc = doc_ref.get()

    if doc.exists:
        return User(**doc.to_dict())

def create_user(user_info: dict) -> User:
    doc_ref = _db.collection("users").document(user_info["email"])
    doc = doc_ref.get()
    if not doc.exists:
        doc_ref.set({
            "email": user_info["email"],
            "name": user_info["name"],
            "role": user_info["role"],  # default to client
            "created_at": datetime.now(timezone.utc).isoformat(),
            "active": True,
            "currentPlan": None,
            "previousPlans": []
        })
        doc = doc_ref.get()
    return User(**doc.to_dict())

def get_latest_plan(user_email):
    plans = _db.collection("users").document(user_email).collection("plans")\
        .order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1).stream()
    for p in plans:
        return p.to_dict()
    return None

def get_all_clients():
    users_ref = _db.collection("users")
    query = users_ref.where(filter=FieldFilter("role", "==", "client")).stream()
    return [doc.to_dict() for doc in query]

def new_user_goals(user_email: str, new_plan: dict):
    user_ref = _db.collection("users").document(user_email)
    user_doc = user_ref.get()
    
    if user_doc.exists:
        user_data = user_doc.to_dict()
        previous = user_data.get("currentPlan")
        
        updates = {
            "currentPlan": new_plan,
        }

        if previous:
            firestore.ArrayUnion
            updates["previousPlans"] = firestore.ArrayUnion([previous])

        user_ref.update(updates)

def update_user_goals(client_email: str, goals: Dict[str,Goal]) -> None:
    user_ref = _db.collection("users").document(client_email)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        current_plan = user_data.get("currentPlan")
        
        current_plan["goals"] = goals["goals"]

        
        user_ref.update({
            "currentPlan": current_plan
        })

def save_user_events(user_email: str, events: List[Dict]):
    """
    Save user's events to Firestore under the user document.
    """
    user_ref = _db.collection("users").document(user_email)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        current_plan = user_data.get("currentPlan")

        current_plan["events"] = events


        user_ref.update({
            "currentPlan": current_plan
        })


def add_main_goal(user_email: str, new_goal: Goal) -> None:
    """
    Add a new Goal object to the user's main_goals dict in Firestore.
    """
    user_ref = _db.collection("users").document(user_email)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        main_goals = user_data.get("main_goals", {})

        # Avoid overwrite if key exists
        if new_goal.id not in main_goals:
            main_goals[new_goal.id] = new_goal.model_dump()
            user_ref.update({"main_goals": main_goals})

def edit_main_goal(user_email: str, updated_goal: Goal) -> None:
    """
    Update an existing main goal by matching goal id in Firestore dict.
    """
    user_ref = _db.collection("users").document(user_email)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        main_goals = user_data.get("main_goals", {})

        if updated_goal.id in main_goals:
            main_goals[updated_goal.id] = updated_goal.model_dump()
            user_ref.update({"main_goals": main_goals})

def delete_main_goal(user_email: str, goal_id: str) -> None:
    """
    Remove a main goal by goal id from user's main_goals dict in Firestore.
    """
    user_ref = _db.collection("users").document(user_email)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        main_goals = user_data.get("main_goals", {})

        if goal_id in main_goals:
            del main_goals[goal_id]
            user_ref.update({"main_goals": main_goals})

def save_checkin(user_email: str, checkin_data: CheckinSummary) -> None:
    """
    Append a new check-in to the user's checkins list.
    """
    user_ref = _db.collection("users").document(user_email)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        checkins = user_data.get("checkins", [])

        checkins.append(checkin_data.model_dump())  # serialize to dict
        user_ref.update({"checkins": checkins})


def update_goal_context(user_email: str, goal_id: str, goal_type: str, new_summary: str) -> None:
    """
    Update LLM summary context for a main or coach goal.
    """
    user_ref = _db.collection("users").document(user_email)
    user_doc = user_ref.get()

    if user_doc.exists:
        field_name = "main_goal_context" if goal_type == "main" else "coach_goal_context"
        user_data = user_doc.to_dict()
        context = user_data.get(field_name, {})

        context[goal_id] = new_summary
        user_ref.update({field_name: context})

def get_llm_context(user_email: str) -> str:
    """
    Create prompt-ready context for the LLM based on user's goal summaries.
    """
    user_ref = _db.collection("users").document(user_email)
    user_doc = user_ref.get()
    lines = []

    if user_doc.exists:
        user_data = user_doc.to_dict()
        
        main_goals = user_data.get("main_goals", {})
        main_context = user_data.get("main_goal_context", {})

        if main_goals and main_context:
            lines.append("MAIN GOALS AND PROGRESS:")
            for gid, goal in main_goals.items():
                title = goal.get("title", "Untitled Goal")
                summary = main_context.get(gid, "No summary available.")
                lines.append(f"- {title}: {summary}")

        coach_goals = user_data.get("currentPlan", {}).get("goals", {})
        coach_context = user_data.get("coach_goal_context", {})

        if coach_goals and coach_context:
            lines.append("\nCOACH GOALS AND PROGRESS:")
            for gid, goal in coach_goals.items():
                title = goal.get("title", "Untitled Goal")
                summary = coach_context.get(gid, "No summary available.")
                lines.append(f"- {title}: {summary}")

    return "\n".join(lines) if lines else "No goal progress available yet."


def get_recent_checkins(user_email: str, limit: int = 5) -> List[Dict]:
    user_ref = _db.collection("users").document(user_email)
    user_doc = user_ref.get()

    if user_doc.exists:
        checkins = user_doc.to_dict().get("checkins", [])
        return sorted(checkins, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
    return []


def add_checkin_context_entry(user_email: str, goal_id: str, goal_type: str, user_msg: str, coach_msg: str) -> None:
    """
    Appends a check-in summary string (user + coach exchange) to the correct context store in Firestore.
    """
    user_ref = _db.collection("users").document(user_email)
    user_doc = user_ref.get()
    if not user_doc.exists:
        return

    data = user_doc.to_dict()

    # Choose correct context key
    context_key = "coach_goal_context" if goal_type == "coach" else "main_goal_context"

    existing_context = data.get(context_key, {}).get(goal_id, "")

    # Format the new exchange as text
    new_entry = f"User: {user_msg}\nCoach: {coach_msg}"

    # Combine with existing string context
    updated_context = f"{existing_context}\n\n{new_entry}" if existing_context else new_entry

    # Prepare update
    user_ref.update({
        f"{context_key}.{goal_id}": updated_context
    })

def update_user_role(user_email: str, new_role: str) -> User:
    """
    Update the user's role and mark them as not a first-time user.

    Args:
        user_email (str): The user's email (Firestore document ID).
        new_role (str): The new role to assign, e.g., 'coach' or 'client'.

    Returns:
        User: The updated User model instance.
    """
    user_ref = _db.collection("users").document(user_email)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_ref.update({
            "role": new_role,
            "first_time_user": False
        })
        updated_doc = user_ref.get()
        return User(**updated_doc.to_dict())
    else:
        raise ValueError(f"User with email {user_email} not found.")
