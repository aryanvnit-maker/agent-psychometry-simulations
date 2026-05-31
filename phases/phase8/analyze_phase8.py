#!/usr/bin/env python3
# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Phase 8: Agent Diversity vs Structured Self-Refinement — Analysis

Reads results/phase8.jsonl and answers the core question:

    Does kalibr-chain (two DIFFERENT agents) outperform
    single-agent-refine (same agent twice)?

    Both conditions make exactly 2 LLM calls.
    If chain > refine: agent diversity adds genuine value.
    If tied: the synthesis step structure is all that matters.

Usage:
    python phases/phase8/analyze_phase8.py
"""
from __future__ import annotations
import json
import statistics
from collections import defaultdict
from pathlib import Path
from scipy import stats as scipy_stats

RESULTS_FILE = Path("results/phase8.jsonl")


def load() -> list[dict]:
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(f"{RESULTS_FILE} not found. Run run_phase8.py first.")
    records = []
    with RESULTS_FILE.open() as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except Exception:
                pass
    return records


def mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def stdev(vals: list[float]) -> float:
    return statistics.stdev(vals) if len(vals) > 1 else 0.0


def main():
    records = load()
    print(f"Loaded {len(records)} records from {RESULTS_FILE}")

    by_condition: dict[str, list[float]] = defaultdict(list)
    by_scenario:  dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for r in records:
        by_condition[r["condition"]].append(r["task_score"])
        by_scenario[r["scenario_id"]][r["condition"]].append(r["task_score"])

    print("\n" + "=" * 60)
    print("PHASE 8: AGENT DIVERSITY vs STRUCTURED SELF-REFINEMENT")
    print("Compute-matched: both conditions = 2 LLM calls")
    print("=" * 60)

    # ── Overall table ─────────────────────────────────────────────────────────
    print(f"\n{'Condition':<24} {'Calls':>5} {'N':>5} {'Mean':>7} {'Std':>6}")
    print("-" * 50)
    for cond in ["kalibr-chain", "single-agent-refine"]:
        vals = by_condition.get(cond, [])
        if vals:
            print(f"  {cond:<22} {'2':>5} {len(vals):>5} {mean(vals):>7.1f} {stdev(vals):>6.1f}")
        else:
            print(f"  {cond:<22} {'2':>5} {'0':>5} {'n/a':>7} {'n/a':>6}")

    # ── Primary comparison ────────────────────────────────────────────────────
    chain  = by_condition.get("kalibr-chain", [])
    refine = by_condition.get("single-agent-refine", [])

    print("\n── PRIMARY: kalibr-chain vs single-agent-refine (both 2 calls) ──")
    if chain and refine:
        delta = mean(chain) - mean(refine)
        t_stat, p_val = scipy_stats.ttest_ind(chain, refine, equal_var=False)
        print(f"  kalibr-chain:        {mean(chain):.1f}  (n={len(chain)}, sd={stdev(chain):.1f})")
        print(f"  single-agent-refine: {mean(refine):.1f}  (n={len(refine)}, sd={stdev(refine):.1f})")
        print(f"  Δ = {delta:+.1f} pts  (Welch t={t_stat:.2f}, p={p_val:.3f})")
        sig = "p<0.05 *" if p_val < 0.05 else ("p<0.10 +" if p_val < 0.10 else "n.s.")
        print(f"  Significance: {sig}")

        if delta > 10:
            verdict = "DIVERSITY CONFIRMED"
            detail  = (
                "Agent diversity adds genuine value beyond structured self-prompting.\n"
                "  Multi-agent architecture has a non-trivial moat.\n"
                "  A second perspective materially improves judgment quality."
            )
        elif delta > 3:
            verdict = "WEAK DIVERSITY SIGNAL"
            detail  = (
                "Small but positive diversity signal.\n"
                "  The synthesis step is primary; a different second agent adds marginal lift.\n"
                "  Product angle: structured refinement + diversity bonus."
            )
        elif delta >= -3:
            verdict = "TIED — SYNTHESIS IS ALL THAT MATTERS"
            detail  = (
                "Agent diversity does NOT add value beyond structured self-prompting.\n"
                "  A single agent with forced two-pass refinement matches multi-agent.\n"
                "  Product pivot: collapse-proof structured refinement, not swarm intelligence.\n"
                "  The SYNTHESIS PROMPT is the moat, not agent count."
            )
        else:
            verdict = "SINGLE-AGENT WINS"
            detail  = (
                "Self-refinement outperforms diversity.\n"
                "  A second agent introduces noise or incoherence that hurts synthesis.\n"
                "  Optimal architecture: single captain with structured self-correction."
            )

        print(f"\n  VERDICT: {verdict}")
        print(f"  {detail}")
    else:
        missing = []
        if not chain:
            missing.append("kalibr-chain")
        if not refine:
            missing.append("single-agent-refine")
        print(f"  Missing data for: {', '.join(missing)}")
        print(f"  Run run_phase8.py to completion before analyzing.")
        return

    # ── Per-scenario breakdown ─────────────────────────────────────────────────
    print("\n── Per-Scenario Breakdown ──")
    scenarios = sorted(by_scenario.keys())
    print(f"  {'Scenario':<30} {'chain':>9} {'refine':>9} {'Δ':>7}")
    print("  " + "-" * 57)
    for s in scenarios:
        c = by_scenario[s].get("kalibr-chain", [])
        r = by_scenario[s].get("single-agent-refine", [])
        c_str = f"{mean(c):.1f}" if c else "n/a"
        r_str = f"{mean(r):.1f}" if r else "n/a"
        d_str = f"{mean(c) - mean(r):+.1f}" if c and r else "n/a"
        print(f"  {s:<30} {c_str:>9} {r_str:>9} {d_str:>7}")

    # ── Consistency ──────────────────────────────────────────────────────────
    print("\n── Consistency: does chain win on EVERY scenario? ──")
    consistent = True
    for s in scenarios:
        c = by_scenario[s].get("kalibr-chain", [])
        r = by_scenario[s].get("single-agent-refine", [])
        if c and r:
            direction = "✓ chain" if mean(c) >= mean(r) else "✗ refine"
            print(f"  {s:<30} {direction}  ({mean(c):.1f} vs {mean(r):.1f})")
            if mean(c) < mean(r):
                consistent = False

    if consistent and chain and refine:
        print("\n  Diversity advantage is consistent across all scenarios.")
    elif chain and refine:
        print("\n  Mixed results — diversity advantage is scenario-dependent.")

    # ── Implication for product ───────────────────────────────────────────────
    print("\n── Implication for Product ──")
    if chain and refine:
        delta = mean(chain) - mean(refine)
        if delta > 3:
            print("  Ship multi-agent: the diverse second perspective earns its API cost.")
            print("  Marketing: 'two expert minds, one decisive answer'.")
        else:
            print("  Ship single-agent-refine: same output quality, half the complexity.")
            print("  Marketing: 'structured two-pass reasoning — collapse-proof by design'.")
            print("  Architecture: sell the synthesis prompt as the IP, not the agent count.")

    print()


if __name__ == "__main__":
    main()
