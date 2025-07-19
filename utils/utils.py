import os
import asyncio
from utils.models import GoalsLiteOnly, GoalsOnly, Goal


def load_file(filename: str) -> str:
    transcript_path = os.path.join("samples", filename)

    if not os.path.exists(transcript_path):
        raise FileNotFoundError(f"No such file: '{transcript_path}'")

    with open(transcript_path, "r", encoding="utf-8") as file:
        return file.read()

def convert_goals(goals_lite: GoalsLiteOnly) -> GoalsOnly:
    """
    Converts a list of GoalLite objects to a dict of full Goal objects keyed by id.
    """
    goal_dict = {}
    for g in goals_lite.goals:
        full_goal = Goal(**g.model_dump())  # triggers the ID generator
        goal_dict[full_goal.id] = full_goal
    return goal_dict


def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    return loop.run_until_complete(coro)