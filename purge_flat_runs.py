#!/usr/bin/env python3
"""
Delete all flat-topology runs and their evaluations from Supabase.
Run this before re-running 'python run_all.py --topology flat' after a bug fix.
"""
from dotenv import load_dotenv
load_dotenv()

from src.telemetry.database import get_conn

with get_conn() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM runs WHERE topology = 'flat'")
        n_runs = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM evaluations WHERE run_id IN "
            "(SELECT run_id FROM runs WHERE topology = 'flat')"
        )
        n_evals = cur.fetchone()[0]
        print(f"Found {n_runs} flat runs and {n_evals} evaluations to delete.")

        if n_runs == 0:
            print("Nothing to delete.")
        else:
            confirm = input("Delete? [y/N] ")
            if confirm.strip().lower() == "y":
                cur.execute(
                    "DELETE FROM evaluations WHERE run_id IN "
                    "(SELECT run_id FROM runs WHERE topology = 'flat')"
                )
                cur.execute("DELETE FROM runs WHERE topology = 'flat'")
                print("Deleted.")
            else:
                print("Aborted.")
