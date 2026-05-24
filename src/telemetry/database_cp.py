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

"""Supabase persistence for KalibrBench-CP runs."""
from __future__ import annotations
from .database import get_conn


def already_completed_cp(problem_id: str, topology: str, condition: str, model_family: str = "gemini") -> bool:
    """True if this (problem, topology, condition, model) combination is already stored."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM cp_runs
                WHERE problem_id = %s AND topology = %s AND condition = %s AND model_family = %s
                LIMIT 1
                """,
                (problem_id, topology, condition, model_family),
            )
            return cur.fetchone() is not None


def insert_cp_run(
    run_id: str,
    problem_id: str,
    difficulty: int,
    topology: str,
    condition: str,
    passed: bool,
    compilation_error: bool,
    tests_passed: int,
    tests_total: int,
    pass_rate: float,
    extraction_failed: bool,
    tokens_total: int,
    elapsed_seconds: float | None = None,
    model_family: str = "gemini",
) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cp_runs (
                    run_id, problem_id, difficulty, topology, condition,
                    passed, compilation_error, tests_passed, tests_total,
                    pass_rate, extraction_failed, tokens_total,
                    elapsed_seconds, model_family
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (run_id) DO NOTHING
                """,
                (
                    run_id, problem_id, difficulty, topology, condition,
                    passed, compilation_error, tests_passed, tests_total,
                    pass_rate, extraction_failed, tokens_total,
                    elapsed_seconds, model_family,
                ),
            )
