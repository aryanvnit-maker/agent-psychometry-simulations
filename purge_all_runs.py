#!/usr/bin/env python3
"""
Delete ALL runs and their evaluations from Supabase.

Use before re-running the full batch with a new judge or scoring methodology.
The simulation pool is deterministic (seed=42), so results will reproduce exactly.

Usage:
    python purge_all_runs.py
    python purge_all_runs.py --model-family gemini   # only purge one model family
    python purge_all_runs.py --topology chain        # only purge one topology
    python purge_all_runs.py --dry-run               # show count without deleting
"""
from __future__ import annotations
import argparse
from dotenv import load_dotenv
load_dotenv()

from src.telemetry.database import get_conn


def count_runs(conn, topology: str | None, model_family: str | None) -> int:
    filters, params = _build_filters(topology, model_family)
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM runs{filters}", params)
        return cur.fetchone()[0]


def purge(topology: str | None, model_family: str | None, dry_run: bool) -> None:
    filters, params = _build_filters(topology, model_family)

    with get_conn() as conn:
        n = count_runs(conn, topology, model_family)
        desc = []
        if topology:
            desc.append(f"topology={topology}")
        if model_family:
            desc.append(f"model_family={model_family}")
        label = " | ".join(desc) if desc else "ALL"

        print(f"Runs matching [{label}]: {n}")

        if dry_run:
            print("DRY RUN — no changes made.")
            return

        if n == 0:
            print("Nothing to delete.")
            return

        confirm = input(f"Delete {n} runs and all their evaluations? [yes/N] ").strip().lower()
        if confirm != "yes":
            print("Aborted.")
            return

        with conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM evaluations WHERE run_id IN (SELECT run_id FROM runs{filters})",
                params,
            )
            evals_deleted = cur.rowcount
            cur.execute(f"DELETE FROM runs{filters}", params)
            runs_deleted = cur.rowcount

        print(f"Deleted {runs_deleted} runs and {evals_deleted} evaluations.")


def _build_filters(topology: str | None, model_family: str | None):
    clauses, params = [], []
    if topology:
        clauses.append("topology = %s")
        params.append(topology)
    if model_family:
        clauses.append("model_family = %s")
        params.append(model_family)
    filters = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    return filters, params


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topology", choices=["chain", "flat"])
    parser.add_argument("--model-family")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    purge(args.topology, args.model_family, args.dry_run)
