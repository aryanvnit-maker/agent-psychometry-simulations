#!/usr/bin/env python3
# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Phase E: Epistemic Investigation Architecture
FLF Epistemic Case Study Competition (flf.org)

Tests four conditions on five open epistemic disputes (COVID origins, eggs/CVD,
LHC black holes, nuclear power risk, alcohol J-curve):

    kalibr-chain/epistemic   — chain-2 + EPISTEMIC_SYNTHESIS_PROMPT
                               Tuned for calibrated uncertainty, not decisive commitment.
                               This is the key fix for the Phase 9 post-mortem gap:
                               the decisive synthesis prompt scored −13.3 pts on
                               reflective tasks; this variant is designed for investigation.

    single-agent/epistemic   — single agent + EPISTEMIC_SYNTHESIS_PROMPT (self-review)
                               Compute-matched baseline: same 2 LLM calls, 1 agent.

    kalibr-chain/decisive    — chain-2 + DECISIVE_SYNTHESIS_PROMPT (ablation)
                               Same architecture as kalibr-chain but with Phase 5/8/9 prompt.
                               Tests H2: whether prompt specificity (not architecture) drives
                               the Phase 9 post-mortem gap. Expected to underperform on
                               epistemic tasks — replicating the −13.3 pt finding.

    flat/no-handoff          — round-table, 2 rounds, no synthesis step
                               The framework default (LangChain/CrewAI/AutoGen baseline).
                               Expected to fail on epistemic quality for the same reason
                               it fails on judgment tasks: no forcing function to commit
                               to a structured epistemic output.

The EPISTEMIC_SYNTHESIS_PROMPT is deliberately different from the SYNTHESIS_PROMPT
used in Phases 5, 8, and 9. That prompt instructs the terminal agent to "be decisive"
and "close every open question" — optimal for strategy/resource/crisis tasks but
known to degrade performance on reflective tasks (Phase 9, s03, −13.3 pts).

The epistemic variant instructs the terminal agent to:
    - Identify cruxes (not collapse to a verdict)
    - Assess evidence quality per claim
    - Flag correlated evidence
    - Give calibrated probability ranges
    - Preserve uncertainty where warranted

This tests whether the synthesis architecture generalises to epistemic investigation
tasks when the prompt is correctly tuned for reflection rather than commitment.

Usage:
    python phases/phase_e/run_phase_e.py
    python phases/phase_e/run_phase_e.py --reps 5 --scenarios e01 e02
    python phases/phase_e/run_phase_e.py --conditions kalibr-chain single-agent

Output: results/phase_e.jsonl
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
load_dotenv(override=True)

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.pool import initialise_pool
from src.agents.team import draft_team
from src.orchestration.engine import run_simulation, build_flat_graph, SimState
from src.evaluation.judge import score_transcript_panel
from src.evaluation.epistemic_schema import (
    EpistemicMap,
    EPISTEMIC_MAP_JSON_SCHEMA,
    parse_epistemic_map,
)
from src.scenarios.epistemic import EPISTEMIC_SCENARIOS

RESULTS_FILE = Path("results/phase_e.jsonl")
MAPS_DIR     = Path("results/epistemic_maps")
SEED         = 42
DELAY_SECS   = 2

# ── Synthesis prompts ─────────────────────────────────────────────────────────

# Decisive synthesis — identical to Phases 5, 8, 9.
# Known to underperform on reflective tasks (Phase 9 s03: −13.3 pts).
# Included for comparison only.
DECISIVE_SYNTHESIS_PROMPT = (
    "OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN.\n"
    "You are the terminal synthesis agent. The prior analysis is above.\n"
    "You must:\n"
    "1. Identify what the prior analysis got right\n"
    "2. Identify what it missed or got wrong\n"
    "3. Produce a COMPLETE, DEFINITIVE final answer — strictly better\n"
    "Do not summarise. Close every open question. Be decisive."
)

