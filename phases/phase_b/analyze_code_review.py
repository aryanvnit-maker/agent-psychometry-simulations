#!/usr/bin/env python3
# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Phase B: Code Review — Analysis

Checks whether the Phase 1 topology finding (chain > flat) replicates
on real-world code review tasks.

Usage:
    python phases/phase_b/analyze_code_review.py
"""
from __future__ import annotations
import json
import statistics
from collections import defaultdict
from pathlib import Path

RESULTS_FILE = Path("results/code_review.jsonl")


def load() -> list[dict]:
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(f"{RESULTS_FILE} not found. Run run_code_review.py first.")
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
    print(f"Loaded {len(records)} records")

    by_condition: dict[str, list[float]] = defaultdict(list)
    by_scenario:  dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    by_category:  dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for r in records:
        by_condition[r["condition"]].append(r["task_score"])
        by_scenario[r["scenario_id"]][r["condition"]].append(r["task_score"])
        by_category[r.get("category", "unknown")][r["condition"]].append(r["task_score"])

    print("\n" + "=" * 60)
    print("PHASE B: CODE REVIEW — TOPOLOGY REPLICATION")
    print("=" * 60)

    chain = by_condition.get("chain-2", [])
    flat  = by_condition.get("flat-2",  [])

    print(f"\n{'Condition':<12} {'N':>4} {'Mean':>7} {'Std':>6}")
    print("-" * 32)
    for cond, vals in [("chain-2", chain), ("flat-2", flat)]:
        print(f"  {cond:<10} {len(vals):>4} {mean(vals):>7.1f} {stdev(vals):>6.1f}")

    gap = mean(chain) - mean(flat)
    print(f"\n  Chain − Flat gap: {gap:+.1f} pts")

    if gap > 10:
        print("  VERDICT: Topology finding REPLICATES on code review tasks.")
        print("  Chain outperforms flat on real-world engineering judgment tasks.")
    elif gap > 3:
        print("  VERDICT: Directional replication — chain leads but gap is smaller than Phase 1.")
    elif gap > -3:
        print("  VERDICT: No clear topology effect on code review. Task type may be insensitive.")
    else:
        print("  VERDICT: Flat outperforms chain on code review. Topology effect may be task-specific.")

    print("\n── Per-Scenario Breakdown ──")
    print(f"  {'Scenario':<30} {'chain-2':>9} {'flat-2':>9} {'Δ':>7}")
    print("  " + "-" * 58)
    for s in sorted(by_scenario.keys()):
        c = mean(by_scenario[s].get("chain-2", []))
        f = mean(by_scenario[s].get("flat-2",  []))
        print(f"  {s:<30} {c:>9.1f} {f:>9.1f} {c-f:>+7.1f}")

    print("\n── Per-Category Breakdown ──")
    print(f"  {'Category':<16} {'chain-2':>9} {'flat-2':>9} {'Δ':>7}")
    print("  " + "-" * 44)
    for cat in sorted(by_category.keys()):
        c = mean(by_category[cat].get("chain-2", []))
        f = mean(by_category[cat].get("flat-2",  []))
        print(f"  {cat:<16} {c:>9.1f} {f:>9.1f} {c-f:>+7.1f}")

    print("\n── Cross-Phase Comparison ──")
    print(f"  Phase 1 (judgment scenarios):   chain-2 57.6  flat-2 10.7  Δ=+46.9")
    print(f"  Phase B (code review):          chain-2 {mean(chain):.1f}  flat-2 {mean(flat):.1f}  Δ={gap:+.1f}")
    print()
    if gap > 15:
        print("  Effect size similar — topology gap is general, not scenario-specific.")
    elif gap > 5:
        print("  Smaller effect on code review — topology gap may be larger for open-ended judgment.")
    else:
        print("  No replication — topology may not be the primary factor for structured review tasks.")

    print()


if __name__ == "__main__":
    main()
