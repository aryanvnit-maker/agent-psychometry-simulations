#!/usr/bin/env python3
# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Phase B: Real-World Task Coverage — Code Review.

Tests whether the topology finding from Phase 1 (chain > flat) replicates on
real-world code review tasks. This extends Phase 1's 4 synthetic judgment
scenarios to a concrete engineering domain.

Each scenario presents a code diff with exactly 3 planted bugs. Rubrics
score 30+30+20+20 based on whether each specific bug was identified.

Conditions:
    chain-2   — sequential chain (Phase 1 winner config)
    flat-2    — flat round-table (Phase 1 loser config)

Usage:
    python phases/phase_b/run_code_review.py
    python phases/phase_b/run_code_review.py --reps 5

Output: results/code_review.jsonl
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

os.environ.setdefault("AGENT_TOKEN_BUDGET", "1200")  # larger budget for code review

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.pool import initialise_pool
from src.orchestration.engine import run_simulation
from src.evaluation.judge import score_transcript_panel
from src.scenarios.code_review import ALL_CODE_REVIEW_SCENARIOS

RESULTS_FILE = Path("results/code_review.jsonl")
SEED         = 99
FLAT_ROUNDS  = 2
DELAY_SECS   = 3

SYNTHESIS_HANDOFF = (
    "Based on the analysis above, synthesize a complete final code review. "
    "List every bug found with: (1) what the bug is, (2) why it is a bug, "
    "(3) the specific fix. Be precise. No hedging."
)

CONDITIONS = {
    "chain-2": {
        "topology": "chain",
        "chain_handoff_prompts": {1: SYNTHESIS_HANDOFF},
        "default_handoff": None,
        "closing_prompt": None,
    },
    "flat-2": {
        "topology": "flat",
        "chain_handoff_prompts": None,
        "default_handoff": None,
        "closing_prompt": None,
    },
}


def build_transcript(messages) -> str:
    from langchain_core.messages import AIMessage
    lines = []
    for m in messages:
        if isinstance(m, dict):
            role, content = m.get("role", "unknown"), m.get("content", "")
        elif isinstance(m, AIMessage):
            role, content = "assistant", m.content
        else:
            role = "user"
            content = m.content if hasattr(m, "content") else str(m)
        lines.append(f"[{role.upper()}]: {content}")
    return "\n\n".join(lines)


def _load_done() -> set[str]:
    done: set[str] = set()
    if not RESULTS_FILE.exists():
        return done
    with RESULTS_FILE.open() as f:
        for line in f:
            try:
                rec = json.loads(line)
                done.add(f"{rec['condition']}::{rec['scenario_id']}::{rec['rep']}")
            except Exception:
                pass
    return done


def _append(rec: dict) -> None:
    RESULTS_FILE.parent.mkdir(exist_ok=True)
    with RESULTS_FILE.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def run_one(condition_name: str, cond: dict, scenario_id: str, rep: int) -> dict | None:
    scenario = ALL_CODE_REVIEW_SCENARIOS[scenario_id]
    run_id   = str(uuid.uuid4())

    pool    = initialise_pool(seed=SEED + rep)
    workers = [a for a in pool if not a.is_judge]
    judges  = [a for a in pool if a.is_judge]

    from phases.phase1.run_simulation import draft_team  # type: ignore
    # Use adaptive_intelligence + feedback_orientation as task dims for code review
    task_dims = ["adaptive_intelligence", "feedback_orientation", "ambiguity_tolerance"]
    team, captain_id = draft_team(workers, 2, task_dims, "drafted")

    try:
        state = run_simulation(
            agents=team,
            scenario_brief=scenario.brief,
            phase="phase_b",
            topology=cond["topology"],
            flat_rounds=FLAT_ROUNDS,
            chain_handoff_prompts=cond["chain_handoff_prompts"],
            default_handoff=cond["default_handoff"],
            closing_prompt=cond["closing_prompt"],
        )
    except Exception as e:
        print(f"    ERROR: {e}")
        traceback.print_exc()
        return None

    transcript = build_transcript(state["messages"])

    evaluations = score_transcript_panel(
        run_id=run_id,
        phase="phase_b",
        transcript=transcript,
        rubric=scenario.rubric,
        n_judges=len(judges),
        topology=cond["topology"],
        team_size=2,
    )

    scores     = [e.task_score for e in evaluations]
    mean_score = sum(scores) / len(scores)

    return {
        "run_id":       run_id,
        "condition":    condition_name,
        "topology":     cond["topology"],
        "scenario_id":  scenario_id,
        "category":     scenario.category,
        "planted_bugs": scenario.planted_bugs,
        "rep":          rep,
        "task_score":   mean_score,
        "judge_scores": scores,
        "turn_count":   state["turn_count"],
    }


def main():
    parser = argparse.ArgumentParser(description="Phase B: Code Review task coverage")
    parser.add_argument("--reps", type=int, default=3, help="Reps per condition-scenario")
    parser.add_argument("--conditions", nargs="+", default=list(CONDITIONS.keys()),
                        choices=list(CONDITIONS.keys()))
    args = parser.parse_args()

    scenarios = list(ALL_CODE_REVIEW_SCENARIOS.keys())
    done      = _load_done()
    total     = len(args.conditions) * len(scenarios) * args.reps
    completed = 0

    print(f"Phase B: Code Review")
    print(f"Conditions:  {args.conditions}")
    print(f"Scenarios:   {scenarios}")
    print(f"Reps:        {args.reps}")
    print(f"Total runs:  {total}")
    print("=" * 60)

    for cond_name in args.conditions:
        cond = CONDITIONS[cond_name]
        print(f"\n=== {cond_name} ===")
        for scenario_id in scenarios:
            for rep in range(args.reps):
                key = f"{cond_name}::{scenario_id}::{rep}"
                completed += 1

                if key in done:
                    print(f"  [{completed}/{total}] {scenario_id} rep={rep} — SKIP")
                    continue

                print(f"  [{completed}/{total}] {scenario_id} rep={rep} ...", end="", flush=True)
                rec = run_one(cond_name, cond, scenario_id, rep)
                if rec is None:
                    print(" ERROR")
                    continue

                _append(rec)
                done.add(key)
                print(f" score={rec['task_score']:.1f}")
                time.sleep(DELAY_SECS)

    print(f"\n{'='*60}")
    print(f"Done. Results in {RESULTS_FILE}")


if __name__ == "__main__":
    main()
