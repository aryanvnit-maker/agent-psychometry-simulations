#!/usr/bin/env python3
"""
Export all agent system prompts (constitutions) to /constitutions/ as readable text files.

Usage:
    python export_constitutions.py

Output:
    constitutions/
        drafted/        — diversity-optimised team (4 agents + captain)
        homogeneous/    — minimum variance team (4 agents)
        founder_brained/ — high drive, high conviction team (4 agents)
        judges/         — all 3 judge agent prompts

No API key required — constitutions are generated from dimensional profiles only.
"""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# No DB needed
import unittest.mock as _mock
import src.telemetry.database as _db
_db.insert_run        = _mock.MagicMock()
_db.insert_evaluation = _mock.MagicMock()

from src.agents.pool import initialise_pool
from src.agents.constitution import build_constitution
from src.scenarios import ALL_SCENARIOS
from run_simulation import draft_team

SCENARIO_ID = "s01_series_a_fork"
TEAM_SIZE   = 4
SEED        = 42
OUT_DIR     = Path("constitutions")


def write_constitution(path: Path, agent, include_profile: bool = True):
    path.parent.mkdir(parents=True, exist_ok=True)
    constitution = build_constitution(agent)
    with open(path, "w", encoding="utf-8") as f:
        if include_profile:
            f.write("=" * 60 + "\n")
            f.write(f"KALIBR DIMENSIONAL PROFILE — {agent.agent_id}\n")
            f.write("=" * 60 + "\n\n")
            d = agent.dimensions
            dims = {
                "philosophy_cohesion":  d.philosophy_cohesion,
                "drive_alignment":      d.drive_alignment,
                "bonding_index":        d.bonding_index,
                "adaptive_intelligence": d.adaptive_intelligence,
                "volatility_vector":    d.volatility_vector,
                "ambiguity_tolerance":  d.ambiguity_tolerance,
                "influence_style":      d.influence_style,
                "feedback_orientation": d.feedback_orientation,
                "temporal_orientation": d.temporal_orientation,
                "energy_resilience":    d.energy_resilience,
            }
            for dim, val in dims.items():
                bar = "█" * (val // 10) + "░" * (10 - val // 10)
                f.write(f"  {dim:<25} {bar}  {val:>3}\n")
            f.write(f"\n  role:             {agent.role.value}\n")
            f.write(f"  conflict_style:   {agent.game_theory.conflict_style.value}\n")
            f.write(f"  context_sharing:  {agent.game_theory.context_sharing}\n")
            f.write(f"  memory:           {agent.game_theory.memory_persistence}\n")
            f.write(f"  signaling:        {agent.game_theory.signaling}\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("GENERATED SYSTEM PROMPT (CONSTITUTION)\n")
            f.write("=" * 60 + "\n\n")
        f.write(constitution)
        f.write("\n")
    print(f"  Wrote: {path}")


def main():
    scenario = ALL_SCENARIOS[SCENARIO_ID]
    pool     = initialise_pool(seed=SEED)
    workers  = [a for a in pool if not a.is_judge]
    judges   = [a for a in pool if a.is_judge]

    print(f"\nExporting constitutions (seed={SEED}, scenario={SCENARIO_ID}, team_size={TEAM_SIZE})\n")

    for composition in ["drafted", "homogeneous", "founder_brained"]:
        print(f"[{composition}]")
        team, captain_id = draft_team(
            list(workers), TEAM_SIZE, scenario.task_dimensions, composition
        )
        for agent in team:
            tag = "_captain" if agent.agent_id == captain_id else ""
            fname = OUT_DIR / composition / f"{agent.agent_id}{tag}.txt"
            write_constitution(fname, agent)

        # Write a README for this composition folder
        readme_path = OUT_DIR / composition / "README.txt"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(f"Composition: {composition}\n")
            f.write(f"Scenario:    {SCENARIO_ID}\n")
            f.write(f"Team size:   {TEAM_SIZE}\n")
            f.write(f"Captain:     {captain_id}\n")
            f.write(f"Seed:        {SEED}\n\n")
            f.write("Agents:\n")
            for agent in team:
                tag = " (captain)" if agent.agent_id == captain_id else ""
                f.write(f"  {agent.agent_id}{tag} — role: {agent.role.value}\n")
        print(f"  Wrote: {readme_path}\n")

    print("[judges]")
    for judge in judges:
        fname = OUT_DIR / "judges" / f"{judge.agent_id}.txt"
        write_constitution(fname, judge)

    print(f"\nDone. All constitutions written to /{OUT_DIR}/")
    print("\nKey files to read:")
    print(f"  constitutions/founder_brained/   — why these agents excel on chain topology")
    print(f"  constitutions/drafted/           — why constraint collision degrades diverse teams")
    print(f"  constitutions/judges/            — neutral evaluator profile")


if __name__ == "__main__":
    main()
