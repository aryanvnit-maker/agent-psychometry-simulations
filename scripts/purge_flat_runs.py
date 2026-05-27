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
