from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Literal
import hashlib

class Goal(BaseModel):
    id: str | None = None
    title: str
    task: str
    importance: Literal["high", "medium", "low", "mainGoal"]

    @model_validator(mode="before")
    @classmethod
    def generate_id(cls, values: dict) -> dict:
        if "id" not in values or values["id"] is None:
            hash_input = f'{values.get("title")}|{values.get("task")}|{values.get("importance")}'
            values["id"] = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
        return values
    

class GoalLite(BaseModel):
    """
    Simpler version of Goal used for Gemini agent output.
    """
    title: str
    task: str
    importance: Literal["high", "medium", "low", "mainGoal"]

class Event(BaseModel):
    id: str
    title: str
    start: str
    end: str
    backgroundColor: str = Field(default=None)
    borderColor: str = "#000"
    textColor: str = "#fff"
    extendedProps: Dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def set_derived_fields(cls, values: Dict) -> Dict:
        importance = values.get("extendedProps", "").get("importance", "")
        values["backgroundColor"] = (
            "#0d6efd" if importance == "high"
            else "#198754" if importance == "medium"
            else "#6c757d"
        )
        return values

    @classmethod
    def from_goal(cls, goal, start: str, end: str):
        return cls(
            id=goal.id,
            title=goal.title,
            start=start,
            end=end,
        )
    

class Plan(BaseModel):
    goals: Dict[str, Goal] = {}
    events: List[Event] = []

class GoalsLiteOnly(BaseModel):
    goals: list[GoalLite]

class GoalsOnly(BaseModel):
    goals: Dict[str, Goal]


class CheckinSummary(BaseModel):
    goal_id: str
    goal_type: str  # "main" or "coach"
    raw_text: str
    summary: Optional[str]
    timestamp: str

class User(BaseModel):
    email: str
    name: str
    role: Optional[str] = None  # Role might be None initially
    first_time_user: bool = True  # New flag to track onboarding status
    created_at: str
    active: bool

    # Plan and goal-related
    currentPlan: Plan = Plan()
    previousPlans: List[Plan] = []
    main_goals: Optional[Dict[str, Goal]] = None

    # New additions for LLM chat context
    main_goal_context: Optional[Dict[str, str]] = None  # goal_id → summary
    coach_goal_context: Optional[Dict[str, str]] = None  # goal_id → summary
    checkins: Optional[List[CheckinSummary]] = None  # raw + summary check-in data
