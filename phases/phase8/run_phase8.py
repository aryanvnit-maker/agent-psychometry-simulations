#!/usr/bin/env python3
# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Phase 8: Agent Diversity vs Structured Self-Refinement.

Compute-matched comparison: both conditions make exactly 2 LLM calls.

    kalibr-chain      — two DIFFERENT agents (captain + diversity pick).
                        Diversity pick goes first, captain synthesizes last.
                        Tests whether a second perspective improves output.

    single-agent-refine — same captain, two calls.
                          Draft on first call, synthesize on second.
                          Isolates structured prompting from agent diversity.

If kalibr-chain > single-agent-refine:
    Agent diversity adds genuine value beyond structured self-prompting.
    Multi-agent architecture has a non-trivial moat.

If tied:
    The advantage is in the synthesis step structure, not agent diversity.
    A single agent with forced two-pass refinement matches multi-agent.
    Product pivot: sell collapse-proof structured refinement, not swarm intelligence.

Same judgment scenarios as Phase 5. LLM judge panel scores each run.

Usage:
    python phases/phase8/run_phase8.py
    python phases/phase8/run_phase8.py --reps 10

Output: results/phase8.jsonl
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

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.pool import initialise_pool
from src.agents.team import draft_team
from src.orchestration.engine import run_simulation, _call_agent
from src.evaluation.judge import score_transcript_panel
from src.scenarios import ALL_SCENARIOS

RESULTS_FILE = Path("results/phase8.jsonl")
SEED         = 99
DELAY_SECS   = 2

SYNTHESIS_PROMPT = (
    "OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN.\n"
    "You are the terminal synthesis agent. The prior analysis is above.\n"
    "You must:\n"
    "1. Identify what the prior analysis got right\n"
    "2. Identify what it missed or got wrong\n"
    "3. Produce a COMPLETE, DEFINITIVE final answer — strictly better\n"
    "Do not summarise. Close every open question. Be decisive."
)


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


def run_chain(scenario_id: str, rep: int, rep_seed: int) -> dict | None:
    """kalibr-chain: two different agents, captain synthesizes last. 2 calls."""
    run_id  = str(uuid.uuid4())
    scenario = ALL_SCENARIOS[scenario_id]

    pool    = initialise_pool(seed=rep_seed)
    workers = [a for a in pool if not a.is_judge]
    judges  = [a for a in pool if a.is_judge]

    team, captain_id = draft_team(workers, 2, scenario.task_dimensions, "drafted")
    team = list(reversed(team))  # diversity pick first, captain synthesizes

    try:
        state = run_simulation(
            agents=team,
            scenario_brief=scenario.brief,
            phase=scenario.phase,
            topology="chain",
            chain_handoff_prompts={1: SYNTHESIS_PROMPT},
            default_handoff=None,
        )
    except Exception as e:
        print(f"    ERROR in simulation: {e}")
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
            topology="chain",
            team_size=2,
        )
    except Exception as e:
        print(f"    ERROR in judge panel: {e}")
        return None

    scores     = [e.task_score for e in evaluations]
    mean_score = sum(scores) / len(scores)

    return {
        "run_id":      run_id,
        "condition":   "kalibr-chain",
        "scenario_id": scenario_id,
        "rep":         rep,
        "captain_id":  captain_id,
        "task_score":  mean_score,
        "judge_scores": scores,
        "turn_count":  state["turn_count"],
        "cull_events": state["cull_events"],
        "n_calls":     2,
    }


