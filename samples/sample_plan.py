from utils.models import Goal, Plan

PLAN = Plan(
    goals={
        goal.id: goal for goal in [
            Goal(
                title='Implement Grounding Technique',
                task='Practice the 5-4-3-2-1 grounding technique whenever anxiety spikes.',
                importance='high'
            ),
            Goal(
                title='Evening Gratitude and Accomplishment Journal',
                task="Each evening, journal one work accomplishment, one moment of resilience, and one thing you're grateful for.",
                importance='medium'
            ),
            Goal(
                title='Challenge Negative Self-Talk',
                task="Identify and reframe negative self-talk. For example, change 'What if they say I'm not good enough?' to 'I've consistently contributed and grown—my review is a checkpoint, not a judgment.'",
                importance='medium'
            ),
            Goal(
                title='Prepare Self-Evaluation',
                task='Draft a self-evaluation focusing on progress and contributions.',
                importance='low'
            ),
            Goal(
                title='Recognize and Counteract Discounting the Positive',
                task='Reflect on instances of discounting the positive and identify your accomplishments.',
                importance='low'
            )
        ]
    },
    events=[]
)