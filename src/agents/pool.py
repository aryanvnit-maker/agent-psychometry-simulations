from __future__ import annotations
import random
from .profile import AgentProfile, KalibrDimensions, GameTheoryParams, Role, ConflictStyle

_WORKER_ROLES = [
    Role.COORDINATOR,
    Role.PLANT,
    Role.IMPLEMENTER,
    Role.DEVIL_ADVOCATE,
    Role.MONITOR_EVALUATOR,
    Role.COMPLETER_FINISHER,
]

_CONFLICT_STYLES = list(ConflictStyle)


def _random_game_theory() -> GameTheoryParams:
    return GameTheoryParams(
        context_sharing=random.choice(["full", "filtered"]),
        memory_persistence=random.choice([True, False]),
        signaling=random.choice([True, False]),
        conflict_style=random.choice(_CONFLICT_STYLES),
    )


def initialise_pool(seed: int | None = None) -> list[AgentProfile]:
    if seed is not None:
        random.seed(seed)

    pool: list[AgentProfile] = []

    for i in range(32):
        pool.append(AgentProfile(
            agent_id=f"worker_{i:02d}",
            dimensions=KalibrDimensions.random(),
            role=random.choice(_WORKER_ROLES),
            game_theory=_random_game_theory(),
            is_judge=False,
        ))

    for j in range(3):
        pool.append(AgentProfile(
            agent_id=f"judge_{j:02d}",
            dimensions=KalibrDimensions.judge_profile(),
            role=Role.JUDGE,
            game_theory=GameTheoryParams(
                context_sharing="full",
                memory_persistence=True,
                signaling=True,
                conflict_style=ConflictStyle.NEGOTIATE,
            ),
            is_judge=True,
        ))

    return pool


def get_workers(pool: list[AgentProfile]) -> list[AgentProfile]:
    return [a for a in pool if not a.is_judge]


def get_judges(pool: list[AgentProfile]) -> list[AgentProfile]:
    return [a for a in pool if a.is_judge]


def select_captain(workers: list[AgentProfile], task_dimensions: list[str]) -> AgentProfile:
    """Return the worker with the highest mean score across task-relevant dimensions."""
    def task_score(agent: AgentProfile) -> float:
        scores = [getattr(agent.dimensions, dim) for dim in task_dimensions if hasattr(agent.dimensions, dim)]
        return sum(scores) / len(scores) if scores else 0.0

    return max(workers, key=task_score)
