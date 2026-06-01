#!/usr/bin/env python3
# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Phase 9: Kalibr Orchestration vs Grok Multi-Agent Panel.

Same backend model (Grok), different orchestration layers:

    kalibr-chain    — Kalibr chain-2 + synthesis prompt on grok-4.20-0309-reasoning.
                      Explicit synthesis architecture; our orchestration.
                      Reasoning variant used to match panel capability — the panel
                      likely uses reasoning internally; using non-reasoning would
                      conflate orchestration effect with reasoning gap.

    grok-panel      — xAI's internal multi-agent panel via a single API call.
                      Black-box orchestration; their architecture.
                      Model: grok-4.20-multi-agent-0309 (same generation, different orchestration).
                      ~4 internal agents; NOT compute-matched to kalibr-chain's 2 calls.

Both conditions use the same Grok model as the underlying LLM.
Both scored by the same 3-judge panel on the same judgment scenarios.

The question: does Kalibr's explicit synthesis architecture outperform
xAI's internal panel when both use the same base model?

Setup:
    Set XAI_API_KEY, MODEL_PROVIDER=xai, MODEL=<grok-model> in .env.
    Optionally set GROK_PANEL_MODEL=<grok-multi-agent-model> if the panel
    endpoint uses a different model name than the single-call model.

    Verify your panel model name at console.x.ai before running —
    multi-agent endpoint names may differ from standard model names.

Usage:
    python phases/phase9/run_phase9.py
    python phases/phase9/run_phase9.py --reps 5
    python phases/phase9/run_phase9.py --reps 5 --skip-panel
        (--skip-panel runs only kalibr-chain; useful if panel endpoint
         is unavailable or unverified)

Output: results/phase9.jsonl
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
from src.orchestration.engine import run_simulation, _call_agent
from src.evaluation.judge import score_transcript_panel
from src.scenarios import ALL_SCENARIOS

RESULTS_FILE     = Path("results/phase9.jsonl")
SEED             = 42
DELAY_SECS       = 2

# Kalibr synthesis prompt — identical to Phase 5 and Phase 8
SYNTHESIS_PROMPT = (
    "OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN.\n"
    "You are the terminal synthesis agent. The prior analysis is above.\n"
    "You must:\n"
    "1. Identify what the prior analysis got right\n"
    "2. Identify what it missed or got wrong\n"
    "3. Produce a COMPLETE, DEFINITIVE final answer — strictly better\n"
    "Do not summarise. Close every open question. Be decisive."
)

# Judgment scenarios only — same as Phase 5/8
JUDGMENT_SCENARIOS = [
    s for s in ALL_SCENARIOS
    if ALL_SCENARIOS[s].phase in ("phase1", "phase5", "phase8", "kalibr")
]


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


def run_kalibr_chain(scenario_id: str, rep: int, rep_seed: int) -> dict | None:
    """Kalibr chain-2 + synthesis prompt, Grok as worker model."""
    run_id   = str(uuid.uuid4())
    scenario = ALL_SCENARIOS[scenario_id]
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
            chain_handoff_prompts={1: SYNTHESIS_PROMPT},
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
        "condition":   "kalibr-chain",
        "scenario_id": scenario_id,
        "rep":         rep,
        "captain_id":  captain_id,
        "task_score":  mean_score,
        "turn_count":  state["turn_count"],
        "n_calls":     2,
        "model":       os.getenv("MODEL", "unknown"),
        "provider":    os.getenv("MODEL_PROVIDER", "unknown"),
    }