# Epistemic synthesis — designed for investigation tasks.
# Does NOT demand decisiveness. Demands calibration and structure.
# This is the primary intervention in Phase E.
EPISTEMIC_SYNTHESIS_PROMPT = (
    "OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN.\n"
    "You are the terminal epistemic synthesis agent.\n"
    "Your goal is NOT a confident verdict. Your goal is a calibrated epistemic map.\n\n"
    "Produce the following in order:\n"
    "1. CRUXES: The 2-3 specific factual or inferential questions where resolution "
    "would most shift the overall probability. Be specific — name the question, "
    "not the theme.\n"
    "2. EVIDENCE QUALITY: For each major evidence stream in the prior analysis, "
    "rate its quality: strong / weak / contested / missing. Name the specific "
    "weakness or strength.\n"
    "3. CORRELATED EVIDENCE: Identify at least one pair of evidence streams that "
    "appear independent but share a methodological assumption, source, or "
    "selection mechanism. Explain why this matters for the overall estimate.\n"
    "4. CALIBRATED ASSESSMENT: Give a probability range (not a point estimate) "
    "with explicit conditions stated. E.g. '55-70% for hypothesis A, conditional "
    "on X being accurately measured and Y not being systematically biased.' "
    "A range is required. Refusing to estimate scores zero.\n"
    "5. SETTLED vs PERFORMED: Distinguish what has actually been resolved by "
    "the evidence from what was merely performed as resolved. State at least one "
    "open question that the current evidence cannot close.\n\n"
    "Preserve uncertainty where it is warranted. Do not collapse to false certainty."
)

# JSON variant of the epistemic synthesis prompt — instructs structured output.
# Used in run_kalibr_chain_epistemic to produce parseable EpistemicMap artifacts.
# Falls back gracefully: if the model produces prose instead of JSON, the run
# still scores normally; map_parsed=False is recorded for analysis.
EPISTEMIC_SYNTHESIS_PROMPT_JSON = (
    "OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN.\n"
    "You are the terminal epistemic synthesis agent.\n"
    "Your goal is NOT a confident verdict. Your goal is a calibrated epistemic map.\n\n"
    "Produce a valid JSON object matching this exact schema:\n"
    f"{EPISTEMIC_MAP_JSON_SCHEMA}\n\n"
    "Rules:\n"
    "- range_low and range_high are integers 0-100 (probability percent)\n"
    "- Include 2-3 cruxes, 3-5 evidence_streams, at least 1 correlated_pair\n"
    "- Wide probability ranges are correct when warranted — do not collapse to false certainty\n"
    "- Output ONLY the JSON object — no prose before or after"
)

ALL_SCENARIOS = list(EPISTEMIC_SCENARIOS.keys())


def _save_epistemic_map(run_id: str, emap: EpistemicMap) -> None:
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    path = MAPS_DIR / f"{run_id}.json"
    path.write_text(emap.model_dump_json(indent=2))


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


def _score(run_id: str, scenario, transcript: str, judges: list, topology: str) -> float:
    evals = score_transcript_panel(
        run_id=run_id,
        phase=scenario.phase,
        transcript=transcript,
        rubric=scenario.rubric,
        n_judges=len(judges),
        judge_agents=judges,
        topology=topology,
        team_size=2,
    )
    return sum(e.task_score for e in evals) / len(evals)


