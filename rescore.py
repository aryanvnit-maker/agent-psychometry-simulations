#!/usr/bin/env python3
"""
Re-score stored transcripts with the current judge, without re-running simulations.

Requires runs to have been stored with transcripts (run_all.py v2+).
Old runs without stored transcripts must be re-run via run_all.py.

Usage:
    python rescore.py                          # re-score all runs with transcripts
    python rescore.py --model-family gemini    # one model family only
    python rescore.py --topology chain         # one topology only
    python rescore.py --dry-run                # show what would be re-scored
"""
from __future__ import annotations
import argparse
import os
import time
import traceback
from dotenv import load_dotenv
load_dotenv()

from src.telemetry.database import load_runs_with_transcripts, delete_evaluations, insert_evaluation
from src.evaluation.judge import score_transcript_panel
from src.scenarios import ALL_SCENARIOS

# Judges always run on Gemini for consistent cross-model evaluation
JUDGE_MODEL    = "gemini-2.5-flash"
JUDGE_PROVIDER = "gemini"
N_JUDGES       = 3
DELAY_SECS     = 3

LOG_FILE = "rescore.log"


def log(msg: str):
    print(msg, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-family")
    parser.add_argument("--topology", choices=["chain", "flat"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Force Gemini for judging regardless of env
    os.environ["MODEL_PROVIDER"] = JUDGE_PROVIDER
    os.environ["MODEL"]          = JUDGE_MODEL

    runs = load_runs_with_transcripts(model_family=args.model_family)

    if args.topology:
        runs = [r for r in runs if r["topology"] == args.topology]

    log(f"Runs with stored transcripts: {len(runs)}")

    if args.dry_run:
        for r in runs:
            log(f"  {r['run_id']} | {r['scenario_id']} | {r['topology']} | {r['model_family']}")
        log("DRY RUN — no changes made.")
        return

    if not runs:
        log("No runs with stored transcripts found. Re-run the batch first.")
        return

    passed = failed = 0

    for i, run in enumerate(runs, 1):
        run_id     = run["run_id"]
        scenario   = ALL_SCENARIOS.get(run["scenario_id"])
        if scenario is None:
            log(f"[{i}/{len(runs)}] SKIP — unknown scenario {run['scenario_id']}")
            continue

        log(f"\n[{i}/{len(runs)}] {run['scenario_id']} | {run['topology']} | {run['model_family']} | {run_id}")

        try:
            evaluations = score_transcript_panel(
                run_id=run_id,
                phase=run["task_phase"],
                transcript=run["transcript"],
                rubric=scenario.rubric,
                n_judges=N_JUDGES,
            )

            delete_evaluations(run_id)

            scores = [e.task_score for e in evaluations]
            for j, ev in enumerate(evaluations):
                insert_evaluation(run_id=run_id, judge_index=j, scores=ev.model_dump())

            log(f"  scores={scores} mean={sum(scores)/len(scores):.1f}")
            passed += 1

        except Exception as e:
            failed += 1
            log(f"  ERROR: {e}\n{traceback.format_exc()}")

        if i < len(runs):
            time.sleep(DELAY_SECS)

    log("\n" + "=" * 60)
    log(f"RESCORE COMPLETE: {passed} passed, {failed} failed out of {len(runs)}")


if __name__ == "__main__":
    main()
