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
KalibrBench-CP: main experiment runner.

Conditions (topology × constitution):
  chain-1 × generic     — single balanced IMPLEMENTER (reference; matches run_cp_baseline.py)
  chain-2 × generic     — two balanced agents, second synthesises
  chain-2 × specialized — ALGORITHMIST → IMPLEMENTER, role-specialised constitutions

Results are written incrementally to results/cp_experiment.jsonl and synced
to Supabase cp_runs (if DATABASE_URL is set).

Usage:
    GEMINI_API_KEY=... python run_cp_experiment.py [--n 100] [--conditions chain2-generic chain2-specialized]

Env vars:
    GEMINI_API_KEY / ANTHROPIC_API_KEY
    MODEL                  (default: gemini-2.5-flash)
    MODEL_PROVIDER         gemini | anthropic (default: gemini)
    JUDGE0_URL             (default: http://localhost:2358)
    AGENT_TOKEN_BUDGET     (default: 4096)
    DATABASE_URL           Supabase connection string (optional — skipped if unset)
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

os.environ.setdefault("AGENT_TOKEN_BUDGET", "4096")

from dotenv import load_dotenv
load_dotenv()

from src.agents.profile import AgentProfile, KalibrDimensions, GameTheoryParams, Role, ConflictStyle
from src.datasets.codecontests import load_problems, format_prompt
from src.execution.judge0 import evaluate, health_check
from src.execution.extractor import extract
from src.orchestration.engine import run_simulation

RESULTS_DIR  = Path("results")
EXPERIMENT_OUT = RESULTS_DIR / "cp_experiment.jsonl"

_MODEL_FAMILY = os.getenv("MODEL_PROVIDER", "gemini")

# ---------------------------------------------------------------------------
# Agent profiles
# ---------------------------------------------------------------------------

def _generic_agent(agent_id: str, role: Role = Role.IMPLEMENTER) -> AgentProfile:
    """Balanced, unspecialized profile matching the Phase 1 research baseline."""
    return AgentProfile(
        agent_id=agent_id,
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
        role=role,
        game_theory=GameTheoryParams(
            context_sharing="full",
            memory_persistence=False,
            signaling=False,
            conflict_style=ConflictStyle.NEGOTIATE,
        ),
    )


def _algorithmist_agent() -> AgentProfile:
    """Specialized: analytical, pattern-matching, forward-planning. Designs; does not code."""
    return AgentProfile(
        agent_id="algorithmist",
        dimensions=KalibrDimensions(
            philosophy_cohesion=85,   # reasoning must match design decisions
            drive_alignment=80,       # holds direction through long analysis
            bonding_index=45,         # functional handoff, not collaborative warmth
            adaptive_intelligence=90, # updates approach immediately on constraint discovery
            volatility_vector=30,     # flat affect; pressure doesn't change the math
            ambiguity_tolerance=60,   # tolerates partial specs but pushes for constraints
            influence_style=60,       # persuasive: makes the case for the chosen algorithm
            feedback_orientation=80,  # integrates implementer feedback on feasibility
            temporal_orientation=75,  # future-oriented: evaluates decisions by downstream cost
            energy_resilience=85,     # sustained precision across long problem analyses
        ),
        role=Role.ALGORITHMIST,
        game_theory=GameTheoryParams(
            context_sharing="full",
            memory_persistence=False,
            signaling=False,
            conflict_style=ConflictStyle.CHALLENGE,
        ),
    )


def _implementer_agent() -> AgentProfile:
    """Specialized: execution-focused, translates algorithm spec to clean Python."""
    return AgentProfile(
        agent_id="implementer",
        dimensions=KalibrDimensions(
            philosophy_cohesion=80,   # code must match what was stated
            drive_alignment=85,       # locks onto the spec and executes without drift
            bonding_index=55,         # reads and respects the algorithmist's output
            adaptive_intelligence=70, # updates on edge cases surfaced during coding
            volatility_vector=40,     # low reactivity; bugs are problems to solve, not crises
            ambiguity_tolerance=30,   # requests specificity; does not assume
            influence_style=35,       # defers on algorithm; asserts only on implementation detail
            feedback_orientation=85,  # integrates critique without defensiveness
            temporal_orientation=45,  # present-focused: the task is to make this run correctly
            energy_resilience=80,     # output quality holds over long code generation turns
        ),
        role=Role.IMPLEMENTER,
        game_theory=GameTheoryParams(
            context_sharing="full",
            memory_persistence=False,
            signaling=False,
            conflict_style=ConflictStyle.NEGOTIATE,
        ),
    )


# ---------------------------------------------------------------------------
# Condition definitions
# ---------------------------------------------------------------------------

ALL_CONDITIONS = {
    "chain1-generic": {
        "topology":   "chain",
        "label":      "chain-1",
        "condition":  "generic",
        "agents_fn":  lambda: [_generic_agent("agent_1")],
    },
    "chain2-generic": {
        "topology":   "chain",
        "label":      "chain-2",
        "condition":  "generic",
        "agents_fn":  lambda: [_generic_agent("agent_1"), _generic_agent("agent_2")],
    },
    "chain2-specialized": {
        "topology":   "chain",
        "label":      "chain-2",
        "condition":  "specialized",
        "agents_fn":  lambda: [_algorithmist_agent(), _implementer_agent()],
    },
}


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def _load_done_keys(path: Path) -> set[tuple]:
    """Return set of (problem_id, label, condition) already in the output file."""
    if not path.exists():
        return set()
    done = set()
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    r = json.loads(line)
                    done.add((r["problem_id"], r["topology"], r["condition"]))
                except Exception:
                    pass
    return done


def _append_result(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(result) + "\n")


def _try_supabase(result: dict) -> None:
    if not os.getenv("DATABASE_URL"):
        return
    try:
        from src.telemetry.database_cp import insert_cp_run
        insert_cp_run(
            run_id=result["run_id"],
            problem_id=result["problem_id"],
            difficulty=result["difficulty"],
            topology=result["topology"],
            condition=result["condition"],
            passed=result["passed"],
            compilation_error=result["compilation_error"],
            tests_passed=result["tests_passed"],
            tests_total=result["tests_total"],
            pass_rate=result["pass_rate"],
            extraction_failed=result["extraction_failed"],
            tokens_total=result["tokens_total"],
            elapsed_seconds=result.get("elapsed_seconds"),
            model_family=_MODEL_FAMILY,
        )
    except Exception as e:
        print(f"  [supabase warn] {e}")


# ---------------------------------------------------------------------------
# Single run
# ---------------------------------------------------------------------------

def run_one(problem, cond_cfg: dict) -> dict:
    t0       = time.time()
    topology = cond_cfg["topology"]
    label    = cond_cfg["label"]
    condition = cond_cfg["condition"]
    agents   = cond_cfg["agents_fn"]()
    n_agents = len(agents)

    prompt = format_prompt(problem)

    try:
        state = run_simulation(
            agents=agents,
            scenario_brief=prompt,
            phase="cp_experiment",
            topology=topology,
        )
    except Exception as e:
        return {
            "run_id":            str(uuid.uuid4()),
            "problem_id":        problem.problem_id,
            "difficulty":        problem.difficulty,
            "topology":          label,
            "condition":         condition,
            "passed":            False,
            "compilation_error": False,
            "tests_passed":      0,
            "tests_total":       len(problem.private_tests),
            "pass_rate":         0.0,
            "extraction_failed": True,
            "tokens_total":      0,
            "elapsed_seconds":   round(time.time() - t0, 2),
            "error":             str(e),
        }

    tokens_total = sum(state["token_usage"].values())
    code = extract(state["messages"], topology=topology, n_agents=n_agents)
    extraction_failed = not bool(code.strip())

    if extraction_failed:
        return {
            "run_id":            state["run_id"],
            "problem_id":        problem.problem_id,
            "difficulty":        problem.difficulty,
            "topology":          label,
            "condition":         condition,
            "passed":            False,
            "compilation_error": False,
            "tests_passed":      0,
            "tests_total":       len(problem.private_tests),
            "pass_rate":         0.0,
            "extraction_failed": True,
            "tokens_total":      tokens_total,
            "elapsed_seconds":   round(time.time() - t0, 2),
        }

    eval_result = evaluate(
        code=code,
        test_cases=problem.private_tests,
        time_limit=problem.time_limit,
        max_test_cases=10,
    )

    return {
        "run_id":            state["run_id"],
        "problem_id":        problem.problem_id,
        "difficulty":        problem.difficulty,
        "topology":          label,
        "condition":         condition,
        "passed":            eval_result["passed"],
        "compilation_error": eval_result["compilation_error"],
        "tests_passed":      eval_result["tests_passed"],
        "tests_total":       eval_result["tests_total"],
        "pass_rate":         eval_result["pass_rate"],
        "extraction_failed": False,
        "tokens_total":      tokens_total,
        "elapsed_seconds":   round(time.time() - t0, 2),
    }


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary(results: list[dict]) -> None:
    from collections import defaultdict
    groups = defaultdict(list)
    for r in results:
        groups[(r["topology"], r["condition"])].append(r)

    print("\n" + "=" * 60)
    print("KalibrBench-CP Experiment Summary")
    print("=" * 60)
    print(f"{'Topology':<12} {'Condition':<14} {'Pass@1':>8} {'AvgRate':>9} {'CE':>5} {'NoCode':>7} {'N':>5}")
    print("-" * 60)

    for (topo, cond), rs in sorted(groups.items()):
        n       = len(rs)
        passed  = sum(1 for r in rs if r.get("passed"))
        ce      = sum(1 for r in rs if r.get("compilation_error"))
        nocode  = sum(1 for r in rs if r.get("extraction_failed"))
        avg_pr  = sum(r.get("pass_rate", 0) for r in rs) / n if n else 0
        print(f"{topo:<12} {cond:<14} {passed:>5}/{n:<3} {100*avg_pr:>8.1f}% {ce:>5} {nocode:>7}")

    print("=" * 60)
    print(f"Full results: {EXPERIMENT_OUT}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="KalibrBench-CP experiment runner")
    parser.add_argument("--n", type=int, default=100, help="Number of problems per condition")
    parser.add_argument(
        "--conditions", nargs="+",
        choices=list(ALL_CONDITIONS.keys()),
        default=list(ALL_CONDITIONS.keys()),
        help="Which conditions to run (default: all)",
    )
    parser.add_argument("--no-judge0-check", action="store_true")
    args = parser.parse_args()

    if not args.no_judge0_check:
        print("Checking Judge0...", end=" ", flush=True)
        if not health_check():
            print("FAILED")
            print("Start Judge0: cd judge0 && docker-compose up -d")
            sys.exit(1)
        print("OK")

    problems = load_problems(n=args.n)
    if not problems:
        print("No problems loaded.")
        sys.exit(1)

    done_keys = _load_done_keys(EXPERIMENT_OUT)
    print(f"{len(done_keys)} (problem, topology, condition) combinations already done.")

    for cond_name in args.conditions:
        cond_cfg = ALL_CONDITIONS[cond_name]
        label    = cond_cfg["label"]
        condition = cond_cfg["condition"]

        pending = [
            p for p in problems
            if (p.problem_id, label, condition) not in done_keys
        ]
        print(f"\n[{cond_name}] {len(pending)} remaining / {len(problems)} total")

        for i, problem in enumerate(pending, 1):
            print(
                f"  [{i}/{len(pending)}] {problem.problem_id} (d={problem.difficulty})...",
                end=" ", flush=True,
            )
            result = run_one(problem, cond_cfg)
            _append_result(EXPERIMENT_OUT, result)
            done_keys.add((result["problem_id"], result["topology"], result["condition"]))
            _try_supabase(result)

            status = "PASS" if result.get("passed") else (
                "CE"     if result.get("compilation_error") else (
                "NOCODE" if result.get("extraction_failed") else
                f"FAIL {result.get('tests_passed',0)}/{result.get('tests_total',0)}"
            ))
            tok = result.get("tokens_total", 0)
            sec = result.get("elapsed_seconds", 0)
            print(f"{status}  ({sec:.1f}s, {tok} tok)")

    all_results = []
    with EXPERIMENT_OUT.open() as f:
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
