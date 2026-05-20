from __future__ import annotations
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# Supabase: use the connection pooler URL from Project Settings → Database → Connection string
# Format: postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
_DSN = os.getenv("DATABASE_URL")


@contextmanager
def get_conn():
    if not _DSN:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env and add your Supabase connection string.")
    dsn = _DSN.split("?")[0]  # strip ?pgbouncer=true — psycopg2 doesn't support it
    conn = psycopg2.connect(dsn, sslmode="require")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_run(
    run_id: str,
    composition_matrix: dict,
    topology: str,
    task_phase: str,
    scenario_category: str,
    composition_condition: str,
    team_size: int,
    captain_agent_id: str | None,
    draft_order: int | None,
    token_cost: int | None,
    turns_to_complete: int | None,
    cull_events: list,
    state_snapshot: dict | None,
) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO runs (
                    run_id, composition_matrix, topology, task_phase,
                    scenario_category, composition_condition, team_size,
                    captain_agent_id, draft_order, token_cost,
                    turns_to_complete, cull_events, state_snapshot
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    json.dumps(composition_matrix),
                    topology,
                    task_phase,
                    scenario_category,
                    composition_condition,
                    team_size,
                    captain_agent_id,
                    draft_order,
                    token_cost,
                    turns_to_complete,
                    json.dumps(cull_events),
                    json.dumps(state_snapshot) if state_snapshot else None,
                ),
            )


def insert_evaluation(run_id: str, judge_index: int, scores: dict) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO evaluations (run_id, judge_index, scores) VALUES (%s, %s, %s)",
                (run_id, judge_index, json.dumps(scores)),
            )


def save_state_snapshot(run_id: str, snapshot: dict) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE runs SET state_snapshot = %s WHERE run_id = %s",
                (json.dumps(snapshot), run_id),
            )
