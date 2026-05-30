#!/usr/bin/env python3
# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Phase 6: Objective Benchmark — GSM8K (Math Reasoning).

Tests whether chain topology outperforms flat on grade-school math.
Scoring is deterministic: exact numerical answer match. No LLM judge.

Same 4 conditions as run_humaneval.py, same design principles.

Usage:
    python phases/phase6/run_gsm8k.py
    python phases/phase6/run_gsm8k.py --n-problems 100

Output: results/gsm8k.jsonl
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
import traceback
import uuid
from pathlib import Path

os.environ.setdefault("AGENT_TOKEN_BUDGET", "1200")

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.pool import initialise_pool
from src.agents.team import draft_team
from src.orchestration.engine import run_simulation
from src.scenarios.gsm8k import load_problems, extract_answer, answers_match

RESULTS_FILE = Path("results/gsm8k.jsonl")
SEED         = 88
FLAT_ROUNDS  = 2
DELAY_SECS   = 2

MATH_SYNTHESIS_PROMPT = (
    "OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN.\n"
    "You are the terminal synthesis agent in a sequential reasoning chain.\n"
    "Review the prior reasoning above. Verify each step carefully. Correct any errors.\n"
    "Show your final verified solution, then end with:\n"
    "#### [number]\n"
    "where [number] is your final numerical answer — digits only, no units, no commas."
)

MATH_CLOSING_PROMPT = (
    "OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN.\n"
    "Based on all reasoning above, produce the final verified answer.\n"
    "Check the arithmetic. Then end with:\n"
    "#### [number]\n"
    "where [number] is the final numerical answer — digits only, no units, no commas."
)

TASK_DIMS = ["adaptive_intelligence", "ambiguity_tolerance", "drive_alignment"]

CONDITIONS = {
    "single-agent": {
        "topology":      "chain",
        "team_size":     1,
        "chain_handoff_prompts": None,
        "default_handoff": None,
        "closing_prompt": None,
        "captain_last":  False,
    },
    "kalibr-chain": {
        "topology":      "chain",
        "team_size":     2,
        "chain_handoff_prompts": {1: MATH_SYNTHESIS_PROMPT},
        "default_handoff": None,
        "closing_prompt": None,
        "captain_last":  True,
    },
    "kalibr-flat-handoff": {
        "topology":      "flat",
        "team_size":     2,
        "chain_handoff_prompts": None,
        "default_handoff": None,
        "closing_prompt": MATH_CLOSING_PROMPT,
        "captain_last":  False,
    },
    "kalibr-flat-no-handoff": {
        "topology":      "flat",
        "team_size":     2,
        "chain_handoff_prompts": None,
        "default_handoff": None,
        "closing_prompt": None,
        "captain_last":  False,
    },
}


def _msg_content(m) -> str:
    if isinstance(m, dict):
        return m.get("content", "")
    return m.content if hasattr(m, "content") else str(m)


def _is_assistant(m) -> bool:
    if isinstance(m, dict):
        return m.get("role") == "assistant"
    from langchain_core.messages import AIMessage
    return isinstance(m, AIMessage)


def get_final_output(state: dict, topology: str, team_size: int) -> str:
    assistant_msgs = [m for m in state["messages"] if _is_assistant(m)]
    if not assistant_msgs:
        return ""
    if topology == "flat" and team_size > 1:
        last = _msg_content(assistant_msgs[-1])
        if "_synthesis]:" in last:
            return last
        return "\n\n".join(_msg_content(m) for m in assistant_msgs[-team_size:])
    return _msg_content(assistant_msgs[-1])


def _load_done() -> set[str]:
    done: set[str] = set()
    if not RESULTS_FILE.exists():
        return done
    with RESULTS_FILE.open() as f:
        for line in f:
            try:
                rec = json.loads(line)
                done.add(f"{rec['condition']}::{rec['problem_id']}")
            except Exception:
                pass
    return done


def _append(rec: dict) -> None:
    RESULTS_FILE.parent.mkdir(exist_ok=True)
    with RESULTS_FILE.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def run_one(condition_name: str, cond: dict, problem, rep_seed: int) -> dict | None:
    run_id = str(uuid.uuid4())

    pool    = initialise_pool(seed=rep_seed)
    workers = [a for a in pool if not a.is_judge]

    team, captain_id = draft_team(workers, cond["team_size"], TASK_DIMS, "drafted")

    if cond["captain_last"] and len(team) > 1:
        team = list(reversed(team))

    try:
        state = run_simulation(
            agents=team,
            scenario_brief=problem.brief,
            phase="performing",
            topology=cond["topology"],
            flat_rounds=FLAT_ROUNDS,
            chain_handoff_prompts=cond["chain_handoff_prompts"],
            default_handoff=cond["default_handoff"],
            closing_prompt=cond["closing_prompt"],
        )
    except Exception as e:
        print(f"    ERROR in simulation: {e}")
        traceback.print_exc()
        return None

    final_output    = get_final_output(state, cond["topology"], cond["team_size"])
    predicted       = extract_answer(final_output)
    correct         = answers_match(predicted, problem.answer_value)

    return {
        "run_id":         run_id,
        "condition":      condition_name,
        "topology":       cond["topology"],
        "team_size":      cond["team_size"],
        "problem_id":     problem.problem_id,
        "correct":        correct,
        "predicted":      predicted,
        "expected":       problem.answer_value,
        "turn_count":     state["turn_count"],
        "cull_events":    state["cull_events"],
    }


def main():
    parser = argparse.ArgumentParser(description="Phase 6: GSM8K objective benchmark")
    parser.add_argument("--n-problems", type=int, default=100)
    parser.add_argument("--conditions", nargs="+", default=list(CONDITIONS.keys()),
                        choices=list(CONDITIONS.keys()))
    args = parser.parse_args()

    problems  = load_problems(n=args.n_problems, seed=SEED)
    done      = _load_done()
    total     = len(args.conditions) * len(problems)
    completed = 0

    print(f"Phase 6: GSM8K Objective Benchmark")
    print(f"Conditions:  {args.conditions}")
    print(f"Problems:    {len(problems)}")
    print(f"Total runs:  {total}")
    print(f"Already done: {len(done)}")
    print("=" * 60)

    for cond_name in args.conditions:
        cond = CONDITIONS[cond_name]
        print(f"\n=== {cond_name} ===")
        for problem in problems:
            key = f"{cond_name}::{problem.problem_id}"
            completed += 1

            if key in done:
                print(f"  [{completed}/{total}] {problem.problem_id} — SKIP")
                continue

            print(f"  [{completed}/{total}] {problem.problem_id} ...", end="", flush=True)
            rec = run_one(cond_name, cond, problem, rep_seed=SEED + completed)
            if rec is None:
                print(" ERROR")
                continue

            _append(rec)
            done.add(key)
            status = "CORRECT" if rec["correct"] else f"WRONG (got {rec['predicted']}, expected {rec['expected']})"
            print(f" {status}")
            time.sleep(DELAY_SECS)

    print(f"\n{'='*60}")
    print(f"Done. Results in {RESULTS_FILE}")


if __name__ == "__main__":
    main()