def run_kalibr_chain_epistemic(scenario_id: str, rep: int, rep_seed: int) -> dict | None:
    """Chain-2 + epistemic synthesis prompt (JSON output → EpistemicMap artifact)."""
    run_id   = str(uuid.uuid4())
    scenario = EPISTEMIC_SCENARIOS[scenario_id]
    pool     = initialise_pool(seed=rep_seed)
    workers  = [a for a in pool if not a.is_judge]
    judges   = [a for a in pool if a.is_judge]
    team, captain_id = draft_team(workers, 2, scenario.task_dimensions, "drafted")

    try:
        state = run_simulation(
            agents=team,
            scenario_brief=scenario.brief,
            phase=scenario.phase,
            topology="chain",
            chain_handoff_prompts={1: EPISTEMIC_SYNTHESIS_PROMPT_JSON},
            default_handoff=None,
        )
    except Exception as e:
        print(f"    ERROR in simulation: {e}")
        traceback.print_exc()
        return None

    transcript = build_transcript(state["messages"])

    # Attempt structured EpistemicMap extraction from synthesis output
    last_assistant = next(
        (m["content"] for m in reversed(state["messages"])
         if isinstance(m, dict) and m.get("role") == "assistant"),
        ""
    )
    emap = parse_epistemic_map(last_assistant)
    if emap is not None:
        emap.case_id = scenario_id
        _save_epistemic_map(run_id, emap)

    try:
        mean_score = _score(run_id, scenario, transcript, judges, topology="chain")
    except Exception as e:
        print(f"    ERROR in judge panel: {e}")
        return None

    return {
        "run_id":      run_id,
        "condition":   "kalibr-chain",
        "scenario_id": scenario_id,
        "rep":         rep,
        "captain_id":  captain_id,
        "task_score":  mean_score,
        "turn_count":  state["turn_count"],
        "n_calls":     2,
        "synthesis":   "epistemic",
        "map_parsed":  emap is not None,
        "model":       os.getenv("MODEL", "unknown"),
        "provider":    os.getenv("MODEL_PROVIDER", "unknown"),
    }


def run_single_agent_epistemic(scenario_id: str, rep: int, rep_seed: int) -> dict | None:
    """Single agent with self-review using epistemic synthesis prompt. 2 calls, 1 agent.

    Uses flat topology with max_rounds=1 and a closing synthesis prompt:
    - Call 1: agent produces initial analysis (flat round 0)
    - Call 2: same agent runs EPISTEMIC_SYNTHESIS_PROMPT (closing/synth node)
    This is the compute-matched baseline for kalibr-chain: same 2 calls, 1 agent.
    """
    run_id   = str(uuid.uuid4())
    scenario = EPISTEMIC_SCENARIOS[scenario_id]
    pool     = initialise_pool(seed=rep_seed)
    workers  = [a for a in pool if not a.is_judge]
    judges   = [a for a in pool if a.is_judge]

    team, captain_id = draft_team(workers, 1, scenario.task_dimensions, "drafted")

    try:
        initial_state: SimState = {
            "run_id": run_id,
            "phase": scenario.phase,
            "scenario_brief": scenario.brief,
            "messages": [{"role": "user", "content": scenario.brief}],
            "turn_count": 0,
            "token_usage": {},
            "output_token_usage": {},
            "cull_events": [],
            "active_agent_ids": [team[0].agent_id],
            "routing_log": [],
            "state_snapshot": None,
        }
        graph = build_flat_graph(
            agents=team,
            max_rounds=1,
            closing_prompt=EPISTEMIC_SYNTHESIS_PROMPT,
        )
        compiled = graph.compile()
        final_state = compiled.invoke(initial_state)
    except Exception as e:
        print(f"    ERROR in single-agent simulation: {e}")
        traceback.print_exc()
        return None

    transcript = build_transcript(final_state["messages"])
    try:
        mean_score = _score(run_id, scenario, transcript, judges, topology="chain")
    except Exception as e:
        print(f"    ERROR in judge panel: {e}")
        return None

    return {
        "run_id":      run_id,
        "condition":   "single-agent",
        "scenario_id": scenario_id,
        "rep":         rep,
        "captain_id":  captain_id,
        "task_score":  mean_score,
        "turn_count":  final_state["turn_count"],
        "n_calls":     2,
        "synthesis":   "epistemic",
        "map_parsed":  False,
        "model":       os.getenv("MODEL", "unknown"),
        "provider":    os.getenv("MODEL_PROVIDER", "unknown"),
    }


