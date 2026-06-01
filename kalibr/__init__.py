# Copyright (C) 2026 Aryan Shah
# AGPL-3.0 for research/non-commercial use. Commercial license: aryan199841@gmail.com

"""
Kalibr — empirically-grounded multi-agent orchestration.

Configure your model in .env before importing:
    GEMINI_API_KEY=...          # default model: gemini-2.5-flash
    ANTHROPIC_API_KEY=...       # set MODEL_PROVIDER=anthropic, MODEL=claude-...
    MODEL=gemini-2.5-flash      # override model
    MODEL_PROVIDER=gemini       # gemini | anthropic | openai

Quickstart:
    from kalibr import chain, route

    # 2-agent synthesis chain — empirically optimal for judgment tasks
    result = chain(task="Should we pivot to enterprise or stay SMB?")
    print(result.output)

    # Auto-route: classifies task and picks the right config
    result = route(task="Implement a binary search function in Python.")
    print(result.output)

    # With judge-panel scoring (+latency)
    result = chain(task="Evaluate this acquisition offer.", score=True)
    print(result.score)   # 0-100
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache

from src.orchestration.engine import run_simulation
from src.agents.profile import (
    AgentProfile,
    KalibrDimensions,
    GameTheoryParams,
    Role,
    ConflictStyle,
)


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


@lru_cache(maxsize=1)
def _judges() -> list[AgentProfile]:
    """Return the 3-judge panel used across all research phases. Cached after first call."""
    from src.agents.pool import initialise_pool
    pool = initialise_pool(seed=42)
    return [a for a in pool if a.is_judge]


def _extract_output(messages: list, topology: str = "chain") -> str:
    from langchain_core.messages import AIMessage
    assistant_blocks = []
    for m in messages:
        if isinstance(m, dict) and m.get("role") == "assistant":
            assistant_blocks.append(m["content"])
        elif isinstance(m, AIMessage):
            assistant_blocks.append(m.content)
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


def _panel_score(state: dict, topology: str = "chain") -> float:
    from src.evaluation.judge import score_transcript_panel
    rubric = (
        "Score whether the final response directly addresses the task, "
        "commits to a clear answer, and provides specific reasoning. "
        "Penalise hedging, vagueness, and incomplete answers."
    )
    judges = _judges()
    evals = score_transcript_panel(
        run_id=state["run_id"],
        phase="kalibr",
        transcript=_build_transcript(state["messages"]),
        rubric=rubric,
        n_judges=len(judges),
        judge_agents=judges,
        topology=topology,
        team_size=2,
    )
    return sum(e.task_score for e in evals) / len(evals)


def chain(task: str, score: bool = False) -> KalibrResult:
    """
    Run a 2-agent synthesis chain on any task.

    Agent 1 analyses; agent 2 synthesises into a committed final answer.
    Empirically optimal for judgment and open-ended tasks (Phase 5: 86.3/100).
    Configure model via .env (MODEL, MODEL_PROVIDER, GEMINI_API_KEY).

    Args:
        task:  The task prompt.
        score: If True, run the 3-judge panel and populate result.score (adds ~3 LLM calls).

    Returns:
        KalibrResult(output, transcript, turn_count, token_usage, score)
    """
    handoff = (
        "OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN. "
        "You are the terminal synthesis agent. The prior analysis is above. "
        "You must: 1. Identify what the prior analysis got right. "
        "2. Identify what it missed or got wrong. "
        "3. Produce a COMPLETE, DEFINITIVE final answer — strictly better. "
        "Do not summarise. Close every open question. Be decisive."
    )

    agents = [
        _generic_agent("analyst",     role=Role.IMPLEMENTER),
        _generic_agent("synthesizer", role=Role.SOLVER),
    ]

    state = run_simulation(
        agents=agents,
        scenario_brief=task,
        phase="kalibr",
        topology="chain",
        chain_handoff_prompts={1: handoff},
        default_handoff=None,
    )

    return KalibrResult(
        output=_extract_output(state["messages"], topology="chain"),
        transcript=_build_transcript(state["messages"]),
        turn_count=state["turn_count"],
        token_usage=state["token_usage"],
        score=_panel_score(state, topology="chain") if score else None,
    )


def route(task: str, score: bool = False) -> KalibrResult:
    """
    Classify task domain and run the empirically optimal config.

    judgment tasks  → chain-2 with Kalibr dimension profiles
    execution tasks → chain-2 generic with code-specific synthesis handoff
    Classifier accuracy: 100% on 47 tasks including adversarial inputs (Phase 4).

    Args:
        task:  The task prompt.
        score: If True, run the 3-judge panel and populate result.score.

    Returns:
        KalibrResult(output, transcript, turn_count, token_usage, score)
    """
    from src.meta_orchestrator.classifier import classify
    from src.meta_orchestrator.router import route as _route

    config = _route(classify(task))

    state = run_simulation(
        agents=config["agents"],
        scenario_brief=task,
        phase="kalibr",
        topology=config["topology"],
        chain_handoff_prompts=config.get("handoff_prompts"),
        default_handoff=None,
    )

    topology = config["topology"]
    return KalibrResult(
        output=_extract_output(state["messages"], topology=topology),
        transcript=_build_transcript(state["messages"]),
        turn_count=state["turn_count"],
        token_usage=state["token_usage"],
        score=_panel_score(state, topology=topology) if score else None,
    )


__all__ = ["chain", "route", "KalibrResult", "KalibrDimensions", "AgentProfile"]
