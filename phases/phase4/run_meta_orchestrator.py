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
Phase 4: Meta-Orchestrator benchmark.

Mixed dataset: judgment tasks (Phase 1 scenarios) + execution tasks (CP problems).
Three conditions evaluated head-to-head:

    static-judgment  — always deploys judgment config (chain-2 Kalibr profiles)
    static-execution — always deploys execution config (chain-2 generic)
    meta-router      — classifies task domain first, then routes to correct config

Primary question: does dynamic routing recover the performance lost by mismatching
config to task type?

Expected findings:
    - static-judgment  scores well on judgment tasks, poorly on execution
    - static-execution scores poorly on judgment tasks, well on execution
    - meta-router       matches the per-domain winner on each task type

Dataset:
    Judgment: 4 Phase 1 scenarios × 3 runs = 12 tasks (scored 0–100 rubric)
    Execution: 25 CP problems (scored pass@1, binary)
    Total: 37 tasks × 3 conditions = 111 evaluations

Usage:
    python run_meta_orchestrator.py [--judgment-runs 3] [--cp-n 25]

Env vars:
    GEMINI_API_KEY  required
    MODEL           default gemini-2.5-flash
    MODEL_PROVIDER  gemini | anthropic
"""
from __future__ import annotations
import argparse
import json
import os
import re as _re
import sys
import time
import uuid
from pathlib import Path

os.environ.setdefault("AGENT_TOKEN_BUDGET", "8192")

from dotenv import load_dotenv
load_dotenv(override=True)

from src.meta_orchestrator.classifier import classify, DOMAIN_JUDGMENT, DOMAIN_EXECUTION
from src.meta_orchestrator.router import get_judgment_config, get_execution_config
from src.orchestration.engine import run_simulation
from src.evaluation.judge import score_transcript_panel
from src.datasets.codecontests import load_problems, format_prompt, CPProblem
from src.execution.judge0 import evaluate
from src.execution.extractor import extract
from src.scenarios.library import ALL_SCENARIOS

RESULTS_DIR = Path("results")
META_OUT    = RESULTS_DIR / "meta_orchestrator.jsonl"

ALL_CONDITIONS = ["static-judgment", "static-execution", "meta-router"]

# ---------------------------------------------------------------------------
# Transcript builder (mirrors run_simulation.py)
# ---------------------------------------------------------------------------

def _build_transcript(messages) -> str:
    from langchain_core.messages import AIMessage
    lines = []
    for m in messages:
        if isinstance(m, dict):
            role = m.get("role", "unknown")
            content = m.get("content", "")
        elif isinstance(m, AIMessage):
            role = "assistant"
            content = m.content
        else:
            role = "user"
            content = m.content if hasattr(m, "content") else str(m)
        lines.append(f"[{role.upper()}]: {content}")
    return "\n\n".join(lines)


# ---------------------------------------------------------------------------
# Code cleanup (mirrors run_phase3.py)
# ---------------------------------------------------------------------------

def _ensure_callable(code: str) -> str:
    for fname in ("solve", "main"):
        if _re.search(rf'^def {fname}\s*\(', code, _re.MULTILINE):
            if not _re.search(rf'^{fname}\s*\(', code, _re.MULTILINE):
                if '__name__' not in code:
                    return code.rstrip() + f'\n\n{fname}()\n'
    return code


# ---------------------------------------------------------------------------
# Config resolution
# ---------------------------------------------------------------------------

def _resolve_config(condition: str, prompt: str) -> tuple[dict, str]:
    """Return (agent_config, actual_domain). actual_domain is the domain used."""
    if condition == "static-judgment":
        return get_judgment_config(), DOMAIN_JUDGMENT
    if condition == "static-execution":
        return get_execution_config(), DOMAIN_EXECUTION
    # meta-router: classify and route
    domain = classify(prompt)
    if domain == DOMAIN_EXECUTION:
        return get_execution_config(), DOMAIN_EXECUTION
    return get_judgment_config(), DOMAIN_JUDGMENT


# ---------------------------------------------------------------------------
# Resumability
# ---------------------------------------------------------------------------

def _load_done() -> set[str]:
    done: set[str] = set()
    if not META_OUT.exists():
        return done
    with META_OUT.open() as f:
        for line in f:
            try:
                rec = json.loads(line)
                done.add(f"{rec['condition']}::{rec['task_id']}")
            except Exception:
                pass
    return done


def _append(rec: dict) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    with META_OUT.open("a") as f:
        f.write(json.dumps(rec) + "\n")


# ---------------------------------------------------------------------------
# Judgment task runner
# ---------------------------------------------------------------------------

def run_judgment_task(
    condition: str,
    scenario_id: str,
    run_index: int,
) -> dict:
    scenario = ALL_SCENARIOS[scenario_id]
    task_id  = f"{scenario_id}/run{run_index}"
    run_id   = str(uuid.uuid4())

    cfg, routed_domain = _resolve_config(condition, scenario.brief)
    agents             = cfg["agents"]
    handoff_prompts    = cfg.get("handoff_prompts")

    classifier_call = condition == "meta-router"

    try:
        state = run_simulation(
            agents=agents,
            scenario_brief=scenario.brief,
            phase=scenario.phase,
            topology="chain",
            flat_rounds=2,
            chain_handoff_prompts=handoff_prompts,
        )
    except Exception as e:
        return {
            "run_id":        run_id,
            "condition":     condition,
            "task_id":       task_id,
            "task_type":     DOMAIN_JUDGMENT,
            "routed_domain": routed_domain,
            "routed_correct": routed_domain == DOMAIN_JUDGMENT,
            "classifier_called": classifier_call,
            "task_score":    0.0,
            "passed":        None,
            "error":         str(e),
        }

    transcript = _build_transcript(state["messages"])
    judge_error = None
    try:
        evals = score_transcript_panel(
            run_id=run_id,
            phase=scenario.phase,
            transcript=transcript,
            rubric=scenario.rubric,
            n_judges=3,
            topology="chain",
            team_size=len(agents),
        )
        task_score = sum(e.task_score for e in evals) / len(evals)
    except Exception as e:
        task_score = None
        judge_error = str(e)

    return {
        "run_id":           run_id,
        "condition":        condition,
        "task_id":          task_id,
        "task_type":        DOMAIN_JUDGMENT,
        "routed_domain":    routed_domain,
        "routed_correct":   routed_domain == DOMAIN_JUDGMENT,
        "classifier_called": classifier_call,
        "task_score":       task_score,
        "passed":           None,
        **({"error": judge_error} if judge_error else {}),
    }


# ---------------------------------------------------------------------------
# Execution task runner
# ---------------------------------------------------------------------------

def run_execution_task(
    condition: str,
    problem: CPProblem,
) -> dict:
    task_id  = problem.problem_id
    run_id   = str(uuid.uuid4())
    prompt   = format_prompt(problem)

    cfg, routed_domain = _resolve_config(condition, prompt)
    agents             = cfg["agents"]
    handoff_prompts    = cfg.get("handoff_prompts")

    classifier_call = condition == "meta-router"

    try:
        state = run_simulation(
            agents=agents,
            scenario_brief=prompt,
            phase="phase4",
            topology="chain",
            flat_rounds=2,
            chain_handoff_prompts=handoff_prompts,
        )
    except Exception as e:
        return {
            "run_id":           run_id,
            "condition":        condition,
            "task_id":          task_id,
            "task_type":        DOMAIN_EXECUTION,
            "routed_domain":    routed_domain,
            "routed_correct":   routed_domain == DOMAIN_EXECUTION,
            "classifier_called": classifier_call,
            "task_score":       None,
            "passed":           False,
            "compilation_error": False,
            "pass_rate":        0.0,
            "nocode":           False,
            "error":            str(e),
        }

    code = extract(state["messages"], topology="chain", n_agents=len(agents))
    code = _ensure_callable(code)
    nocode = not code.strip()

    if nocode:
        result = {"passed": False, "compilation_error": False, "pass_rate": 0.0,
                  "tests_passed": 0, "tests_total": 0}
    else:
        result = evaluate(code, problem.private_tests, time_limit=problem.time_limit)

    return {
        "run_id":           run_id,
        "condition":        condition,
        "task_id":          task_id,
        "task_type":        DOMAIN_EXECUTION,
        "routed_domain":    routed_domain,
        "routed_correct":   routed_domain == DOMAIN_EXECUTION,
        "classifier_called": classifier_call,
        "task_score":       None,
        "passed":           result["passed"],
        "compilation_error": result["compilation_error"],
        "pass_rate":        result.get("pass_rate", 0.0),
        "tests_passed":     result.get("tests_passed", 0),
        "tests_total":      result.get("tests_total", 0),
        "nocode":           nocode,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Phase 4: Meta-Orchestrator benchmark")
    parser.add_argument("--judgment-runs", type=int, default=3,
                        help="Runs per judgment scenario (default 3)")
    parser.add_argument("--cp-n",          type=int, default=25,
                        help="CP problems to include (default 25)")
    parser.add_argument("--conditions",    nargs="+", default=ALL_CONDITIONS,
                        choices=ALL_CONDITIONS, help="Conditions to run")
    args = parser.parse_args()

    done = _load_done()
    print(f"Already completed: {len(done)} runs\n")

    # Build judgment task list
    judgment_tasks: list[tuple[str, int]] = []
    for sid in sorted(ALL_SCENARIOS.keys()):
        for run_idx in range(args.judgment_runs):
            judgment_tasks.append((sid, run_idx))

    # Load CP problems
    print(f"Loading {args.cp_n} CP problems...")
    cp_problems = load_problems(n=args.cp_n)
    print(f"Loaded {len(cp_problems)} CP problems\n")

    total = len(args.conditions) * (len(judgment_tasks) + len(cp_problems))
    completed = 0

    for condition in args.conditions:
        print(f"{'=' * 60}")
        print(f"CONDITION: {condition}")
        print(f"{'=' * 60}")

        # --- Judgment tasks ---
        print(f"\n  [JUDGMENT — {len(judgment_tasks)} tasks]\n")
        for scenario_id, run_idx in judgment_tasks:
            task_id = f"{scenario_id}/run{run_idx}"
            key = f"{condition}::{task_id}"
            completed += 1
            if key in done:
                print(f"  [{completed}/{total}] {task_id} — skip")
                continue

            rec = run_judgment_task(condition, scenario_id, run_idx)
            _append(rec)
            done.add(key)

            score_str = f"{rec['task_score']:.1f}" if rec.get("task_score") is not None else "ERR"
            routed    = rec.get("routed_domain", "?")
            correct   = "✓" if rec.get("routed_correct") else "✗"
            print(f"  [{completed}/{total}] {task_id} — score={score_str}  routed={routed}{correct}")
            time.sleep(0.1)

        # --- Execution tasks ---
        print(f"\n  [EXECUTION — {len(cp_problems)} tasks]\n")
        for i, prob in enumerate(cp_problems):
            key = f"{condition}::{prob.problem_id}"
            completed += 1
            if key in done:
                print(f"  [{completed}/{total}] {prob.problem_id} — skip")
                continue

            rec = run_execution_task(condition, prob)
            _append(rec)
            done.add(key)

            status = "PASS" if rec["passed"] else ("CE" if rec.get("compilation_error") else ("NC" if rec.get("nocode") else "FAIL"))
            routed  = rec.get("routed_domain", "?")
            correct = "✓" if rec.get("routed_correct") else "✗"
            print(f"  [{completed}/{total}] {prob.problem_id} — {status}  routed={routed}{correct}")
            time.sleep(0.1)

        print()

    print(f"\n{'=' * 60}")
    print("Phase 4 complete.")
    print(f"Results written to {META_OUT}")


if __name__ == "__main__":
    main()