def run_flat_no_handoff(scenario_id: str, rep: int, rep_seed: int) -> dict | None:
    """Flat round-table, 2 rounds, no synthesis step. Framework default baseline."""
    run_id   = str(uuid.uuid4())
    scenario = EPISTEMIC_SCENARIOS[scenario_id]
    pool     = initialise_pool(seed=rep_seed)
    workers  = [a for a in pool if not a.is_judge]
    judges   = [a for a in pool if a.is_judge]
    team, captain_id = draft_team(workers, 2, scenario.task_dimensions, "drafted")

    try:
        state = run_simulation(
            agents=team,
            scenario_brief=scenario.brief,
            phase=scenario.phase,
            topology="flat",
            flat_rounds=2,
        )
    except Exception as e:
        print(f"    ERROR in simulation: {e}")
        traceback.print_exc()
        return None

    transcript = build_transcript(state["messages"])
    try:
        mean_score = _score(run_id, scenario, transcript, judges, topology="flat")
    except Exception as e:
        print(f"    ERROR in judge panel: {e}")
        return None

    return {
        "run_id":      run_id,
        "condition":   "flat-no-handoff",
        "scenario_id": scenario_id,
        "rep":         rep,
        "captain_id":  captain_id,
        "task_score":  mean_score,
        "turn_count":  state["turn_count"],
        "n_calls":     4,
        "synthesis":   "none",
        "map_parsed":  False,
        "model":       os.getenv("MODEL", "unknown"),
        "provider":    os.getenv("MODEL_PROVIDER", "unknown"),
    }


def run_kalibr_chain_decisive(scenario_id: str, rep: int, rep_seed: int) -> dict | None:
    """Chain-2 + DECISIVE synthesis prompt — ablation control for H2.

    Identical architecture to run_kalibr_chain_epistemic but uses the decisive
    synthesis prompt from Phases 5/8/9 instead of the epistemic one.
    Phase 9 showed this prompt costs −13.3 pts on reflective tasks (s03_post_mortem).
    This condition tests whether the same penalty applies to Phase E scenarios directly,
    making H2 (prompt specificity) testable within Phase E rather than inferred
    cross-experiment.

    Expected result: scores below kalibr-chain/epistemic by a similar margin.
    If the gap is not observed, the decisive prompt is not the mechanism.
    """
    run_id   = str(uuid.uuid4())
    scenario = EPISTEMIC_SCENARIOS[scenario_id]
    pool     = initialise_pool(seed=rep_seed)
    workers  = [a for a in pool if not a.is_judge]
    judges   = [a for a in pool if a.is_judge]
    team, captain_id = draft_team(workers, 2, scenario.task_dimensions, "drafted")

    try:
        state = run_simulation(
            agents=team,
            scenario_brief=scenario.brief,
            phase=scenario.phase,
            topology="chain",
            chain_handoff_prompts={1: DECISIVE_SYNTHESIS_PROMPT},
            default_handoff=None,
        )
    except Exception as e:
        print(f"    ERROR in simulation: {e}")
        traceback.print_exc()
        return None

    transcript = build_transcript(state["messages"])
    try:
        mean_score = _score(run_id, scenario, transcript, judges, topology="chain")
    except Exception as e:
        print(f"    ERROR in judge panel: {e}")
        return None

    return {
        "run_id":      run_id,
        "condition":   "kalibr-chain/decisive",
        "scenario_id": scenario_id,
        "rep":         rep,
        "captain_id":  captain_id,
        "task_score":  mean_score,
        "turn_count":  state["turn_count"],
        "n_calls":     2,
        "synthesis":   "decisive",
        "map_parsed":  False,
        "model":       os.getenv("MODEL", "unknown"),
        "provider":    os.getenv("MODEL_PROVIDER", "unknown"),
    }


