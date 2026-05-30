# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Team drafting utilities shared across phases.

draft_team is defined here rather than in phases/phase1/run_simulation.py
so that phase5, phase_b, and future phases can import it without pulling in
phase1's top-level telemetry/database imports.
"""
from __future__ import annotations
from .profile import AgentProfile
from .pool import select_captain


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
        for _ in range(team_size - 1):
            if not workers:
                break
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
        founder_dims = ["drive_alignment", "philosophy_cohesion"]
        def founder_score(a: AgentProfile) -> float:
            high = sum(getattr(a.dimensions, d) for d in founder_dims)
            low  = getattr(a.dimensions, "ambiguity_tolerance") + getattr(a.dimensions, "feedback_orientation")
            return high - low
        ranked = sorted(workers, key=founder_score, reverse=True)
        team   = ranked[:team_size]
        for a in team:
            workers.remove(a)
        return team, team[0].agent_id

    raise ValueError(f"Unknown composition: {composition}")