def run_grok_panel(scenario_id: str, rep: int, rep_seed: int) -> dict | None:
    """
    xAI's internal multi-agent panel — single API call, their orchestration.

    Uses the Responses API (client.responses.create) — the panel model does NOT
    work reliably on /v1/chat/completions. See xAI docs for detail.

    NOTE: NOT compute-matched to kalibr-chain.
    Grok panel runs 4 agents internally by default (up to 16 at high effort).
    kalibr-chain makes 2 LLM calls. Record n_calls=1 (our API calls) and
    n_internal_agents=4 so the analysis can flag this explicitly.

    Set GROK_PANEL_MODEL=grok-4.20-multi-agent-0309 in .env for reproducibility.
    """
    from openai import OpenAI

    panel_model = os.getenv("GROK_PANEL_MODEL", "grok-4.20-multi-agent-0309")
    api_key     = os.getenv("XAI_API_KEY")
    if not api_key:
        raise EnvironmentError("XAI_API_KEY not set")

    run_id   = str(uuid.uuid4())
    scenario = ALL_SCENARIOS[scenario_id]
    pool     = initialise_pool(seed=rep_seed)
    judges   = [a for a in pool if a.is_judge]

    client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

    try:
        response = client.responses.create(
            model=panel_model,
            input=[{"role": "user", "content": scenario.brief}],
            temperature=0.0,
        )
        output        = response.output_text or ""
        prompt_tokens = getattr(getattr(response, "usage", None), "input_tokens", 0)
        output_tokens = getattr(getattr(response, "usage", None), "output_tokens", 0)
    except Exception as e:
        print(f"    ERROR calling Grok panel: {e}")
        traceback.print_exc()
        return None

    messages = [
        {"role": "user",      "content": scenario.brief},
        {"role": "assistant", "content": f"[grok-panel]: {output}"},
    ]
    transcript = build_transcript(messages)

    try:
        mean_score = _score(run_id, scenario, transcript, judges, topology="chain")
    except Exception as e:
        print(f"    ERROR in judge panel: {e}")
        return None

    return {
        "run_id":             run_id,
        "condition":          "grok-panel",
        "scenario_id":        scenario_id,
        "rep":                rep,
        "captain_id":         None,
        "task_score":         mean_score,
        "turn_count":         1,
        "n_calls":            1,       # our API calls
        "n_internal_agents":  4,       # xAI default; NOT compute-matched to kalibr-chain
        "model":              panel_model,
        "provider":           "xai",
        "prompt_tokens":      prompt_tokens,
        "output_tokens":      output_tokens,
    }


def main():
    parser = argparse.ArgumentParser(description="Phase 9: Kalibr vs Grok Panel")
    parser.add_argument("--reps",        type=int,  default=5)
    parser.add_argument("--skip-panel",  action="store_true",
                        help="Run only kalibr-chain (skips grok-panel condition)")
    args = parser.parse_args()

    provider = os.getenv("MODEL_PROVIDER", "gemini")
    model    = os.getenv("MODEL", "gemini-2.5-flash")
    if provider != "xai":
        print(f"WARNING: MODEL_PROVIDER={provider}, MODEL={model}")
        print("Phase 9 is designed to run with MODEL_PROVIDER=xai.")
        print("Set MODEL_PROVIDER=xai and MODEL=<grok-model> in .env to use Grok as the backend.")
        print("Continuing with current provider for kalibr-chain condition.")

    scenarios  = JUDGMENT_SCENARIOS or list(ALL_SCENARIOS.keys())
    conditions = ["kalibr-chain"] if args.skip_panel else ["kalibr-chain", "grok-panel"]
    done       = _load_done()
    total      = len(conditions) * len(scenarios) * args.reps
    completed  = 0

    print("Phase 9: Kalibr Orchestration vs Grok Multi-Agent Panel")
    print(f"Backend model:  {model} ({provider})")
    panel_model = os.getenv("GROK_PANEL_MODEL", model)
    if "grok-panel" in conditions:
        print(f"Panel model:    {panel_model}")
    print(f"Scenarios:      {scenarios}")
    print(f"Reps:           {args.reps}")
    print(f"Total runs:     {total}")
    print(f"Already done:   {len(done)}")
    print("=" * 60)

    runners = {
        "kalibr-chain": run_kalibr_chain,
        "grok-panel":   run_grok_panel,
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
                scenario_idx = scenarios.index(scenario_id)
                rep_seed     = SEED + scenario_idx * args.reps + rep
                rec          = runners[cond_name](scenario_id, rep, rep_seed)

                if rec is None:
                    print(" ERROR")
                    continue

                _append(rec)
                done.add(key)
                print(f" {rec['task_score']:.1f}")
                time.sleep(DELAY_SECS)

    print(f"\n{'='*60}")
    print(f"Done. Results in {RESULTS_FILE}")
    print("Run: python phases/phase9/analyze_phase9.py")


if __name__ == "__main__":
    main()
