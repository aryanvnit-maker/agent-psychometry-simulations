#!/usr/bin/env python3
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

"""
Archive runs + evaluations to backup tables, then delete from live tables.

ALWAYS backs up before deleting — rows are copied to runs_backup and
evaluations_backup (created automatically if they don't exist) before
any DELETE is issued. Safe to run multiple times; backup tables accumulate.

Usage:
    python purge_all_runs.py                          # archive + purge all
    python purge_all_runs.py --model-family gemini    # one model family only
    python purge_all_runs.py --topology chain         # one topology only
    python purge_all_runs.py --dry-run                # show count, no changes
    python purge_all_runs.py --backup-only            # archive only, no delete
"""
from __future__ import annotations
import argparse
from dotenv import load_dotenv
load_dotenv()

from src.telemetry.database import get_conn

_CREATE_RUNS_BACKUP = """
CREATE TABLE IF NOT EXISTS runs_backup (
    LIKE runs INCLUDING ALL
);
"""

_CREATE_EVALS_BACKUP = """
CREATE TABLE IF NOT EXISTS evaluations_backup (
    LIKE evaluations INCLUDING ALL
);
"""


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


def main(topology: str | None, model_family: str | None, dry_run: bool, backup_only: bool) -> None:
    filters, params = _build_filters(topology, model_family)

    desc = []
    if topology:
        desc.append(f"topology={topology}")
    if model_family:
        desc.append(f"model_family={model_family}")
    label = " | ".join(desc) if desc else "ALL"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM runs{filters}", params or None)
            n_runs = cur.fetchone()[0]
            cur.execute(
                f"SELECT COUNT(*) FROM evaluations WHERE run_id IN (SELECT run_id FROM runs{filters})",
                params or None,
            )
            n_evals = cur.fetchone()[0]

        print(f"Runs matching [{label}]: {n_runs}")
        print(f"Evaluations matching:     {n_evals}")

        if dry_run:
            print("DRY RUN — no changes made.")
            return

        if n_runs == 0:
            print("Nothing to archive/delete.")
            return

        action = "Archive (no delete)" if backup_only else "Archive + delete"
        confirm = input(f"{action} {n_runs} runs and {n_evals} evaluations? [yes/N] ").strip().lower()
        if confirm != "yes":
            print("Aborted.")
            return

        with conn.cursor() as cur:
            # Create backup tables if they don't exist
            cur.execute(_CREATE_RUNS_BACKUP)
            cur.execute(_CREATE_EVALS_BACKUP)

            # Copy evaluations to backup
            cur.execute(
                f"""
                INSERT INTO evaluations_backup
                SELECT e.* FROM evaluations e
                WHERE e.run_id IN (SELECT run_id FROM runs{filters})
                ON CONFLICT DO NOTHING
                """,
                params or None,
            )
            evals_backed = cur.rowcount

            # Copy runs to backup
            cur.execute(
                f"""
                INSERT INTO runs_backup
                SELECT * FROM runs{filters}
                ON CONFLICT DO NOTHING
                """,
                params or None,
            )
            runs_backed = cur.rowcount

        print(f"Backed up: {runs_backed} runs, {evals_backed} evaluations")

        if backup_only:
            print("Backup complete — live tables unchanged.")
            return

        with conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM evaluations WHERE run_id IN (SELECT run_id FROM runs{filters})",
                params or None,
            )
            evals_deleted = cur.rowcount
            cur.execute(f"DELETE FROM runs{filters}", params or None)
            runs_deleted = cur.rowcount

        print(f"Deleted:   {runs_deleted} runs, {evals_deleted} evaluations")
        print("Backup tables: runs_backup, evaluations_backup — data is safe.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topology", choices=["chain", "flat"])
    parser.add_argument("--model-family")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--backup-only", action="store_true",
                        help="Archive to backup tables but do not delete from live tables.")
    args = parser.parse_args()
    main(args.topology, args.model_family, args.dry_run, args.backup_only)
