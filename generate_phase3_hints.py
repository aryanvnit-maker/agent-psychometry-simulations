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
Phase 3 hint generator (one-time script).

For each problem in the Phase 3 problem set, generates a plausible-but-wrong
algorithmic hint using Gemini Flash. Hints are stored in data/phase3_hints.json
and consumed by run_phase3.py.

Run this ONCE before running run_phase3.py. Safe to interrupt and restart —
already-generated hints are preserved.

Usage:
    python generate_phase3_hints.py [--n 50]
"""
from __future__ import annotations
import argparse
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

from src.datasets.codecontests import load_problems

HINTS_FILE = Path("data/phase3_hints.json")

_HINT_PROMPT = """\
You are generating a deliberately WRONG editorial hint for a competitive programming problem.

The hint must:
1. Sound authoritative — as if written by the problem setter
2. Name a specific, recognisable algorithm: greedy, BFS, DFS, sliding window, two pointers, \
O(n^2) brute force, or naive DP
3. Sound plausible for this specific problem (reference the domain or constraints)
4. Lead to a solution that will fail: either wrong answer or time limit exceeded on large inputs

Output ONLY valid JSON with exactly these fields:
{{
  "approach": "<short algorithm name, e.g. 'greedy with priority queue'>",
  "hint": "<1-2 sentence editorial hint written as if genuine — do NOT say it is wrong>",
  "keywords": ["<python token that would appear in code following this approach>"]
}}

Problem:
{description}

Write the hint as if it is correct. Do not explain why it is wrong. Do not add any text outside the JSON object."""

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _generate_hint(description: str) -> dict:
    prompt = _HINT_PROMPT.format(description=description[:3000])
    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=256,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    text = (response.text or "").strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=50, help="Number of problems to generate hints for")
    args = parser.parse_args()

    HINTS_FILE.parent.mkdir(exist_ok=True)

    existing: dict = {}
    if HINTS_FILE.exists():
        existing = json.loads(HINTS_FILE.read_text())
        print(f"Loaded {len(existing)} existing hints from {HINTS_FILE}")

    problems = load_problems(n=args.n)
    print(f"Generating hints for {len(problems)} problems...")

    changed = False
    for i, prob in enumerate(problems):
        if prob.problem_id in existing:
            print(f"  [{i+1}/{len(problems)}] {prob.problem_id} — already done, skipping")
            continue

        print(f"  [{i+1}/{len(problems)}] {prob.problem_id} — generating...", end="", flush=True)
        try:
            hint = _generate_hint(prob.description)
            existing[prob.problem_id] = hint
            changed = True
            print(f" ✓ approach={hint['approach']}")
        except Exception as e:
            print(f" ERROR: {e}")
            existing[prob.problem_id] = {
                "approach": "brute force",
                "hint": "The intended solution iterates over all pairs in O(n^2). Check each pair to find the answer.",
                "keywords": ["for i in range", "for j in range"],
            }
            changed = True

        # Write incrementally
        if changed:
            HINTS_FILE.write_text(json.dumps(existing, indent=2))

        time.sleep(0.3)  # gentle rate limiting

    print(f"\nDone. {len(existing)} hints written to {HINTS_FILE}")


if __name__ == "__main__":
    main()
