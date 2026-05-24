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
KalibrBench-CP: single-agent (chain-1) baseline calibration.

Runs a generic IMPLEMENTER agent on N CodeContests problems and evaluates
pass@1 via Judge0. Results written incrementally to results/cp_baseline.jsonl
so the run is resumable.

Usage:
    GEMINI_API_KEY=... python run_cp_baseline.py [--n 100] [--dry-run]

Env vars:
    GEMINI_API_KEY / ANTHROPIC_API_KEY  — API credentials
    MODEL                               — model ID (default: gemini-2.5-flash)
    MODEL_PROVIDER                      — gemini | anthropic (default: gemini)
    JUDGE0_URL                          — Judge0 base URL (default: http://localhost:2358)
    AGENT_TOKEN_BUDGET                  — max output tokens per agent turn (default: 4096)
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

# Raise token budget before importing engine so the module-level constant picks it up
os.environ.setdefault("AGENT_TOKEN_BUDGET", "4096")

from dotenv import load_dotenv
load_dotenv()

from src.agents.profile import AgentProfile, KalibrDimensions, GameTheoryParams, Role, ConflictStyle
from src.datasets.codecontests import load_problems, format_prompt
from src.execution.judge0 import evaluate, health_check
from src.execution.extractor import extract
from src.orchestration.engine import run_simulation

RESULTS_DIR  = Path("results")
BASELINE_OUT = RESULTS_DIR / "cp_baseline.jsonl"

# Generic capable IMPLEMENTER — high integrity, adaptive, execution-focused.
# Not tuned for competitive programming; this is the unspecialized baseline.
_BASELINE_DIMENSIONS = KalibrDimensions(
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
)


def _baseline_agent() -> AgentProfile:
    return AgentProfile(
        agent_id="baseline_agent",
        dimensions=_BASELINE_DIMENSIONS,
        role=Role.IMPLEMENTER,
        game_theory=GameTheoryParams(
            context_sharing="full",
            memory_persistence=False,
            signaling=False,
            conflict_style=ConflictStyle.NEGOTIATE,
        ),
    )


def _load_done_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    done = set()
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    done.add(json.loads(line)["problem_id"])
                except Exception:
                    pass
    return done


def _append_result(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(result) + "\n")


def run_one(problem, dry_run: bool = False) -> dict:
    """Run chain-1 on a single problem. Returns result dict."""
    t0 = time.time()

    if dry_run:
        return {
            "problem_id":        problem.problem_id,
            "difficulty":        problem.difficulty,
            "passed":            False,
            "compilation_error": False,
            "tests_passed":      0,
            "tests_total":       len(problem.private_tests),
            "pass_rate":         0.0,
            "extraction_failed": True,
            "tokens_total":      0,
            "run_id":            "dry-run",
            "elapsed_seconds":   0.0,
            "dry_run":           True,
        }

    prompt = format_prompt(problem)
    agent  = _baseline_agent()

    try:
        state = run_simulation(
            agents=[agent],
            scenario_brief=prompt,
            phase="cp_baseline",
            topology="chain",
        )
    except Exception as e:
        return {
            "problem_id":        problem.problem_id,
            "difficulty":        problem.difficulty,
            "passed":            False,
            "compilation_error": False,
            "tests_passed":      0,
            "tests_total":       len(problem.private_tests),
            "pass_rate":         0.0,
            "extraction_failed": True,
            "tokens_total":      0,
            "run_id":            None,
            "elapsed_seconds":   round(time.time() - t0, 2),
            "error":             str(e),
        }

    tokens_total = sum(state["token_usage"].values())
    transcript   = state["messages"]

    code = extract(transcript, topology="chain", n_agents=1)
    extraction_failed = not bool(code.strip())

    if extraction_failed:
        return {
            "problem_id":        problem.problem_id,
            "difficulty":        problem.difficulty,
            "passed":            False,
            "compilation_error": False,
            "tests_passed":      0,
            "tests_total":       len(problem.private_tests),
            "pass_rate":         0.0,
            "extraction_failed": True,
            "tokens_total":      tokens_total,
            "run_id":            state["run_id"],
            "elapsed_seconds":   round(time.time() - t0, 2),
        }

    eval_result = evaluate(
        code=code,
        test_cases=problem.private_tests,
        time_limit=problem.time_limit,
        max_test_cases=10,
    )

    return {
        "problem_id":        problem.problem_id,
        "difficulty":        problem.difficulty,
        "passed":            eval_result["passed"],
        "compilation_error": eval_result["compilation_error"],
        "tests_passed":      eval_result["tests_passed"],
        "tests_total":       eval_result["tests_total"],
        "pass_rate":         eval_result["pass_rate"],
        "extraction_failed": False,
        "tokens_total":      tokens_total,
        "run_id":            state["run_id"],
        "elapsed_seconds":   round(time.time() - t0, 2),
    }


def print_summary(results: list[dict]) -> None:
    total    = len(results)
    passed   = sum(1 for r in results if r.get("passed"))
    ce       = sum(1 for r in results if r.get("compilation_error"))
    no_code  = sum(1 for r in results if r.get("extraction_failed"))
    avg_pass = sum(r.get("pass_rate", 0) for r in results) / total if total else 0

    print("\n" + "=" * 50)
    print(f"Chain-1 Baseline Summary ({total} problems)")
    print("=" * 50)
    print(f"  Pass@1 (all tests):   {passed}/{total}  ({100*passed/total:.1f}%)")
    print(f"  Avg pass rate:        {100*avg_pass:.1f}%")
    print(f"  Compilation errors:   {ce}")
    print(f"  Extraction failures:  {no_code}")
    print(f"  Results:              {BASELINE_OUT}")


def main():
    parser = argparse.ArgumentParser(description="KalibrBench-CP chain-1 baseline")
    parser.add_argument("--n",        type=int,  default=100,   help="Number of problems")
    parser.add_argument("--dry-run",  action="store_true",      help="Skip API calls; test pipeline only")
    parser.add_argument("--no-judge0-check", action="store_true", help="Skip Judge0 health check")
    args = parser.parse_args()

    if not args.dry_run and not args.no_judge0_check:
        print("Checking Judge0...", end=" ", flush=True)
        if not health_check():
            print("FAILED")
            print("Judge0 is not reachable. Start it with: cd judge0 && docker-compose up -d")
            sys.exit(1)
        print("OK")

    problems = load_problems(n=args.n)
    if not problems:
        print("No problems loaded. Check dataset filters.")
        sys.exit(1)

    done_ids = _load_done_ids(BASELINE_OUT)
    pending  = [p for p in problems if p.problem_id not in done_ids]
    print(f"{len(done_ids)} already done. Running {len(pending)} remaining.")

    session_results = []
    for i, problem in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] {problem.problem_id} (difficulty={problem.difficulty})...", end=" ", flush=True)
        result = run_one(problem, dry_run=args.dry_run)
        _append_result(BASELINE_OUT, result)
        session_results.append(result)

        status = "PASS" if result.get("passed") else (
            "CE"   if result.get("compilation_error") else (
            "NOCODE" if result.get("extraction_failed") else
            f"FAIL {result.get('tests_passed',0)}/{result.get('tests_total',0)}"
        ))
        print(f"{status}  ({result.get('elapsed_seconds', 0):.1f}s, {result.get('tokens_total', 0)} tok)")

    # Print summary over everything in the file, not just this session
    all_results = []
    with BASELINE_OUT.open() as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    all_results.append(json.loads(line))
                except Exception:
                    pass

    print_summary(all_results)


if __name__ == "__main__":
    main()
