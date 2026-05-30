# Copyright (C) 2026 Aryan Shah
# AGPL-3.0 for research/non-commercial use. Commercial license: aryan199841@gmail.com

"""
Kalibr — empirically-grounded multi-agent orchestration.

Quickstart:
    from kalibr import chain, route, KalibrProfile

    # Run a 2-agent chain on any task
    result = chain(
        task="Should we pivot to enterprise or stay SMB?",
        model="gemini-2.5-flash",   # or "gpt-4o" / "claude-3-5-sonnet-20241022"
    )
    print(result.output)
    print(result.score)   # judge panel score 0-100

    # Auto-route: Kalibr classifies the task and picks the right config
    result = route(
        task="Implement a binary search function in Python.",
        model="gemini-2.5-flash",
    )
    print(result.output)
"""
from __future__ import annotations
import os
from dataclasses import dataclass

from src.orchestration.engine import run_simulation
from src.agents.profile import (
    AgentProfile,
    KalibrDimensions,
    GameTheoryParams,
    Role,
    ConflictStyle,
)
from src.agents.constitution import build_constitution


@dataclass
class KalibrResult:
    output: str
    transcript: str
    turn_count: int
    token_usage: dict
    score: float | None = None


def _generic_agent(agent_id: str, role: Role = Role.IMPLEMENTER) -> AgentProfile:
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


def _extract_output(messages: list, topology: str = "chain") -> str:
    assistant_blocks = [
        m["content"] for m in messages
        if isinstance(m, dict) and m.get("role") == "assistant"
    ]
    if not assistant_blocks:
        return ""
    if topology == "chain":
        return assistant_blocks[-1]
    return "\n\n".join(assistant_blocks[-2:])


def _build_transcript(messages: list) -> str:
    lines = []
    for m in messages:
        if isinstance(m, dict):
            lines.append(f"[{m.get('role','?').upper()}]: {m.get('content','')}")
    return "\n\n".join(lines)


def chain(
    task: str,
    model: str = "gemini-2.5-flash",
    provider: str | None = None,
    score: bool = False,
) -> KalibrResult:
    """
    Run a 2-agent chain on any task.

    Chain topology: agent 1 analyses, agent 2 synthesises into a committed final response.
    Empirically optimal for judgment and open-ended tasks (Phase 1 finding: +46 pts vs flat).

    Args:
        task:     The task prompt.
        model:    Model name (Gemini, OpenAI, or Anthropic model string).
        provider: 'gemini' | 'openai' | 'anthropic'. Auto-detected from model name if omitted.
        score:    If True, run a 3-judge panel and return score in result.score (adds latency).

    Returns:
        KalibrResult with output, transcript, turn_count, token_usage, score.
    """
    _set_provider(model, provider)

    agents = [
        _generic_agent("analyst",    role=Role.IMPLEMENTER),
        _generic_agent("synthesizer", role=Role.SOLVER),
    ]

    handoff = (
        "Based on the analysis above, synthesize a complete final response that directly "
        "addresses the prompt. Be specific and decisive. No hedging."
    )

    state = run_simulation(
        agents=agents,
        scenario_brief=task,
        phase="kalibr",
        topology="chain",
        chain_handoff_prompts={1: handoff},
        default_handoff=None,
    )

    result_score = None
    if score:
        result_score = _panel_score(state, task, topology="chain")

    return KalibrResult(
        output=_extract_output(state["messages"], topology="chain"),
        transcript=_build_transcript(state["messages"]),
        turn_count=state["turn_count"],
        token_usage=state["token_usage"],
        score=result_score,
    )


def route(
    task: str,
    model: str = "gemini-2.5-flash",
    provider: str | None = None,
    score: bool = False,
) -> KalibrResult:
    """
    Classify task domain and run the empirically optimal agent config.

    judgment tasks  → chain-2 with Kalibr dimension profiles
    execution tasks → chain-2 generic with code-specific handoff

    Classifier accuracy: 100% on 47 tasks including adversarial inputs (Phase 4).

    Args:
        task:     The task prompt.
        model:    Model name.
        provider: Auto-detected if omitted.
        score:    If True, run judge panel scoring.

    Returns:
        KalibrResult with output and metadata.
    """
    _set_provider(model, provider)

    from src.meta_orchestrator.classifier import classify
    from src.meta_orchestrator.router import route as _route

    domain = classify(task)
    config = _route(domain)

    state = run_simulation(
        agents=config["agents"],
        scenario_brief=task,
        phase="kalibr",
        topology=config["topology"],
        chain_handoff_prompts=config.get("handoff_prompts"),
        default_handoff=None,
    )

    result_score = None
    if score:
        result_score = _panel_score(state, task, topology=config["topology"])

    return KalibrResult(
        output=_extract_output(state["messages"], topology=config["topology"]),
        transcript=_build_transcript(state["messages"]),
        turn_count=state["turn_count"],
        token_usage=state["token_usage"],
        score=result_score,
    )


def _panel_score(state: dict, task: str, topology: str = "chain") -> float:
    from src.evaluation.judge import score_transcript_panel
    transcript = _build_transcript(state["messages"])
    rubric = (
        "Score whether the final response directly addresses the task, "
        "commits to a clear answer, and provides specific reasoning. "
        "Penalise hedging, vagueness, and incomplete answers."
    )
    evals = score_transcript_panel(
        run_id=state["run_id"],
        phase="kalibr",
        transcript=transcript,
        rubric=rubric,
        n_judges=3,
        topology=topology,
        team_size=2,
    )
    return sum(e.task_score for e in evals) / len(evals)


def _set_provider(model: str, provider: str | None) -> None:
    if provider:
        os.environ["MODEL_PROVIDER"] = provider
        os.environ["MODEL"] = model
        return
    # Auto-detect from model name
    if model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"):
        os.environ["MODEL_PROVIDER"] = "openai"
    elif model.startswith("claude"):
        os.environ["MODEL_PROVIDER"] = "anthropic"
    else:
        os.environ["MODEL_PROVIDER"] = "gemini"
    os.environ["MODEL"] = model


__all__ = ["chain", "route", "KalibrResult", "KalibrProfile", "KalibrDimensions"]
KalibrProfile = AgentProfile
