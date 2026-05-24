# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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


def already_completed(
    scenario_id: str,
    topology: str,
    composition_condition: str,
    team_size: int,
    model_family: str = "gemini",
) -> bool:
    """Return True if this combination has a run with at least one evaluation stored."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM runs r
                WHERE r.scenario_id = %s
                  AND r.topology = %s
                  AND r.composition_condition = %s
                  AND r.team_size = %s
                  AND r.model_family = %s
                  AND EXISTS (SELECT 1 FROM evaluations e WHERE e.run_id = r.run_id)
                LIMIT 1
                """,
                (scenario_id, topology, composition_condition, team_size, model_family),
            )
            return cur.fetchone() is not None


def insert_run(
    run_id: str,
    scenario_id: str,
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
    model_family: str = "gemini",
    transcript: str | None = None,
) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO runs (
                    run_id, scenario_id, composition_matrix, topology, task_phase,
                    scenario_category, composition_condition, team_size,
                    captain_agent_id, draft_order, token_cost,
                    turns_to_complete, cull_events, state_snapshot, model_family,
                    transcript
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    scenario_id,
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
                    model_family,
                    transcript,
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


def load_runs_with_transcripts(model_family: str | None = None) -> list[dict]:
    """Return all runs that have a stored transcript, with scenario metadata."""
    filters = "WHERE r.transcript IS NOT NULL AND r.transcript != ''"
    params: list = []
    if model_family:
        filters += " AND r.model_family = %s"
        params.append(model_family)
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT r.run_id, r.scenario_id, r.topology, r.model_family,
                       r.composition_condition, r.team_size, r.task_phase,
                       r.transcript
                FROM runs r
                {filters}
                ORDER BY r.model_family, r.topology, r.scenario_id
                """,
                params or None,
            )
            return [dict(row) for row in cur.fetchall()]


def delete_evaluations(run_id: str) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM evaluations WHERE run_id = %s", (run_id,))


def delete_run(run_id: str) -> None:
    """Delete a run and all its evaluations."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM evaluations WHERE run_id = %s", (run_id,))
            cur.execute("DELETE FROM runs WHERE run_id = %s", (run_id,))
