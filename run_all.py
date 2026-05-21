#!/usr/bin/env python3
"""
Runs all experiment combinations and logs results.

Usage:
    python run_all.py                      # chain topology only (default)
    python run_all.py --topology flat      # flat topology only
    python run_all.py --topology all       # both topologies

Output is written to results.log in real time.
Press Ctrl+C to stop at any time — completed runs are already saved to Supabase.
"""
from __future__ import annotations
import argparse
import re
import time
import traceback
import uuid
from itertools import product
from dotenv import load_dotenv

load_dotenv()

from google.genai.errors import ClientError
from src.agents.pool import initialise_pool, get_workers, get_judges
from src.orchestration.engine import run_simulation
from src.evaluation.judge import score_transcript_panel
from src.scenarios import ALL_SCENARIOS
from src.telemetry.database import insert_run, insert_evaluation, already_completed
from run_simulation import draft_team, build_transcript

SCENARIOS    = list(ALL_SCENARIOS.keys())
TEAM_SIZES   = [1, 2, 4, 8, 16]
TOPOLOGIES   = ["chain"]           # overridden at runtime by --topology arg
COMPOSITIONS = ["drafted", "homogeneous", "founder_brained"]
SEED         = 42
DELAY_SECS   = 5    # pause between runs to respect API rate limits
MAX_RETRIES  = 6    # max retries on 429 before giving up on a single run
FLAT_ROUNDS  = 2    # rounds per flat-topology simulation

LOG_FILE = "results.log"


def log(msg: str):
    print(msg, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def all_combinations():
    for scenario_id, team_size, topology, composition in product(
        SCENARIOS, TEAM_SIZES, TOPOLOGIES, COMPOSITIONS
    ):
        # Team of 1 has no meaningful composition variation — run drafted only
        if team_size == 1 and composition != "drafted":
            continue
        yield scenario_id, team_size, topology, composition


def run_one(scenario_id, team_size, topology, composition, run_index, total):
    scenario = ALL_SCENARIOS[scenario_id]
    run_id = str(uuid.uuid4())

    log(f"\n[{run_index}/{total}] {scenario_id} | size={team_size} | {topology} | {composition}")

    if already_completed(scenario_id, topology, composition, team_size):
        log("  SKIPPED — already completed in Supabase")
        return None

    log(f"  run_id: {run_id}")

    pool = initialise_pool(seed=SEED)
    workers = [a for a in pool if not a.is_judge]
    judges  = [a for a in pool if a.is_judge]

    team, captain_id = draft_team(
        workers, team_size, scenario.task_dimensions, composition
    )
    log(f"  captain: {captain_id} | team: {[a.agent_id for a in team]}")

    final_state = run_simulation(
        agents=team,
        scenario_brief=scenario.brief,
        phase=scenario.phase,
        topology=topology,
        flat_rounds=FLAT_ROUNDS,
    )

    transcript  = build_transcript(final_state["messages"])
    total_tokens = sum(final_state["token_usage"].values())
    log(f"  turns={final_state['turn_count']} tokens={total_tokens} culls={[e['agent_id'] for e in final_state['cull_events']]}")

    composition_matrix = {a.agent_id: a.to_dict() for a in team}
    insert_run(
        run_id=run_id,
        scenario_id=scenario_id,
        composition_matrix=composition_matrix,
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
    )

    evaluations = score_transcript_panel(
        run_id=run_id,
        phase=scenario.phase,
        transcript=transcript,
        rubric=scenario.rubric,
        n_judges=len(judges),
    )

    scores = [e.task_score for e in evaluations]
    mean_score = sum(scores) / len(scores)
    log(f"  scores={scores} mean={mean_score:.1f}")

    for i, ev in enumerate(evaluations):
        insert_evaluation(run_id=run_id, judge_index=i, scores=ev.model_dump())

    return mean_score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--topology",
        choices=["chain", "flat", "all"],
        default="chain",
        help="Which topology (or topologies) to run.",
    )
    args = parser.parse_args()

    global TOPOLOGIES  # noqa: PLW0603
    if args.topology == "all":
        TOPOLOGIES = ["chain", "flat"]
    else:
        TOPOLOGIES = [args.topology]

    combos = list(all_combinations())
    total  = len(combos)

    log(f"Starting batch: {total} runs | seed={SEED} | delay={DELAY_SECS}s between runs")
    log(f"Scenarios:    {SCENARIOS}")
    log(f"Team sizes:   {TEAM_SIZES}")
    log(f"Topologies:   {TOPOLOGIES}")
    log(f"Compositions: {COMPOSITIONS}")
    log("=" * 60)

    passed = 0
    failed = 0

    for i, (scenario_id, team_size, topology, composition) in enumerate(combos, 1):
        attempt = 0
        while attempt <= MAX_RETRIES:
            try:
                run_one(scenario_id, team_size, topology, composition, i, total)
                passed += 1
                break
            except ClientError as e:
                if e.status_code == 429:
                    # Extract retry delay from Gemini error message
                    match = re.search(r'retry[^0-9]*(\d+(?:\.\d+)?)\s*s', str(e), re.IGNORECASE)
                    wait = float(match.group(1)) + 5 if match else 60
                    attempt += 1
                    if attempt > MAX_RETRIES:
                        failed += 1
                        log(f"  FAILED after {MAX_RETRIES} retries — skipping")
                        break
                    log(f"  RATE LIMITED — waiting {wait:.0f}s then retrying (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(wait)
                else:
                    failed += 1
                    log(f"  ERROR: {e}")
                    break
            except Exception as e:
                failed += 1
                log(f"  ERROR: {e}")
                log(traceback.format_exc())
                log("  Skipping to next combination...")
                break

        if i < total:
            time.sleep(DELAY_SECS)

    log("\n" + "=" * 60)
    log(f"BATCH COMPLETE: {passed} passed, {failed} failed out of {total} runs")
    log("All results saved to Supabase.")


if __name__ == "__main__":
    main()
