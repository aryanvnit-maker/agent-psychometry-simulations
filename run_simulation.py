#!/usr/bin/env python3
"""
Entry point for a single simulation run.

Usage:
    python run_simulation.py \
        --scenario s01_series_a_fork \
        --team-size 2 \
        --topology chain \
        --composition drafted \
        --seed 42
"""
from __future__ import annotations
import argparse
import json
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

from src.agents.pool import initialise_pool, get_workers, get_judges, select_captain
from src.agents.profile import AgentProfile
from src.orchestration.engine import run_simulation
from src.evaluation.judge import score_transcript_panel
from src.scenarios import ALL_SCENARIOS
from src.telemetry.database import insert_run, insert_evaluation


def draft_team(
    workers: list[AgentProfile],
    team_size: int,
    task_dimensions: list[str],
    composition: str,
) -> tuple[list[AgentProfile], str | None]:
    """Return (team, captain_id). Modifies workers list in place (removes drafted agents)."""
    if team_size == 1:
        captain = select_captain(workers, task_dimensions)
        workers.remove(captain)
        return [captain], captain.agent_id

    if composition == "drafted":
        captain = select_captain(workers, task_dimensions)
        workers.remove(captain)
        team = [captain]
        # Captain fills gaps: pick agents with highest scores on dimensions NOT covered by captain
        for _ in range(team_size - 1):
            if not workers:
                break
            # Simple gap-fill: pick the worker whose profile is most different from team mean
            def diversity_score(candidate: AgentProfile) -> float:
                team_means = {
                    dim: sum(getattr(a.dimensions, dim) for a in team) / len(team)
                    for dim in task_dimensions
                }
                return sum(
                    abs(getattr(candidate.dimensions, dim) - team_means[dim])
                    for dim in task_dimensions
                )
            pick = max(workers, key=diversity_score)
            workers.remove(pick)
            team.append(pick)
        return team, captain.agent_id

    if composition == "homogeneous":
        # Pick the team_size agents whose profiles are most similar to each other
        captain = select_captain(workers, task_dimensions)
        workers.remove(captain)
        team = [captain]
        for _ in range(team_size - 1):
            if not workers:
                break
            def similarity_score(candidate: AgentProfile) -> float:
                return -sum(
                    abs(getattr(candidate.dimensions, dim) - getattr(captain.dimensions, dim))
                    for dim in vars(captain.dimensions)
                )
            pick = max(workers, key=similarity_score)
            workers.remove(pick)
            team.append(pick)
        return team, captain.agent_id

    if composition == "founder_brained":
        # High drive_alignment, high philosophy_cohesion, low ambiguity_tolerance, low feedback_orientation
        founder_dims = ["drive_alignment", "philosophy_cohesion"]
        def founder_score(a: AgentProfile) -> float:
            high = sum(getattr(a.dimensions, d) for d in founder_dims)
            low = getattr(a.dimensions, "ambiguity_tolerance") + getattr(a.dimensions, "feedback_orientation")
            return high - low
        ranked = sorted(workers, key=founder_score, reverse=True)
        team = ranked[:team_size]
        for a in team:
            workers.remove(a)
        return team, team[0].agent_id

    raise ValueError(f"Unknown composition: {composition}")


def build_transcript(messages) -> str:
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, choices=list(ALL_SCENARIOS.keys()))
    parser.add_argument("--team-size", type=int, default=2, choices=[1, 2, 4, 8, 16])
    parser.add_argument("--topology", default="chain", choices=["chain", "flat", "hub_spoke"])
    parser.add_argument("--composition", default="drafted",
                        choices=["drafted", "homogeneous", "founder_brained", "missing_role"])
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--draft-order", type=int, default=1,
                        help="Which draft round this team was assembled in (1 = first pick from full pool)")
    args = parser.parse_args()

    scenario = ALL_SCENARIOS[args.scenario]
    run_id = str(uuid.uuid4())

    print(f"\n{'='*60}")
    print(f"RUN ID:     {run_id}")
    print(f"SCENARIO:   {scenario.scenario_id} ({scenario.category} / {scenario.phase})")
    print(f"TEAM SIZE:  {args.team_size}")
    print(f"TOPOLOGY:   {args.topology}")
    print(f"COMP:       {args.composition}")
    print(f"{'='*60}\n")

    # Initialise pool
    pool = initialise_pool(seed=args.seed)
    workers = [a for a in pool if not a.is_judge]
    judges = [a for a in pool if a.is_judge]

    # Draft team
    team, captain_id = draft_team(
        workers, args.team_size, scenario.task_dimensions, args.composition
    )

    print(f"CAPTAIN:    {captain_id}")
    print(f"TEAM:       {[a.agent_id for a in team]}\n")

    # Run simulation
    final_state = run_simulation(
        agents=team,
        scenario_brief=scenario.brief,
        phase=scenario.phase,
        topology=args.topology,
    )

    transcript = build_transcript(final_state["messages"])
    total_tokens = sum(final_state["token_usage"].values())

    print(f"TURNS:      {final_state['turn_count']}")
    print(f"TOKENS:     {total_tokens}")
    print(f"CULLS:      {[e['agent_id'] for e in final_state['cull_events']]}\n")

    # Persist run
    composition_matrix = {a.agent_id: a.to_dict() for a in team}
    insert_run(
        run_id=run_id,
        scenario_id=scenario.scenario_id,
        composition_matrix=composition_matrix,
        topology=args.topology,
        task_phase=scenario.phase,
        scenario_category=scenario.category,
        composition_condition=args.composition,
        team_size=args.team_size,
        captain_agent_id=captain_id,
        draft_order=args.draft_order,
        token_cost=total_tokens,
        turns_to_complete=final_state["turn_count"],
        cull_events=final_state["cull_events"],
        state_snapshot=None,
        transcript=transcript,
    )

    # Score with judge panel
    print("SCORING...\n")
    evaluations = score_transcript_panel(
        run_id=run_id,
        phase=scenario.phase,
        transcript=transcript,
        rubric=scenario.rubric,
        n_judges=len(judges),
        topology=args.topology,
        team_size=args.team_size,
    )

    for i, ev in enumerate(evaluations):
        print(f"Judge {i}: task_score={ev.task_score}, consensus={ev.consensus_achieved}, "
              f"contradictions={ev.contradiction_count}, geq_task={ev.geq_task_cohesion}")
        insert_evaluation(run_id=run_id, judge_index=i, scores=ev.model_dump())

    mean_score = sum(e.task_score for e in evaluations) / len(evaluations)
    print(f"\nMEAN TASK SCORE: {mean_score:.1f}/100")
    print(f"Run persisted to Supabase. run_id={run_id}\n")


if __name__ == "__main__":
    main()
