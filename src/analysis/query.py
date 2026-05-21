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

# Big Five proxies from Kalibr dimensions (Barrick et al. mapping)
_CONSCIENTIOUSNESS_PROXY = ["drive_alignment", "philosophy_cohesion", "energy_resilience"]
_AGREEABLENESS_PROXY     = ["bonding_index", "feedback_orientation"]


def load_results(topology: str | None = None) -> pd.DataFrame:
    topology_filter = "AND r.topology = %(topology)s" if topology else ""
    with get_conn() as conn:
        df = pd.read_sql(
            f"""
            SELECT
                r.run_id,
                r.topology,
                r.scenario_id,
                r.team_size,
                r.composition_condition,
                r.composition_matrix,
                r.turns_to_complete,
                r.token_cost,
                AVG((e.scores->>'task_score')::float)             AS task_score,
                AVG((e.scores->>'geq_task_cohesion')::float)      AS geq_task,
                AVG((e.scores->>'geq_social_cohesion')::float)    AS geq_social,
                AVG((e.scores->>'tci_innovation')::float)         AS tci_innovation,
                AVG((e.scores->>'firo_inclusion')::float)         AS firo_inclusion,
                AVG((e.scores->>'contradiction_count')::float)    AS contradictions,
                AVG((e.scores->>'novel_approaches_count')::float) AS novel_approaches,
                AVG((e.scores->>'context_fidelity_mean')::float)  AS context_fidelity,
                BOOL_OR((e.scores->>'consensus_achieved')::boolean) AS consensus_achieved
            FROM runs r
            JOIN evaluations e ON r.run_id = e.run_id
            WHERE r.scenario_id != ''
            {topology_filter}
            GROUP BY r.run_id, r.topology, r.scenario_id, r.team_size,
                     r.composition_condition, r.composition_matrix,
                     r.turns_to_complete, r.token_cost
            ORDER BY r.topology, r.scenario_id, r.team_size, r.composition_condition
            """,
            conn,
            params={"topology": topology} if topology else None,
        )

    df["composition_matrix"] = df["composition_matrix"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else x
    )

    # Derived columns computed from composition_matrix
    df["cognitive_diversity"]        = df["composition_matrix"].apply(_diversity_score)
    df["conscientiousness_mean"]     = df["composition_matrix"].apply(
        lambda m: _dim_mean(m, _CONSCIENTIOUSNESS_PROXY))
    df["conscientiousness_variance"] = df["composition_matrix"].apply(
        lambda m: _dim_variance(m, _CONSCIENTIOUSNESS_PROXY))
    df["agreeableness_mean"]         = df["composition_matrix"].apply(
        lambda m: _dim_mean(m, _AGREEABLENESS_PROXY))
    df["agreeableness_variance"]     = df["composition_matrix"].apply(
        lambda m: _dim_variance(m, _AGREEABLENESS_PROXY))

    # Psychological safety composite (Aristotle proxy)
    # consensus + low contradictions + high inclusion → normalised 0-100
    df["psych_safety"] = (
        df["consensus_achieved"].astype(float) * 40
        + (1 - (df["contradictions"].clip(0, 5) / 5)) * 30
        + df["firo_inclusion"] * 30
    )

    return df


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_agents(matrix_raw) -> list[dict]:
    if isinstance(matrix_raw, str):
        matrix = json.loads(matrix_raw)
    else:
        matrix = matrix_raw
    return list(matrix.values())


def _diversity_score(matrix_raw) -> float:
    agents = _get_agents(matrix_raw)
    if len(agents) <= 1:
        return 0.0
    stds = []
    for dim in _DIMENSIONS:
        vals = [a["dimensions"].get(dim, 50) for a in agents]
        stds.append(np.std(vals))
    return float(np.mean(stds))


def _dim_mean(matrix_raw, dims: list[str]) -> float:
    agents = _get_agents(matrix_raw)
    if not agents:
        return 0.0
    vals = [a["dimensions"].get(d, 50) for a in agents for d in dims]
    return float(np.mean(vals))


def _dim_variance(matrix_raw, dims: list[str]) -> float:
    agents = _get_agents(matrix_raw)
    if len(agents) <= 1:
        return 0.0
    # Variance of per-agent means across those dimensions
    agent_means = [np.mean([a["dimensions"].get(d, 50) for d in dims]) for a in agents]
    return float(np.var(agent_means))
