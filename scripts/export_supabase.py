#!/usr/bin/env python3
"""
Export Phase 1 data from Supabase to results/phase1.jsonl.

Each record = one simulation run with mean task_score averaged across judges.

Usage:
    python scripts/export_supabase.py
    python scripts/export_supabase.py --model-family anthropic
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.telemetry.database import get_conn

OUTPUT = Path("results/phase1.jsonl")


def export(model_family: str | None = None) -> None:
    filter_clause = ""
    params: list = []
    if model_family:
        filter_clause = "AND r.model_family = %s"
        params.append(model_family)

    query = f"""
        SELECT
            r.run_id,
            r.scenario_id,
            r.topology,
            r.composition_condition,
            r.team_size,
            r.model_family,
            r.task_phase,
            r.scenario_category,
            r.turns_to_complete,
            r.token_cost,
            AVG((e.scores->>'task_score')::float)          AS task_score,
            AVG((e.scores->>'geq_task_cohesion')::float)   AS geq_task_cohesion,
            AVG((e.scores->>'geq_social_cohesion')::float) AS geq_social_cohesion,
            AVG((e.scores->>'tci_innovation')::float)      AS tci_innovation,
            AVG((e.scores->>'firo_inclusion')::float)      AS firo_inclusion,
            BOOL_OR((e.scores->>'consensus_achieved')::boolean) AS consensus_achieved,
            AVG((e.scores->>'contradiction_count')::float) AS contradiction_count,
            COUNT(e.judge_index)                           AS n_judges
        FROM runs r
        JOIN evaluations e ON e.run_id = r.run_id
        WHERE (e.scores->>'task_score') IS NOT NULL
        {filter_clause}
        GROUP BY
            r.run_id, r.scenario_id, r.topology, r.composition_condition,
            r.team_size, r.model_family, r.task_phase, r.scenario_category,
            r.turns_to_complete, r.token_cost
        ORDER BY r.model_family, r.topology, r.team_size, r.scenario_id
    """

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or None)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]

    records = [dict(zip(cols, row)) for row in rows]

    OUTPUT.parent.mkdir(exist_ok=True)
    with OUTPUT.open("w") as f:
        for r in records:
            # psycopg2 returns Decimal for AVG — convert to float
            cleaned = {
                k: float(v) if hasattr(v, "__float__") and not isinstance(v, (int, bool)) else v
                for k, v in r.items()
            }
            f.write(json.dumps(cleaned) + "\n")

    print(f"Exported {len(records)} runs → {OUTPUT}")

    # Quick summary
    from collections import defaultdict
    by_topo_size: dict[tuple, list] = defaultdict(list)
    for r in records:
        key = (r["topology"], r["team_size"], r["model_family"])
        by_topo_size[key].append(float(r["task_score"]) if r["task_score"] else 0.0)

    print(f"\n{'Topology':<10} {'Size':>5} {'Model':<12} {'N':>5} {'Mean score':>12}")
    print("-" * 48)
    for (topo, size, model), scores in sorted(by_topo_size.items()):
        mean = sum(scores) / len(scores)
        print(f"{topo:<10} {size:>5} {model:<12} {len(scores):>5} {mean:>12.1f}")


def main():
    parser = argparse.ArgumentParser(description="Export Phase 1 Supabase data to JSONL")
    parser.add_argument("--model-family", default=None, help="Filter by model family (gemini/anthropic)")
    args = parser.parse_args()
    export(args.model_family)


if __name__ == "__main__":
    main()
