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
Phase 5: Topology × Handoff Factorial Experiment.

Resolves the confound between topology and handoff prompts in Phase 1.

Phase 1 compared chain (which injects explicit handoff prompts) vs flat (which does
not). The gap could be caused by topology, by handoff prompts, or by both. This
experiment runs a clean 2×2 factorial to isolate each variable.

2×2 Design:
    chain / handoff       — chain topology + explicit synthesis handoff (Phase 1 default)
    chain / no-handoff    — chain topology, second agent sees prior output with no instruction
    flat  / no-handoff    — flat round-table, no closing synthesis step (Phase 1 default)
    flat  / handoff       — flat round-table + explicit closing synthesis step

Fixed: team_size=2, composition=drafted, all 4 Phase 1 judgment scenarios.
Runs:  --reps per condition-scenario (default 5 → 80 total runs).

Key interpretations:
    chain/no-handoff > flat/no-handoff  → topology IS causal (even without handoffs)
    chain/handoff    > chain/no-handoff → handoff adds value ON TOP of topology
    flat/handoff     > flat/no-handoff  → handoff alone can partially rescue flat

Usage:
    python phases/phase5/run_handoff_factorial.py
    python phases/phase5/run_handoff_factorial.py --reps 10

Output: results/handoff_factorial.jsonl
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

os.environ.setdefault("AGENT_TOKEN_BUDGET", "800")

from dotenv import load_dotenv
load_dotenv(override=True)

# Repo root on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.pool import initialise_pool
from src.agents.team import draft_team
from src.orchestration.engine import run_simulation
from src.evaluation.judge import score_transcript_panel
from src.scenarios import ALL_SCENARIOS

RESULTS_FILE = Path("results/handoff_factorial.jsonl")
SEED         = 42
FLAT_ROUNDS  = 2
DELAY_SECS   = 3

# Explicit synthesis instruction — same wording used as JUDGMENT_HANDOFF in Phase 4
SYNTHESIS_PROMPT = (
    "OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN.\n"
    "You are the terminal synthesis agent in a sequential chain. "
    "The prior agent's analysis is above.\n"
    "You must:\n"
    "1. Identify what they got right\n"
    "2. Identify what they missed or got wrong\n"
    "3. Produce a COMPLETE, DEFINITIVE final answer that is strictly better than theirs\n"
    "Do not summarise. Do not surface problems without resolving them. "
    "Close every open question. Be decisive."
)

# 4 conditions
CONDITIONS = {
    "chain/handoff": {
        "topology": "chain",
        "chain_handoff_prompts": {1: SYNTHESIS_PROMPT},
        "default_handoff": None,   # only the explicit prompt, no fallback
        "closing_prompt": None,
    },
    "chain/no-handoff": {
        "topology": "chain",
        "chain_handoff_prompts": None,
        "default_handoff": None,   # no injected prompt at all — pure continuation
        "closing_prompt": None,
    },
    "flat/no-handoff": {
        "topology": "flat",
        "chain_handoff_prompts": None,
        "default_handoff": None,
        "closing_prompt": None,
    },
    "flat/handoff": {
        "topology": "flat",
        "chain_handoff_prompts": None,
        "default_handoff": None,
        "closing_prompt": SYNTHESIS_PROMPT,
    },
}


# ---------------------------------------------------------------------------
# Transcript helper
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Resumability
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Single run
# ---------------------------------------------------------------------------

def run_one(condition_name: str, cond: dict, scenario_id: str, rep: int) -> dict | None:
    scenario = ALL_SCENARIOS[scenario_id]
    run_id   = str(uuid.uuid4())

    pool    = initialise_pool(seed=SEED + rep)
    workers = [a for a in pool if not a.is_judge]
    judges  = [a for a in pool if a.is_judge]

    team, captain_id = draft_team(workers, 2, scenario.task_dimensions, "drafted")

    try:
        state = run_simulation(
            agents=team,
            scenario_brief=scenario.brief,
            phase=scenario.phase,
            topology=cond["topology"],
            flat_rounds=FLAT_ROUNDS,
            chain_handoff_prompts=cond["chain_handoff_prompts"],
            default_handoff=cond["default_handoff"],
            closing_prompt=cond["closing_prompt"],
        )
    except Exception as e:
        print(f"    ERROR in run_simulation: {e}")
        traceback.print_exc()
        return None

    transcript = build_transcript(state["messages"])

    try:
        evaluations = score_transcript_panel(
            run_id=run_id,
            phase=scenario.phase,
            transcript=transcript,
            rubric=scenario.rubric,
            n_judges=len(judges),
            judge_agents=judges,
            topology=cond["topology"],
            team_size=2,
        )
    except Exception as e:
        print(f"    ERROR in judge panel: {e}")
        return None

    scores     = [e.task_score for e in evaluations]
    mean_score = sum(scores) / len(scores)

    return {
        "run_id":          run_id,
        "condition":       condition_name,
        "topology":        cond["topology"],
        "has_handoff":     bool(cond["chain_handoff_prompts"] or cond["closing_prompt"]),
        "scenario_id":     scenario_id,
        "rep":             rep,
        "captain_id":      captain_id,
        "task_score":      mean_score,
        "judge_scores":    scores,
        "turn_count":      state["turn_count"],
        "cull_events":     state["cull_events"],
        "geq_task_mean":   sum(e.geq_task_cohesion for e in evaluations) / len(evaluations),
        "geq_social_mean": sum(e.geq_social_cohesion for e in evaluations) / len(evaluations),
        "consensus_rate":  sum(1 for e in evaluations if e.consensus_achieved) / len(evaluations),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Phase 5: Topology × Handoff Factorial")
    parser.add_argument("--reps", type=int, default=10, help="Repetitions per condition-scenario")
    parser.add_argument("--conditions", nargs="+", default=list(CONDITIONS.keys()),
                        choices=list(CONDITIONS.keys()))
    args = parser.parse_args()

    scenarios = list(ALL_SCENARIOS.keys())
    done      = _load_done()

    total     = len(args.conditions) * len(scenarios) * args.reps
    completed = 0
    skipped   = 0

    print(f"Phase 5: Topology × Handoff Factorial")
    print(f"Conditions:  {args.conditions}")
    print(f"Scenarios:   {scenarios}")
    print(f"Reps:        {args.reps}")
    print(f"Total runs:  {total}")
    print(f"Already done: {len(done)}")
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
                    skipped += 1
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
    print(f"Skipped: {skipped}, Ran: {completed - skipped}")


if __name__ == "__main__":
    main()
