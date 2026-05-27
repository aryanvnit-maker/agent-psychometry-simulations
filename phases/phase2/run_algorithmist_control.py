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
Phase 2 — ALGORITHMIST control condition.

Isolates whether the chain-2/specialized underperformance (13% vs 16% for
chain-2/generic) is caused by:

    (A) The ALGORITHMIST role instruction  — "design; do not write code"
    (B) The extreme Kalibr dimension profiles applied to the ALGORITHMIST
    (C) Both

Control condition: ALGORITHMIST role with balanced 75-baseline dimensions.
If this scores ~13%  → role instruction is the culprit.
If this scores ~16%  → extreme dimensions were the culprit.

Same 100 problems as Phase 2. Results written to results/algorithmist_control.jsonl.

Usage:
    python run_algorithmist_control.py [--n 100]

Env vars:
    GEMINI_API_KEY   required
    MODEL            default gemini-2.5-flash
    MODEL_PROVIDER   gemini | anthropic
"""
from __future__ import annotations
import argparse
import json
import os
import re as _re
import time
import uuid
from pathlib import Path

os.environ.setdefault("AGENT_TOKEN_BUDGET", "8192")

from dotenv import load_dotenv
load_dotenv()

from src.agents.profile import AgentProfile, KalibrDimensions, GameTheoryParams, Role, ConflictStyle
from src.datasets.codecontests import load_problems, format_prompt
from src.execution.judge0 import evaluate
from src.execution.extractor import extract
from src.orchestration.engine import run_simulation

RESULTS_DIR = Path("results")
OUT_FILE    = RESULTS_DIR / "algorithmist_control.jsonl"
CONDITION   = "chain-2/algorithmist-balanced"

_CP_CODE_HANDOFF = (
    "Based on the algorithmic analysis above, implement the complete Python solution now. "
    "Output exactly one ```python code block containing the full runnable solution. "
    "No explanation outside the code block."
)


# ---------------------------------------------------------------------------
# Agent profiles
# ---------------------------------------------------------------------------

def _algorithmist_balanced() -> AgentProfile:
    """ALGORITHMIST role with balanced 75-baseline dimensions — no extreme profiles."""
    return AgentProfile(
        agent_id="algorithmist_balanced",
        dimensions=KalibrDimensions(
            philosophy_cohesion=75,
            drive_alignment=75,
            bonding_index=50,
            adaptive_intelligence=75,
            volatility_vector=50,
            ambiguity_tolerance=70,
            influence_style=50,
            feedback_orientation=70,
            temporal_orientation=50,
            energy_resilience=75,
        ),
        role=Role.ALGORITHMIST,
        game_theory=GameTheoryParams(
            context_sharing="full",
            memory_persistence=False,
            signaling=False,
            conflict_style=ConflictStyle.NEGOTIATE,
        ),
    )


def _solver_balanced() -> AgentProfile:
    """Identical solver to chain-2/generic — holds constant across conditions."""
    return AgentProfile(
        agent_id="solver_balanced",
        dimensions=KalibrDimensions(
            philosophy_cohesion=75,
            drive_alignment=80,
            bonding_index=50,
            adaptive_intelligence=75,
            volatility_vector=50,
            ambiguity_tolerance=70,
            influence_style=50,
            feedback_orientation=70,
            temporal_orientation=50,
            energy_resilience=75,
        ),
        role=Role.SOLVER,
        game_theory=GameTheoryParams(
            context_sharing="full",
            memory_persistence=False,
            signaling=False,
            conflict_style=ConflictStyle.NEGOTIATE,
        ),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_callable(code: str) -> str:
    for fname in ("solve", "main"):
        if _re.search(rf'^def {fname}\s*\(', code, _re.MULTILINE):
            if not _re.search(rf'^{fname}\s*\(', code, _re.MULTILINE):
                if '__name__' not in code:
                    return code.rstrip() + f'\n\n{fname}()\n'
    return code


def _load_done() -> set[str]:
    done: set[str] = set()
    if not OUT_FILE.exists():
        return done
    with OUT_FILE.open() as f:
        for line in f:
            try:
                done.add(json.loads(line)["problem_id"])
            except Exception:
                pass
    return done


def _append(rec: dict) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    with OUT_FILE.open("a") as f:
        f.write(json.dumps(rec) + "\n")


# ---------------------------------------------------------------------------
# Single run
# ---------------------------------------------------------------------------

def run_one(problem) -> dict:
    agents  = [_algorithmist_balanced(), _solver_balanced()]
    prompt  = format_prompt(problem)
    t0      = time.time()

    try:
        state = run_simulation(
            agents=agents,
            scenario_brief=prompt,
            phase="phase2_control",
            topology="chain",
            flat_rounds=2,
            chain_handoff_prompts={1: _CP_CODE_HANDOFF},
        )
    except Exception as e:
        return {
            "run_id":            str(uuid.uuid4()),
            "condition":         CONDITION,
            "problem_id":        problem.problem_id,
            "difficulty":        problem.difficulty,
            "passed":            False,
            "compilation_error": False,
            "pass_rate":         0.0,
            "tests_passed":      0,
            "tests_total":       len(problem.private_tests),
            "extraction_failed": True,
            "elapsed_seconds":   round(time.time() - t0, 2),
            "error":             str(e),
        }

    code = extract(state["messages"], topology="chain", n_agents=2)
    code = _ensure_callable(code)
    extraction_failed = not bool(code.strip())

    if extraction_failed:
        return {
            "run_id":            state["run_id"],
            "condition":         CONDITION,
            "problem_id":        problem.problem_id,
            "difficulty":        problem.difficulty,
            "passed":            False,
            "compilation_error": False,
            "pass_rate":         0.0,
            "tests_passed":      0,
            "tests_total":       len(problem.private_tests),
            "extraction_failed": True,
            "elapsed_seconds":   round(time.time() - t0, 2),
        }

    result = evaluate(code, problem.private_tests, time_limit=problem.time_limit)

    return {
        "run_id":            state["run_id"],
        "condition":         CONDITION,
        "problem_id":        problem.problem_id,
        "difficulty":        problem.difficulty,
        "passed":            result["passed"],
        "compilation_error": result["compilation_error"],
        "pass_rate":         result.get("pass_rate", 0.0),
        "tests_passed":      result.get("tests_passed", 0),
        "tests_total":       result.get("tests_total", 0),
        "extraction_failed": False,
        "elapsed_seconds":   round(time.time() - t0, 2),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Phase 2 ALGORITHMIST control")
    parser.add_argument("--n", type=int, default=100, help="Problems to run (default 100)")
    args = parser.parse_args()

    problems = load_problems(n=args.n)
    print(f"Loaded {len(problems)} problems")

    done = _load_done()
    print(f"Already completed: {len(done)}\n")

    pending = [p for p in problems if p.problem_id not in done]
    total   = len(pending)

    passed_count = 0
    for i, prob in enumerate(pending, 1):
        rec = run_one(prob)
        _append(rec)

        if rec["passed"]:
            passed_count += 1

        status = (
            "PASS"   if rec["passed"] else
            "CE"     if rec["compilation_error"] else
            "NOCODE" if rec["extraction_failed"] else
            f"FAIL {rec['tests_passed']}/{rec['tests_total']}"
        )
        print(f"  [{i}/{total}] {prob.problem_id} — {status}  ({rec['elapsed_seconds']:.1f}s)")
        time.sleep(0.1)

    # Final summary
    all_records = []
    with OUT_FILE.open() as f:
        for line in f:
            try:
                all_records.append(json.loads(line))
            except Exception:
                pass

    n       = len(all_records)
    passed  = sum(1 for r in all_records if r.get("passed"))
    ce      = sum(1 for r in all_records if r.get("compilation_error"))
    nocode  = sum(1 for r in all_records if r.get("extraction_failed"))
    avg_pr  = sum(r.get("pass_rate", 0) for r in all_records) / n if n else 0

    print(f"\n{'='*60}")
    print(f"ALGORITHMIST control complete")
    print(f"{'='*60}")
    print(f"  Condition : {CONDITION}")
    print(f"  N         : {n}")
    print(f"  Pass@1    : {passed}/{n} ({passed/n*100:.1f}%)")
    print(f"  Avg rate  : {avg_pr*100:.1f}%")
    print(f"  CE        : {ce}")
    print(f"  NoCode    : {nocode}")
    print(f"\n  Results   : {OUT_FILE}")
    print(f"\n  Interpretation:")
    print(f"    chain-2/generic    = 16%  (IMPLEMENTER × 2, balanced dims)")
    print(f"    chain-2/specialized = 13%  (ALGORITHMIST extreme + IMPLEMENTER extreme)")
    print(f"    this control        = {passed/n*100:.1f}%  (ALGORITHMIST balanced + SOLVER balanced)")
    if passed/n*100 <= 14:
        print(f"    >> Score near 13% → ALGORITHMIST role instruction is the culprit.")
    elif passed/n*100 >= 15:
        print(f"    >> Score near 16% → extreme dimension profiles were the culprit.")
    else:
        print(f"    >> Ambiguous — both role and dimensions may contribute.")


if __name__ == "__main__":
    main()