def run_refine(scenario_id: str, rep: int, rep_seed: int) -> dict | None:
    """single-agent-refine: same captain, two calls. 2 calls."""
    run_id   = str(uuid.uuid4())
    scenario = ALL_SCENARIOS[scenario_id]

    pool    = initialise_pool(seed=rep_seed)
    workers = [a for a in pool if not a.is_judge]
    judges  = [a for a in pool if a.is_judge]

    team, captain_id = draft_team(workers, 1, scenario.task_dimensions, "drafted")
    captain = team[0]

    # Call 1: initial analysis
    step1_msgs = [{"role": "user", "content": scenario.brief}]
    try:
        analysis, _, _ = _call_agent(captain, step1_msgs, scenario.brief)
    except Exception as e:
        print(f"    ERROR step1: {e}")
        traceback.print_exc()
        return None

    # Call 2: self-synthesis with same prompt as chain
    step2_msgs = [
        {"role": "user",      "content": scenario.brief},
        {"role": "assistant", "content": f"[{captain.agent_id}]: {analysis}"},
        {"role": "user",      "content": SYNTHESIS_PROMPT},
    ]
    try:
        final_output, _, _ = _call_agent(captain, step2_msgs, scenario.brief)
    except Exception as e:
        print(f"    ERROR step2: {e}")
        traceback.print_exc()
        return None

    # Build transcript for judge — omit SYNTHESIS_PROMPT to match chain transcript structure
    # (engine injects it transiently and never stores it in state messages).
    messages = [
        {"role": "user",      "content": scenario.brief},
        {"role": "assistant", "content": f"[{captain.agent_id}]: {analysis}"},
        {"role": "assistant", "content": f"[{captain.agent_id}_synthesis]: {final_output}"},
    ]
    transcript = build_transcript(messages)

    try:
        evaluations = score_transcript_panel(
            run_id=run_id,
            phase=scenario.phase,
            transcript=transcript,
            rubric=scenario.rubric,
            n_judges=len(judges),
            judge_agents=judges,
            topology="chain",
            team_size=1,
        )
    except Exception as e:
        print(f"    ERROR in judge panel: {e}")
        return None

    scores     = [e.task_score for e in evaluations]
    mean_score = sum(scores) / len(scores)

    return {
        "run_id":      run_id,
        "condition":   "single-agent-refine",
        "scenario_id": scenario_id,
        "rep":         rep,
        "captain_id":  captain_id,
        "task_score":  mean_score,
        "judge_scores": scores,
        "turn_count":  2,
        "cull_events": [],
        "n_calls":     2,
    }


def main():
    parser = argparse.ArgumentParser(description="Phase 8: Diversity vs Self-Refinement")
    parser.add_argument("--reps", type=int, default=10)
    args = parser.parse_args()

    scenarios  = list(ALL_SCENARIOS.keys())
    conditions = ["kalibr-chain", "single-agent-refine"]
    done       = _load_done()
    total      = len(conditions) * len(scenarios) * args.reps
    completed  = 0

    print("Phase 8: Agent Diversity vs Structured Self-Refinement")
    print(f"Scenarios:  {scenarios}")
    print(f"Reps:       {args.reps}")
    print(f"Total runs: {total}")
    print(f"Done:       {len(done)}")
    print("=" * 60)

    runners = {
        "kalibr-chain":       run_chain,
        "single-agent-refine": run_refine,
    }

    for cond_name in conditions:
        print(f"\n=== {cond_name} ===")
        for scenario_id in scenarios:
            for rep in range(args.reps):
                key = f"{cond_name}::{scenario_id}::{rep}"
                completed += 1

                if key in done:
                    print(f"  [{completed}/{total}] {scenario_id} rep{rep} — SKIP")
                    continue

                print(f"  [{completed}/{total}] {scenario_id} rep{rep} ...", end="", flush=True)
                # Seed on (scenario, rep) only — both conditions get the same pool
                # for the same scenario+rep so the captain is the same person.
                scenario_idx = scenarios.index(scenario_id)
                rep_seed = SEED + scenario_idx * args.reps + rep
                rec = runners[cond_name](scenario_id, rep, rep_seed)

                if rec is None:
                    print(" ERROR")
                    continue

                _append(rec)
                done.add(key)
                print(f" {rec['task_score']:.1f}")
                time.sleep(DELAY_SECS)

    print(f"\n{'='*60}")
    print(f"Done. Results in {RESULTS_FILE}")


if __name__ == "__main__":
    main()
