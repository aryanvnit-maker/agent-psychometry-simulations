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

Two decoupled phases to avoid running Gemini API calls and Judge0 Docker
simultaneously (CPU thermal management):

  Phase A — collect agent responses (Gemini API only, Docker idle):
      python run_cp_baseline.py --collect-only

  Phase B — evaluate collected code via Judge0 (Docker active, no API calls):
      python run_cp_baseline.py --evaluate-only

  Combined (original behaviour, not recommended on constrained hardware):
      python run_cp_baseline.py

Phase A writes to results/cp_baseline_collected.jsonl (code + metadata).
Phase B reads that file, evaluates via Judge0, writes final results to
results/cp_baseline.jsonl (same schema consumed by analyze_cp.py).
Both phases are fully resumable.
"""
from __future__ import annotations
import argparse
import json
import os
import re as _re
import sys
import time
from pathlib import Path

os.environ.setdefault("AGENT_TOKEN_BUDGET", "8192")

from dotenv import load_dotenv
load_dotenv()

from src.agents.profile import AgentProfile, KalibrDimensions, GameTheoryParams, Role, ConflictStyle
from src.datasets.codecontests import load_problems, format_prompt
from src.execution.judge0 import evaluate, run_test_case, health_check
from src.execution.extractor import extract, _msg_content
from src.orchestration.engine import run_simulation

RESULTS_DIR       = Path("results")
COLLECTED_OUT     = RESULTS_DIR / "cp_baseline_collected.jsonl"
BASELINE_OUT      = RESULTS_DIR / "cp_baseline.jsonl"

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
        role=Role.SOLVER,
        game_theory=GameTheoryParams(
            context_sharing="full",
            memory_persistence=False,
            signaling=False,
            conflict_style=ConflictStyle.NEGOTIATE,
        ),
    )


def _ensure_callable(code: str) -> str:
    """Append a top-level call if solve()/main() is defined but never invoked."""
    for fname in ("solve", "main"):
        if _re.search(rf'^def {fname}\s*\(', code, _re.MULTILINE):
            if not _re.search(rf'^{fname}\s*\(', code, _re.MULTILINE):
                if '__name__' not in code:
                    return code.rstrip() + f'\n\n{fname}()\n'
    return code


def _load_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids = set()
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    ids.add(json.loads(line)["problem_id"])
                except Exception:
                    pass
    return ids


def _append(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(record) + "\n")


# ---------------------------------------------------------------------------
# Phase A — collect
# ---------------------------------------------------------------------------

def collect_one(problem) -> dict:
    """Call Gemini, extract code, return record. No Judge0."""
    t0 = time.time()
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
            "private_tests":     problem.private_tests,
            "time_limit":        problem.time_limit,
            "code":              "",
            "extraction_failed": True,
            "tokens_total":      0,
            "run_id":            None,
            "elapsed_seconds":   round(time.time() - t0, 2),
            "error":             str(e),
        }

    tokens_total = sum(state["token_usage"].values())
    code = extract(state["messages"], topology="chain", n_agents=1)

    extraction_failed = not bool(code.strip())

    return {
        "problem_id":        problem.problem_id,
        "difficulty":        problem.difficulty,
        "private_tests":     problem.private_tests,
        "time_limit":        problem.time_limit,
        "code":              code,
        "extraction_failed": extraction_failed,
        "tokens_total":      tokens_total,
        "run_id":            state["run_id"],
        "elapsed_seconds":   round(time.time() - t0, 2),
    }


def run_collect(n: int) -> None:
    problems   = load_problems(n=n)
    done_ids   = _load_ids(COLLECTED_OUT)
    pending    = [p for p in problems if p.problem_id not in done_ids]
    print(f"{len(done_ids)} already collected. Collecting {len(pending)} remaining.")

    for i, problem in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] {problem.problem_id}...", end=" ", flush=True)
        record = collect_one(problem)
        _append(COLLECTED_OUT, record)

        status = "NOCODE" if record["extraction_failed"] else f"OK ({len(record['code'])} chars)"
        print(f"{status}  ({record['elapsed_seconds']:.1f}s, {record['tokens_total']} tok)")

    print(f"\nCollection done. {COLLECTED_OUT}")
    print("Run `python run_cp_baseline.py --evaluate-only` when ready.")


# ---------------------------------------------------------------------------
# Phase B — evaluate
# ---------------------------------------------------------------------------

def run_evaluate() -> None:
    if not COLLECTED_OUT.exists():
        print("No collected data found. Run --collect-only first.")
        sys.exit(1)

    print("Checking Judge0...", end=" ", flush=True)
    if not health_check():
        print("FAILED")
        print("Start Judge0: cd judge0 && docker-compose up -d")
        sys.exit(1)
    print("OK")

    collected = []
    with COLLECTED_OUT.open() as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    collected.append(json.loads(line))
                except Exception:
                    pass

    done_ids = _load_ids(BASELINE_OUT)
    pending  = [r for r in collected if r["problem_id"] not in done_ids]
    print(f"{len(done_ids)} already evaluated. Evaluating {len(pending)} remaining.")

    for i, record in enumerate(pending, 1):
        pid = record["problem_id"]
        print(f"[{i}/{len(pending)}] {pid}...", end=" ", flush=True)

        if record.get("extraction_failed") or not record.get("code", "").strip():
            result = {
                "problem_id":        pid,
                "difficulty":        record["difficulty"],
                "passed":            False,
                "compilation_error": False,
                "tests_passed":      0,
                "tests_total":       len(record.get("private_tests", [])),
                "pass_rate":         0.0,
                "extraction_failed": True,
                "tokens_total":      record.get("tokens_total", 0),
                "run_id":            record.get("run_id"),
                "elapsed_seconds":   record.get("elapsed_seconds"),
            }
            print("NOCODE")
        else:
            t0 = time.time()
            code = _ensure_callable(record["code"])
            try:
                eval_result = evaluate(
                    code=code,
                    test_cases=record["private_tests"],
                    time_limit=record.get("time_limit", 5.0),
                    max_test_cases=10,
                )
            except Exception as e:
                print(f"ERROR ({e})")
                _append(BASELINE_OUT, {
                    "problem_id":        pid,
                    "difficulty":        record["difficulty"],
                    "passed":            False,
                    "compilation_error": False,
                    "tests_passed":      0,
                    "tests_total":       len(record.get("private_tests", [])),
                    "pass_rate":         0.0,
                    "extraction_failed": False,
                    "tokens_total":      record.get("tokens_total", 0),
                    "run_id":            record.get("run_id"),
                    "elapsed_seconds":   record.get("elapsed_seconds"),
                    "eval_error":        str(e),
                })
                continue
            result = {
                "problem_id":        pid,
                "difficulty":        record["difficulty"],
                "passed":            eval_result["passed"],
                "compilation_error": eval_result["compilation_error"],
                "tests_passed":      eval_result["tests_passed"],
                "tests_total":       eval_result["tests_total"],
                "pass_rate":         eval_result["pass_rate"],
                "extraction_failed": False,
                "tokens_total":      record.get("tokens_total", 0),
                "run_id":            record.get("run_id"),
                "elapsed_seconds":   record.get("elapsed_seconds"),
                "eval_seconds":      round(time.time() - t0, 2),
            }
            status = "PASS" if result["passed"] else (
                "CE" if result["compilation_error"] else
                f"FAIL {result['tests_passed']}/{result['tests_total']}"
            )
            print(f"{status}  ({result['eval_seconds']:.1f}s)")

            # Diagnostic: for first 5 all-zero failures, show Judge0 detail on first test case
            if result["tests_passed"] == 0 and not result["compilation_error"] and i <= 5:
                tc = record["private_tests"][0]
                dr = run_test_case(code, tc["input"], tc["output"], record.get("time_limit", 5.0))
                print(f"    [diag] status={dr.get('status_id')} "
                      f"stdout={dr.get('stdout','')[:120]!r} "
                      f"stderr={dr.get('stderr','')[:120]!r}")

        _append(BASELINE_OUT, result)

    print_summary()


# ---------------------------------------------------------------------------
# Summary + combined mode
# ---------------------------------------------------------------------------

def print_summary() -> None:
    results = []
    if BASELINE_OUT.exists():
        with BASELINE_OUT.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        results.append(json.loads(line))
                    except Exception:
                        pass

    total    = len(results)
    passed   = sum(1 for r in results if r.get("passed"))
    ce       = sum(1 for r in results if r.get("compilation_error"))
    no_code  = sum(1 for r in results if r.get("extraction_failed"))
    avg_pass = sum(r.get("pass_rate", 0) for r in results) / total if total else 0

    print("\n" + "=" * 50)
    print(f"Chain-1 Baseline Summary ({total} problems)")
    print("=" * 50)
    print(f"  Pass@1 (all tests):   {passed}/{total}  ({100*passed/total:.1f}%)" if total else "  No results yet.")
    print(f"  Avg pass rate:        {100*avg_pass:.1f}%")
    print(f"  Compilation errors:   {ce}")
    print(f"  Extraction failures:  {no_code}")
    print(f"  Results:              {BASELINE_OUT}")


def main():
    parser = argparse.ArgumentParser(description="KalibrBench-CP chain-1 baseline")
    parser.add_argument("--n", type=int, default=100)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--collect-only",  action="store_true", help="Phase A: Gemini API only, no Judge0")
    mode.add_argument("--evaluate-only", action="store_true", help="Phase B: Judge0 only, no API calls")
    args = parser.parse_args()

    if args.collect_only:
        run_collect(args.n)
    elif args.evaluate_only:
        run_evaluate()
    else:
        # Combined — original behaviour
        print("Checking Judge0...", end=" ", flush=True)
        if not health_check():
            print("FAILED\nStart Judge0: cd judge0 && docker-compose up -d")
            sys.exit(1)
        print("OK")
        run_collect(args.n)
        run_evaluate()


if __name__ == "__main__":
    main()
