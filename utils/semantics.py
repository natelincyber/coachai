from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

from utils.models import Goal




# Load a dot-product-optimized model
model = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-dot-v1', local_files_only=True)

def embed_main_goal(goal: Goal):
    return model.encode(goal.title, normalize_embeddings=False)

def embed_sub_goal(goal: Goal):
    return model.encode(f"{goal.task}", normalize_embeddings=False)

def assign_parent_id(sub_goals: List[Goal], main_goals: List[Goal]) -> List[Goal]:
    if not sub_goals or not main_goals:
        return sub_goals

    # Only consider sub-goals without parent_id
    sub_goals_needing_parent = [g for g in sub_goals if not g.parent_id]

    if not sub_goals_needing_parent:
        return sub_goals  # Nothing to do

    # Compute embeddings once for main goals
    main_goal_embeddings = np.array([embed_main_goal(g) for g in main_goals])
    main_goal_ids = [g.id for g in main_goals]

    # Assign parent_id based on similarity
    for sub_goal in sub_goals_needing_parent:
        sub_embedding = embed_sub_goal(sub_goal).reshape(1, -1)
        similarities = np.dot(sub_embedding, main_goal_embeddings.T)[0]
        best_idx = int(np.argmax(similarities))
        sub_goal.parent_id = main_goal_ids[best_idx]

        # Optional debug
        print(f"Sub-goal '{sub_goal.title}' → Parent: '{main_goals[best_idx].title}' | Score: {similarities[best_idx]:.3f}")

    return sub_goals


def _test_assignments():
    main_goals = [
        Goal(id=None, title="Be More Spiritual", task="Develop inner peace and mindfulness", importance="mainGoal"),
        Goal(id=None, title="Land a Job", task="Successfully get hired in desired role", importance="mainGoal"),
    ]
    main_goal_embeddings = np.array([embed_main_goal(g) for g in main_goals])

    sub_goals = [
        Goal(id=None, title="Daily Meditation", task="Meditate 10 minutes every morning to quiet the mind and focus inward.", importance="low"),
        Goal(id=None, title="Practice Commitment", task="Stick to daily habits even when motivation is low. Build self-discipline through small consistent actions.", importance="medium"),
        Goal(id=None, title="Update Resume", task="Revise resume using the STAR method. Emphasize results and impact to better reflect qualifications.", importance="high"),
        Goal(id=None, title="Mock Interviews", task="Practicx`e answering behavioral and technical questions to reduce anxiety and improve clarity during interviews.", importance="medium"),
    ]

    for sg in sub_goals:
        parent_id = assign_parent_id(sg, main_goals, main_goal_embeddings)
        sg.parent_id = parent_id
        parent_title = next((g.title for g in main_goals if g.id == parent_id), None)
        print(f"Sub-goal '{sg.title}' assigned to main goal: '{parent_title}'\n")

if __name__ == "__main__":
    _test_assignments()
