#!/usr/bin/env python3
# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Phase 6: Objective Benchmark Analysis.

Reads results/humaneval.jsonl and results/gsm8k.jsonl.
Reports pass@1 (HumanEval) and accuracy (GSM8K) per condition.
No LLM judge involved — all scoring is deterministic.

Usage:
    python phases/phase6/analyze_phase6.py
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

HUMANEVAL_FILE = Path("results/humaneval.jsonl")
GSM8K_FILE     = Path("results/gsm8k.jsonl")

CONDITION_ORDER = [
    "single-agent",
    "kalibr-flat-no-handoff",
    "kalibr-flat-handoff",
    "kalibr-chain",
]


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    with path.open() as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except Exception:
                pass
    return records


def rate(vals: list[bool]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def ci_wilson(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score confidence interval for a proportion."""
    if n == 0:
        return 0.0, 0.0
    p = successes / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    margin = (z * (p * (1 - p) / n + z**2 / (4 * n**2)) ** 0.5) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)


def print_table(title: str, by_cond: dict[str, list[bool]], metric: str) -> None:
    print(f"\n── {title} ──")
    print(f"  {'Condition':<26} {'N':>5} {metric:>8}  {'95% CI':>14}")
    print("  " + "-" * 58)
    for cond in CONDITION_ORDER:
        vals = by_cond.get(cond, [])
        if not vals:
            continue
        n = len(vals)
        s = sum(vals)
        r = rate(vals)
        lo, hi = ci_wilson(s, n)
        print(f"  {cond:<26} {n:>5} {r:>7.1%}  [{lo:.1%}, {hi:.1%}]")


def effect_summary(by_cond: dict[str, list[bool]]) -> None:
    chain   = by_cond.get("kalibr-chain", [])
    flat_h  = by_cond.get("kalibr-flat-handoff", [])
    flat_n  = by_cond.get("kalibr-flat-no-handoff", [])
    single  = by_cond.get("single-agent", [])

    print("\n── Key Effects ──")
    if chain and single:
        delta = rate(chain) - rate(single)
        print(f"  kalibr-chain vs single-agent:          {delta:+.1%}  "
              f"({'chain wins' if delta > 0.03 else 'no clear gain' if abs(delta) <= 0.03 else 'single wins'})")
    if chain and flat_n:
        delta = rate(chain) - rate(flat_n)
        print(f"  kalibr-chain vs flat/no-handoff:       {delta:+.1%}  "
              f"({'topology effect' if delta > 0.05 else 'weak' if delta > 0.01 else 'none'})")
    if chain and flat_h:
        delta = rate(chain) - rate(flat_h)
        print(f"  kalibr-chain vs flat/handoff:          {delta:+.1%}  "
              f"({'chain wins' if delta > 0.03 else 'tie' if abs(delta) <= 0.03 else 'flat wins'})")
    if flat_h and flat_n:
        delta = rate(flat_h) - rate(flat_n)
        print(f"  flat/handoff vs flat/no-handoff:       {delta:+.1%}  "
              f"({'handoff rescues flat' if delta > 0.05 else 'marginal'})")

    if chain:
        print(f"\n  VERDICT: ", end="")
        chain_rate  = rate(chain)
        single_rate = rate(single) if single else 0.0
        flat_rate   = rate(flat_h) if flat_h else rate(flat_n) if flat_n else 0.0
        if chain_rate > flat_rate + 0.05 and chain_rate > single_rate + 0.05:
            print("Kalibr chain topology is the clear winner. Strong evidence for chain architecture.")
        elif chain_rate > flat_rate + 0.02:
            print("Chain leads flat. Directional support for chain topology.")
        elif abs(chain_rate - flat_rate) <= 0.02:
            print("Chain and best flat are tied. Topology effect is weak at this benchmark.")
        else:
            print("Flat outperforms chain. Topology claim does not hold here.")


def main():
    he_records  = load_jsonl(HUMANEVAL_FILE)
    gsm_records = load_jsonl(GSM8K_FILE)

    print("=" * 60)
    print("PHASE 6: OBJECTIVE BENCHMARKS — KALIBR CHAIN vs FLAT")
    print("=" * 60)

    # ── HumanEval ──────────────────────────────────────────────────────────────
    if he_records:
        he_by_cond: dict[str, list[bool]] = defaultdict(list)
        for r in he_records:
            he_by_cond[r["condition"]].append(bool(r["passed"]))

        print(f"\nLoaded {len(he_records)} HumanEval records")
        print_table("HumanEval — pass@1 (Python code generation)", he_by_cond, "pass@1")
        effect_summary(he_by_cond)

        # Per-problem pass rates
        he_by_task: dict[str, dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))
        for r in he_records:
            he_by_task[r["task_id"]][r["condition"]].append(bool(r["passed"]))

        n_problems = len(he_by_task)
        chain_only = sum(
            1 for t in he_by_task.values()
            if rate(t.get("kalibr-chain", [])) > rate(t.get("kalibr-flat-no-handoff", []))
        )
        print(f"\n  Chain leads flat/no-handoff on {chain_only}/{n_problems} individual problems")
    else:
        print("\n  No HumanEval results yet. Run run_humaneval.py first.")

    # ── GSM8K ──────────────────────────────────────────────────────────────────
    if gsm_records:
        gsm_by_cond: dict[str, list[bool]] = defaultdict(list)
        for r in gsm_records:
            gsm_by_cond[r["condition"]].append(bool(r["correct"]))

        print(f"\n{'='*60}")
        print(f"Loaded {len(gsm_records)} GSM8K records")
        print_table("GSM8K — accuracy (math word problems)", gsm_by_cond, "accuracy")
        effect_summary(gsm_by_cond)
    else:
        print("\n  No GSM8K results yet. Run run_gsm8k.py first.")

    # ── Cross-benchmark summary ────────────────────────────────────────────────
    if he_records and gsm_records:
        print(f"\n{'='*60}")
        print("CROSS-BENCHMARK SUMMARY")
        print("=" * 60)

        he_chain  = rate(he_by_cond.get("kalibr-chain", []))
        he_flat   = rate(he_by_cond.get("kalibr-flat-no-handoff", []))
        gsm_chain = rate(gsm_by_cond.get("kalibr-chain", []))
        gsm_flat  = rate(gsm_by_cond.get("kalibr-flat-no-handoff", []))

        print(f"\n  {'Benchmark':<14} {'chain':>8} {'flat':>8} {'Δ':>8}")
        print("  " + "-" * 42)
        print(f"  {'HumanEval':<14} {he_chain:>7.1%} {he_flat:>7.1%} {he_chain-he_flat:>+7.1%}")
        print(f"  {'GSM8K':<14} {gsm_chain:>7.1%} {gsm_flat:>7.1%} {gsm_chain-gsm_flat:>+7.1%}")

        both_positive = (he_chain > he_flat) and (gsm_chain > gsm_flat)
        print(f"\n  Chain outperforms flat on both benchmarks: {both_positive}")
        if both_positive:
            print("  FINDING: Chain topology advantage is cross-domain (code + math).")
            print("  This is objective, judge-free evidence for the Kalibr chain architecture.")

    print()


if __name__ == "__main__":
    main()