CONDITION_RUNNERS = {
    "kalibr-chain":          run_kalibr_chain_epistemic,
    "kalibr-chain/decisive": run_kalibr_chain_decisive,
    "single-agent":          run_single_agent_epistemic,
    "flat-no-handoff":       run_flat_no_handoff,
}


def main():
    parser = argparse.ArgumentParser(
        description="Phase E: Epistemic Investigation Architecture (FLF Competition)"
    )
    parser.add_argument("--reps",       type=int,   default=5)
    parser.add_argument("--scenarios",  nargs="+",  default=ALL_SCENARIOS,
                        help="Scenario IDs to run (default: all)")
    parser.add_argument("--conditions", nargs="+",  default=list(CONDITION_RUNNERS.keys()),
                        help="Conditions to run (default: all)")
    args = parser.parse_args()

    model    = os.getenv("MODEL",          "gemini-2.5-flash")
    provider = os.getenv("MODEL_PROVIDER", "gemini")

    # Support both full IDs ("e01_covid_origins") and short prefixes ("e01")
    def _resolve(s: str) -> str | None:
        if s in EPISTEMIC_SCENARIOS:
            return s
        matches = [k for k in EPISTEMIC_SCENARIOS if k.startswith(s)]
        return matches[0] if len(matches) == 1 else None

    resolved  = [_resolve(s) for s in args.scenarios]
    scenarios = [s for s in resolved if s is not None]
    if len(scenarios) != len(args.scenarios):
        bad = [orig for orig, res in zip(args.scenarios, resolved) if res is None]
        print(f"WARNING: unrecognised scenario(s) ignored: {bad}")
        print(f"Valid IDs: {ALL_SCENARIOS}")
    conditions = [c for c in args.conditions if c in CONDITION_RUNNERS]
    done       = _load_done()
    total      = len(conditions) * len(scenarios) * args.reps

    print("Phase E: Epistemic Investigation Architecture")
    print("FLF Epistemic Case Study Competition")
    print(f"Model:      {model} ({provider})")
    print(f"Scenarios:  {scenarios}")
    print(f"Conditions: {conditions}")
    print(f"Reps:       {args.reps}")
    print(f"Total runs: {total}")
    print(f"Done:       {len(done)}")
    print("=" * 60)
    print()
    print("Synthesis prompts:")
    print("  kalibr-chain          → EPISTEMIC_SYNTHESIS_PROMPT_JSON (calibrated uncertainty + JSON)")
    print("  kalibr-chain/decisive → DECISIVE_SYNTHESIS_PROMPT (ablation: Phase 9 prompt on epistemic tasks)")
    print("  single-agent          → EPISTEMIC_SYNTHESIS_PROMPT (self-review, prose)")
    print("  flat-no-handoff       → none (framework default baseline)")
    print("=" * 60)

    completed = 0
    for cond_name in conditions:
        print(f"\n=== {cond_name} ===")
        for scenario_id in scenarios:
            scenario = EPISTEMIC_SCENARIOS[scenario_id]
            print(f"  Scenario: {scenario_id} — {scenario.brief[:60]}...")
            for rep in range(args.reps):
                key = f"{cond_name}::{scenario_id}::{rep}"
                completed += 1
                if key in done:
                    print(f"    [{completed}/{total}] rep{rep} — SKIP")
                    continue

                print(f"    [{completed}/{total}] rep{rep} ...", end="", flush=True)
                scenario_idx = ALL_SCENARIOS.index(scenario_id)
                rep_seed     = SEED + scenario_idx * args.reps + rep
                rec          = CONDITION_RUNNERS[cond_name](scenario_id, rep, rep_seed)

                if rec is None:
                    print(" ERROR")
                    continue

                _append(rec)
                done.add(key)
                print(f" {rec['task_score']:.1f}")
                time.sleep(DELAY_SECS)

    print(f"\n{'='*60}")
    print(f"Done. Results in {RESULTS_FILE}")
    print("Run: python phases/phase_e/analyze_phase_e.py")


if __name__ == "__main__":
    main()
