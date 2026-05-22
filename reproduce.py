#!/usr/bin/env python3
"""
Reproduce the core finding: chain topology vs flat topology on the same team.

Usage:
    python reproduce.py

No database required — set only GEMINI_API_KEY in your .env.
Runs scenario s01_series_a_fork, team-size=4, drafted composition, seed=42.
Prints each agent turn live. Shows scores at the end.

Expected output:
    Chain mean task score:  ~75
    Flat  mean task score:  ~35
    Gap:                    ~40 points
"""
from __future__ import annotations
import os
import sys
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    print("ERROR: GEMINI_API_KEY not set. Add it to your .env file.")
    sys.exit(1)

# Patch database module so reproduce.py works without DATABASE_URL
import unittest.mock as _mock
import src.telemetry.database as _db
_db.insert_run        = _mock.MagicMock()
_db.insert_evaluation = _mock.MagicMock()

from src.agents.pool import initialise_pool
from src.agents.constitution import build_constitution
from src.orchestration.engine import (
    SimState, build_chain_graph, build_flat_graph, _to_gemini_contents
)
from src.evaluation.judge import score_transcript_panel
from src.scenarios import ALL_SCENARIOS
from run_simulation import draft_team, build_transcript

SCENARIO_ID = "s01_series_a_fork"
TEAM_SIZE   = 4
COMPOSITION = "drafted"
SEED        = 42

_SEP = "─" * 60


def run_with_live_output(topology: str, agents, scenario) -> tuple[SimState, str]:
    """Run a simulation and print each agent turn as it is produced."""
    import uuid

    initial_state: SimState = {
        "run_id": str(uuid.uuid4()),
        "phase": scenario.phase,
        "scenario_brief": scenario.brief,
        "messages": [{"role": "user", "content": scenario.brief}],
        "turn_count": 0,
        "token_usage": {},
        "output_token_usage": {},
        "cull_events": [],
        "active_agent_ids": [a.agent_id for a in agents],
        "routing_log": [],
        "state_snapshot": None,
    }

    if topology == "chain":
        graph = build_chain_graph(agents, scenario.brief)
    else:
        graph = build_flat_graph(agents, max_rounds=2)

    compiled = graph.compile()
    prev_msg_count = 1  # skip the initial user message

    final_state = initial_state
    for chunk in compiled.stream(initial_state):
        for node_name, state in chunk.items():
            if not isinstance(state, dict):
                continue
            msgs = state.get("messages", [])
            new_msgs = msgs[prev_msg_count:]
            for m in new_msgs:
                if isinstance(m, dict):
                    content = m.get("content", "")
                else:
                    content = getattr(m, "content", str(m))
                print(f"\n{content}")
                print(_SEP)
            prev_msg_count = len(msgs)
            final_state = state

    transcript = build_transcript(final_state.get("messages", []))
    return final_state, transcript


def score(run_id, scenario, transcript, judges) -> float:
    evals = score_transcript_panel(
        run_id=run_id,
        phase=scenario.phase,
        transcript=transcript,
        rubric=scenario.rubric,
        n_judges=len(judges),
    )
    scores = [e.task_score for e in evals]
    print(f"  Judge scores: {scores}")
    return sum(scores) / len(scores)


def main():
    scenario = ALL_SCENARIOS[SCENARIO_ID]
    pool     = initialise_pool(seed=SEED)
    workers  = [a for a in pool if not a.is_judge]
    judges   = [a for a in pool if a.is_judge]

    # Draft the same team for both runs
    team_chain, captain_id = draft_team(
        list(workers), TEAM_SIZE, scenario.task_dimensions, COMPOSITION
    )
    team_flat, _ = draft_team(
        list(workers), TEAM_SIZE, scenario.task_dimensions, COMPOSITION
    )

    results = {}

    for topology, team in [("chain", team_chain), ("flat", team_flat)]:
        print(f"\n{'='*60}")
        print(f"TOPOLOGY: {topology.upper()}")
        print(f"SCENARIO: {SCENARIO_ID}")
        print(f"TEAM:     {[a.agent_id for a in team]}")
        print(f"CAPTAIN:  {captain_id}")
        print(f"{'='*60}")
        print(f"\nSCENARIO BRIEF:\n{scenario.brief}\n")
        print(_SEP)

        final_state, transcript = run_with_live_output(topology, team, scenario)

        total_tokens = sum(final_state.get("token_usage", {}).values())
        culls = [e["agent_id"] for e in final_state.get("cull_events", [])]
        print(f"\nTurns: {final_state.get('turn_count', 0)} | Tokens: {total_tokens} | Culls: {culls}")

        print(f"\nSCORING ({topology})...")
        mean = score(final_state["run_id"], scenario, transcript, judges)
        results[topology] = mean
        print(f"  Mean task score: {mean:.1f}/100\n")

    print(f"\n{'='*60}")
    print("RESULT COMPARISON")
    print(f"{'='*60}")
    print(f"  Chain mean task score:  {results.get('chain', 0):.1f}/100")
    print(f"  Flat  mean task score:  {results.get('flat',  0):.1f}/100")
    gap = results.get('chain', 0) - results.get('flat', 0)
    print(f"  Gap:                    {gap:+.1f} points")
    print()
    if gap > 10:
        print("  Chain outperforms flat — sequential commitment beats open deliberation.")
    elif gap < -10:
        print("  Flat outperforms chain — open deliberation beats sequential commitment.")
    else:
        print("  No significant gap — topologies comparable on this run.")
    print()


if __name__ == "__main__":
    main()
