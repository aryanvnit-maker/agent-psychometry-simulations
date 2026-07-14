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
Phase E — quick results summary. Avoids piping JSONL through tools that
only handle a single JSON document (e.g. `python -m json.tool`), which
errors with "Extra data" on anything but exactly one line.

Usage:
    python phases/phase_e/summarize.py                # all records
    python phases/phase_e/summarize.py --tail 18       # last N records
    python phases/phase_e/summarize.py --scenario e02_eggs_cvd
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

RESULTS_FILE = Path("results/phase_e.jsonl")


def main():
    parser = argparse.ArgumentParser(description="Phase E results summary")
    parser.add_argument("--tail", type=int, default=None,
                        help="Only show the last N records")
    parser.add_argument("--scenario", type=str, default=None,
                        help="Filter to one scenario_id")
    parser.add_argument("--condition", type=str, default=None,
                        help="Filter to one condition")
    args = parser.parse_args()

    if not RESULTS_FILE.exists():
        print(f"{RESULTS_FILE} not found.")
        return

    with RESULTS_FILE.open() as f:
        lines = f.readlines()

    if args.tail:
        lines = lines[-args.tail:]

    n_shown, n_parsed = 0, 0
    for line in lines:
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if args.scenario and r.get("scenario_id") != args.scenario:
            continue
        if args.condition and r.get("condition") != args.condition:
            continue
        n_shown += 1
        parsed = r.get("map_parsed")
        if parsed:
            n_parsed += 1
        print(
            f"{r.get('scenario_id', '?'):<24} "
            f"{r.get('condition', '?'):<16} "
            f"rep{r.get('rep', '?'):<3} "
            f"score={r.get('task_score', 0):6.1f}  "
            f"map_parsed={parsed}  "
            f"model={r.get('model', '?')}  "
            f"run_id={r.get('run_id', '?')}"
        )

    print(f"\n{n_shown} record(s) shown, {n_parsed} with a parsed EpistemicMap.")


if __name__ == "__main__":
    main()
