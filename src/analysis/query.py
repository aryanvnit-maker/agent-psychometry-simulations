from __future__ import annotations
import json
import numpy as np
import pandas as pd
from src.telemetry.database import get_conn

_DIMENSIONS = [
    "philosophy_cohesion", "drive_alignment", "bonding_index",
    "adaptive_intelligence", "volatility_vector", "ambiguity_tolerance",
    "influence_style", "feedback_orientation", "temporal_orientation",
    "energy_resilience",
]


def load_results() -> pd.DataFrame:
    """
    Query Supabase and return a flat DataFrame with one row per run,
    scores averaged across the three judges.
    """
    with get_conn() as conn:
        df = pd.read_sql(
            """
            SELECT
                r.run_id,
                r.scenario_id,
                r.team_size,
                r.composition_condition,
                r.composition_matrix,
                r.turns_to_complete,
                r.token_cost,
                AVG((e.scores->>'task_score')::float)         AS task_score,
                AVG((e.scores->>'geq_task_cohesion')::float)  AS geq_task,
                AVG((e.scores->>'geq_social_cohesion')::float)AS geq_social,
                AVG((e.scores->>'tci_innovation')::float)     AS tci_innovation,
                AVG((e.scores->>'firo_inclusion')::float)     AS firo_inclusion,
                AVG((e.scores->>'contradiction_count')::float)AS contradictions,
                AVG((e.scores->>'novel_approaches_count')::float) AS novel_approaches,
                BOOL_OR((e.scores->>'consensus_achieved')::boolean) AS consensus_achieved
            FROM runs r
            JOIN evaluations e ON r.run_id = e.run_id
            GROUP BY r.run_id, r.scenario_id, r.team_size,
                     r.composition_condition, r.composition_matrix,
                     r.turns_to_complete, r.token_cost
            ORDER BY r.scenario_id, r.team_size, r.composition_condition
            """,
            conn,
        )

    df["cognitive_diversity"] = df["composition_matrix"].apply(_diversity_score)
    df["composition_matrix"] = df["composition_matrix"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else x
    )
    return df


def _diversity_score(matrix_raw) -> float:
    """
    Mean standard deviation of all 10 Kalibr dimensions across agents in the team.
    Higher = more cognitively diverse team.
    """
    if isinstance(matrix_raw, str):
        matrix = json.loads(matrix_raw)
    else:
        matrix = matrix_raw

    agents = list(matrix.values())
    if len(agents) <= 1:
        return 0.0

    scores_by_dim = []
    for dim in _DIMENSIONS:
        vals = [a["dimensions"].get(dim, 50) for a in agents]
        scores_by_dim.append(np.std(vals))

    return float(np.mean(scores_by_dim))
