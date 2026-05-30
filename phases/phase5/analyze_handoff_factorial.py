#!/usr/bin/env python3
# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Phase 5: Topology × Handoff Factorial — Analysis

Reads results/handoff_factorial.jsonl and answers:

  1. Pure topology effect:   chain/no-handoff vs flat/no-handoff
     → Is the gap caused by topology alone, independent of handoff prompts?

  2. Pure handoff effect (chain):  chain/handoff vs chain/no-handoff
     → Does an explicit synthesis instruction add value within chain topology?

  3. Pure handoff effect (flat):   flat/handoff vs flat/no-handoff
     → Can a closing synthesis step rescue flat topology performance?

  4. Full comparison: all 4 conditions.
     → Which variable explains more variance: topology or handoff?

Causal interpretation:
  - If chain/no-handoff >> flat/no-handoff: topology is causal. Phase 1 claim holds.
  - If chain/no-handoff ≈ flat/no-handoff: handoff prompt explains Phase 1 gap.
  - If flat/handoff ≈ chain/handoff: topology is irrelevant; handoff is all that matters.

Usage:
    python phases/phase5/analyze_handoff_factorial.py
"""
from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict
import statistics

RESULTS_FILE = Path("results/handoff_factorial.jsonl")


def load() -> list[dict]:
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(f"{RESULTS_FILE} not found. Run run_handoff_factorial.py first.")
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


def print_condition_table(by_condition: dict[str, list[float]]) -> None:
    print(f"\n{'Condition':<22} {'N':>4} {'Mean':>7} {'Std':>6}")
    print("-" * 42)
    for cond in ["chain/handoff", "chain/no-handoff", "flat/handoff", "flat/no-handoff"]:
        vals = by_condition.get(cond, [])
        if vals:
            print(f"  {cond:<20} {len(vals):>4} {mean(vals):>7.1f} {stdev(vals):>6.1f}")


def delta(a: list[float], b: list[float]) -> str:
    d = mean(a) - mean(b)
    return f"{d:+.1f}"


def main():
    records = load()
    print(f"Loaded {len(records)} records from {RESULTS_FILE}")

    by_condition: dict[str, list[float]] = defaultdict(list)
    by_scenario:  dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for r in records:
        by_condition[r["condition"]].append(r["task_score"])
        by_scenario[r["scenario_id"]][r["condition"]].append(r["task_score"])

    print("\n" + "=" * 60)
    print("PHASE 5: TOPOLOGY × HANDOFF FACTORIAL")
    print("=" * 60)

    print_condition_table(by_condition)

    # ── Effect 1: Pure topology (no handoff on either side) ───────────────────
    cn  = by_condition.get("chain/no-handoff", [])
    fn  = by_condition.get("flat/no-handoff",  [])
    ch  = by_condition.get("chain/handoff",    [])
    fh  = by_condition.get("flat/handoff",     [])

    print("\n── Effect 1: Pure Topology (chain vs flat, no handoff on either) ──")
    print(f"  chain/no-handoff: {mean(cn):.1f}  flat/no-handoff: {mean(fn):.1f}  Δ={delta(cn, fn)}")
    if cn and fn:
        topo_gap = mean(cn) - mean(fn)
        if topo_gap > 10:
            print("  VERDICT: Topology IS causal. Chain outperforms flat without handoff prompts.")
            print("  Phase 1 topology claim is independent of the handoff confound.")
        elif topo_gap > 3:
            print("  VERDICT: Weak topology effect. Chain edges flat but gap is small.")
            print("  Handoff prompts likely amplify a smaller underlying topology effect.")
        else:
            print("  VERDICT: No topology effect without handoff prompts.")
            print("  Phase 1 gap was caused by handoff prompts, not topology.")

    # ── Effect 2: Handoff within chain ────────────────────────────────────────
    print("\n── Effect 2: Handoff Within Chain (chain/handoff vs chain/no-handoff) ──")
    print(f"  chain/handoff: {mean(ch):.1f}  chain/no-handoff: {mean(cn):.1f}  Δ={delta(ch, cn)}")
    if ch and cn:
        handoff_gain = mean(ch) - mean(cn)
        if handoff_gain > 5:
            print("  VERDICT: Handoff prompt adds meaningful value within chain topology.")
        elif handoff_gain > 0:
            print("  VERDICT: Marginal handoff gain within chain.")
        else:
            print("  VERDICT: No handoff gain within chain — topology alone drives performance.")

    # ── Effect 3: Handoff within flat ─────────────────────────────────────────
    print("\n── Effect 3: Handoff Within Flat (flat/handoff vs flat/no-handoff) ──")
    print(f"  flat/handoff: {mean(fh):.1f}  flat/no-handoff: {mean(fn):.1f}  Δ={delta(fh, fn)}")
    if fh and fn:
        flat_handoff_gain = mean(fh) - mean(fn)
        if flat_handoff_gain > 10:
            print("  VERDICT: Handoff alone significantly rescues flat topology.")
            print("  Key implication: flat topology's failure is primarily a commitment problem.")
        elif flat_handoff_gain > 3:
            print("  VERDICT: Handoff partially rescues flat, but doesn't close the gap to chain.")
        else:
            print("  VERDICT: Handoff does not rescue flat topology — structural problem beyond commitment.")

    # ── Effect 4: Best flat vs best chain (ceiling comparison) ───────────────
    print("\n── Effect 4: Best Flat vs Best Chain (ceiling comparison) ──")
    best_flat  = max(mean(fh), mean(fn))
    best_chain = max(mean(ch), mean(cn))
    print(f"  Best flat config:  {best_flat:.1f}  ({'flat/handoff' if mean(fh) > mean(fn) else 'flat/no-handoff'})")
    print(f"  Best chain config: {best_chain:.1f}  ({'chain/handoff' if mean(ch) > mean(cn) else 'chain/no-handoff'})")
    print(f"  Residual topology gap after optimising both: {best_chain - best_flat:+.1f}")

    # ── Per-scenario breakdown ─────────────────────────────────────────────────
    print("\n── Per-Scenario Breakdown ──")
    scenarios = sorted(by_scenario.keys())
    conds = ["chain/handoff", "chain/no-handoff", "flat/handoff", "flat/no-handoff"]
    header = f"  {'Scenario':<26}" + "".join(f"{c[:12]:>14}" for c in conds)
    print(header)
    for s in scenarios:
        row = f"  {s:<26}"
        for c in conds:
            vals = by_scenario[s].get(c, [])
            row += f"{mean(vals):>14.1f}" if vals else f"{'n/a':>14}"
        print(row)

    # ── Main conclusion ───────────────────────────────────────────────────────
    print("\n── Main Conclusion ──")
    if cn and fn and ch and fh:
        topo_effect    = mean(cn) - mean(fn)
        handoff_effect = ((mean(ch) - mean(cn)) + (mean(fh) - mean(fn))) / 2
        print(f"  Topology main effect (no-handoff):     {topo_effect:+.1f} pts")
        print(f"  Handoff main effect (avg both topos):  {handoff_effect:+.1f} pts")

        if topo_effect > handoff_effect:
            print("\n  TOPOLOGY dominates. Handoff prompts are secondary.")
            print("  Phase 1 core claim stands: topology is the primary determinant.")
        elif handoff_effect > topo_effect * 1.5:
            print("\n  HANDOFF dominates. Topology is secondary.")
            print("  Phase 1 finding should be reframed: structured handoffs drive performance,")
            print("  not topology per se. Chain implements handoffs naturally; flat requires them explicitly.")
        else:
            print("\n  BOTH contribute. Topology and handoff are independently meaningful.")
            print("  Optimal config: chain topology + explicit synthesis handoff (chain/handoff).")

    print()


if __name__ == "__main__":
    main()
