#!/usr/bin/env python3
"""
Cross-model topology replication.

Runs the topology finding (chain vs flat) across model families to test
whether sequential commitment outperforming flat deliberation is
architectural or model-specific.

Usage:
    python run_cross_model.py --provider anthropic
    python run_cross_model.py --provider gemini

24 combinations per provider:
    4 scenarios × 3 team sizes (2, 4, 8) × 2 topologies × 1 composition (drafted)

Judges always run on Gemini for consistent cross-model evaluation.
Results stored with model_family tag for stratified analysis.
"""
from __future__ import annotations
import argparse
import os
import re
import time
import traceback
import uuid
from dotenv import load_dotenv

load_dotenv()

from google.genai.errors import ClientError, ServerError
from src.agents.pool import initialise_pool
from src.orchestration.engine import run_simulation
from src.evaluation.judge import score_transcript_panel
from src.scenarios import ALL_SCENARIOS
from src.telemetry.database import insert_run, insert_evaluation, already_completed
from run_simulation import draft_team, build_transcript

SCENARIOS    = list(ALL_SCENARIOS.keys())
TEAM_SIZES   = [2, 4, 8]          # skip 1 (confounded baseline) and 16 (cost)
TOPOLOGIES   = ["chain", "flat"]
COMPOSITION  = "drafted"           # topology finding only — composition held constant
SEED         = 42
DELAY_SECS   = 5
MAX_RETRIES  = 6
FLAT_ROUNDS  = 2

LOG_FILE = "cross_model.log"

MODEL_CONFIGS = {
    "gemini":    {"MODEL": "gemini-2.5-flash",  "MODEL_PROVIDER": "gemini"},
    "anthropic": {"MODEL": "claude-sonnet-4-6", "MODEL_PROVIDER": "anthropic"},
}


def log(msg: str):
    print(msg, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def all_combinations():
    for scenario_id in SCENARIOS:
        for team_size in TEAM_SIZES:
            for topology in TOPOLOGIES:
                yield scenario_id, team_size, topology, COMPOSITION


def run_one(scenario_id, team_size, topology, composition, model_family, run_index, total):
    scenario = ALL_SCENARIOS[scenario_id]
    run_id   = str(uuid.uuid4())

    log(f"\n[{run_index}/{total}] {scenario_id} | size={team_size} | {topology} | {model_family}")

    if already_completed(scenario_id, topology, composition, team_size, model_family):
        log("  SKIPPED — already completed")
        return None

    pool    = initialise_pool(seed=SEED)
    workers = [a for a in pool if not a.is_judge]
    judges  = [a for a in pool if a.is_judge]

    team, captain_id = draft_team(workers, team_size, scenario.task_dimensions, composition)
    log(f"  captain={captain_id} team={[a.agent_id for a in team]}")

    final_state = run_simulation(
        agents=team,
        scenario_brief=scenario.brief,
        phase=scenario.phase,
        topology=topology,
        flat_rounds=FLAT_ROUNDS,
    )

    transcript   = build_transcript(final_state["messages"])
    total_tokens = sum(final_state["token_usage"].values())
    log(f"  turns={final_state['turn_count']} tokens={total_tokens} culls={[e['agent_id'] for e in final_state['cull_events']]}")

    insert_run(
        run_id=run_id,
        scenario_id=scenario_id,
        composition_matrix={a.agent_id: a.to_dict() for a in team},
        topology=topology,
        task_phase=scenario.phase,
        scenario_category=scenario.category,
        composition_condition=composition,
        team_size=team_size,
        captain_agent_id=captain_id,
        draft_order=1,
        token_cost=total_tokens,
        turns_to_complete=final_state["turn_count"],
        cull_events=final_state["cull_events"],
        state_snapshot=None,
        model_family=model_family,
    )

    # Judges always run on Gemini regardless of worker provider
    saved_provider = os.environ.get("MODEL_PROVIDER", "gemini")
    saved_model    = os.environ.get("MODEL", "gemini-2.5-flash")
    os.environ["MODEL_PROVIDER"] = "gemini"
    os.environ["MODEL"]          = "gemini-2.5-flash"

    evaluations = score_transcript_panel(
        run_id=run_id,
        phase=scenario.phase,
        transcript=transcript,
        rubric=scenario.rubric,
        n_judges=len(judges),
    )

    os.environ["MODEL_PROVIDER"] = saved_provider
    os.environ["MODEL"]          = saved_model

    scores    = [e.task_score for e in evaluations]
    mean_score = sum(scores) / len(scores)
    log(f"  scores={scores} mean={mean_score:.1f}")

    for i, ev in enumerate(evaluations):
        insert_evaluation(run_id=run_id, judge_index=i, scores=ev.model_dump())

    return mean_score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--provider",
        choices=list(MODEL_CONFIGS.keys()),
        required=True,
        help="Model provider to use for worker agents.",
    )
    args = parser.parse_args()

    config = MODEL_CONFIGS[args.provider]
    os.environ["MODEL"]          = config["MODEL"]
    os.environ["MODEL_PROVIDER"] = config["MODEL_PROVIDER"]

    combos = list(all_combinations())
    total  = len(combos)

    log(f"\nCross-model run | provider={args.provider} | model={config['MODEL']}")
    log(f"Combinations: {total} | seed={SEED} | judges always on gemini-2.5-flash")
    log("=" * 60)

    passed = failed = 0

    for i, (scenario_id, team_size, topology, composition) in enumerate(combos, 1):
        attempt = 0
        while attempt <= MAX_RETRIES:
            try:
                run_one(scenario_id, team_size, topology, composition, args.provider, i, total)
                passed += 1
                break
            except ClientError as e:
                if e.status_code == 429:
                    match = re.search(r'retry[^0-9]*(\d+(?:\.\d+)?)\s*s', str(e), re.IGNORECASE)
                    wait  = float(match.group(1)) + 5 if match else 60
                    attempt += 1
                    if attempt > MAX_RETRIES:
                        failed += 1
                        log(f"  RATE LIMITED — giving up after {MAX_RETRIES} retries")
                        break
                    log(f"  RATE LIMITED — waiting {wait:.0f}s (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(wait)
                else:
                    failed += 1
                    log(f"  ERROR: {e}")
                    break
            except ServerError:
                attempt += 1
                if attempt > MAX_RETRIES:
                    failed += 1
                    log(f"  SERVER ERROR — giving up after {MAX_RETRIES} retries")
                    break
                wait = 30 * attempt
                log(f"  SERVER ERROR — waiting {wait}s (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(wait)
            except Exception as e:
                failed += 1
                log(f"  ERROR: {e}\n{traceback.format_exc()}")
                break

        if i < total:
            time.sleep(DELAY_SECS)

    log("\n" + "=" * 60)
    log(f"DONE: {passed} passed, {failed} failed | provider={args.provider}")


if __name__ == "__main__":
    main()
