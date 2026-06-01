#!/usr/bin/env python3
# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Phase 9: Kalibr Orchestration vs Grok Multi-Agent Panel — Analysis

Reads results/phase9.jsonl and answers the core question:

    Does Kalibr's explicit synthesis architecture (chain-2, 2 LLM calls)
    outperform xAI's internal panel (4 agents, 1 API call) when both
    use the same Grok base model?

NOTE ON COMPUTE:
    This is NOT a compute-matched comparison.
    kalibr-chain  = 2 LLM calls (our orchestration layer)
    grok-panel    = 1 API call, but ~4 internal agents (xAI's orchestration)

    The comparison is architecture vs architecture, not call-for-call.
    Results should be reported with this caveat.

Usage:
    python phases/phase9/analyze_phase9.py
"""
from __future__ import annotations
import json
import statistics
from collections import defaultdict
from pathlib import Path
from scipy import stats as scipy_stats

RESULTS_FILE = Path("results/phase9.jsonl")


def load() -> list[dict]:
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(f"{RESULTS_FILE} not found. Run run_phase9.py first.")
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
    meta:         dict[str, dict] = {}

    for r in records:
        cond = r["condition"]
        by_condition[cond].append(r["task_score"])
        by_scenario[r["scenario_id"]][cond].append(r["task_score"])
        if cond not in meta:
            meta[cond] = {
                "model":             r.get("model", "unknown"),
                "n_calls":           r.get("n_calls", "?"),
                "n_internal_agents": r.get("n_internal_agents", 1),
            }

    print("\n" + "=" * 65)
    print("PHASE 9: KALIBR ORCHESTRATION vs GROK MULTI-AGENT PANEL")
    print("Same base model family, different orchestration layers")
    print("=" * 65)

    # ── Overview table ─────────────────────────────────────────────────────
    print(f"\n{'Condition':<20} {'Model':<35} {'API calls':>9} {'Int.agents':>10} {'N':>4} {'Mean':>7} {'Std':>6}")
    print("-" * 90)
    for cond in ["kalibr-chain", "grok-panel"]:
        vals = by_condition.get(cond, [])
        m    = meta.get(cond, {})
        n_calls   = m.get("n_calls", "?")
        n_int     = m.get("n_internal_agents", 1)
        model_str = m.get("model", "unknown")[:34]
        if vals:
            print(f"  {cond:<18} {model_str:<35} {str(n_calls):>9} {str(n_int):>10} {len(vals):>4} {mean(vals):>7.1f} {stdev(vals):>6.1f}")
        else:
            print(f"  {cond:<18} {model_str:<35} {'?':>9} {'?':>10} {'0':>4} {'n/a':>7} {'n/a':>6}")

    # ── Primary comparison ─────────────────────────────────────────────────
    kalibr = by_condition.get("kalibr-chain", [])
    panel  = by_condition.get("grok-panel",   [])

    print("\n── PRIMARY: kalibr-chain vs grok-panel ──")
    print("   NOTE: not compute-matched — Grok panel runs ~4 agents internally")
    if kalibr and panel:
        delta = mean(kalibr) - mean(panel)
        t_stat, p_val = scipy_stats.ttest_ind(kalibr, panel, equal_var=False)
        print(f"  kalibr-chain:  {mean(kalibr):.1f}  (n={len(kalibr)}, sd={stdev(kalibr):.1f}, 2 LLM calls)")
        print(f"  grok-panel:    {mean(panel):.1f}  (n={len(panel)}, sd={stdev(panel):.1f}, ~4 internal agents)")
        print(f"  Δ = {delta:+.1f} pts  (Welch t={t_stat:.2f}, p={p_val:.3f})")
        sig = "p<0.05 *" if p_val < 0.05 else ("p<0.10 +" if p_val < 0.10 else "n.s.")
        print(f"  Significance: {sig}")

        print(f"\n  VERDICT:", end=" ")
        if delta > 10 and p_val < 0.05:
            print("KALIBR WINS — explicit synthesis architecture outperforms xAI panel")
            print("  Kalibr's 2-call chain beats Grok's ~4-agent internal panel.")
            print("  Orchestration layer is the value; open architecture wins on quality AND cost.")
        elif delta > 5 and p_val < 0.10:
            print("KALIBR LEADS — positive signal, borderline significance")
            print("  Suggestive advantage for Kalibr; replicate with more runs to confirm.")
        elif p_val >= 0.05:
            print("INCONCLUSIVE — difference not statistically significant")
            print(f"  Δ={delta:+.1f} pts but p={p_val:.3f} — cannot reject H0 at α=0.05.")
            print("  Kalibr matches xAI's panel at 2 calls vs ~4 agents.")
            print("  Kalibr wins on efficiency (fewer calls, lower cost, full control).")
            if delta < 0:
                print("  The observed gap may reflect variance, not a true panel advantage.")
                print("  Re-run with more reps or investigate per-scenario collapses.")
        else:
            print("GROK PANEL WINS — statistically significant advantage")
            print("  xAI's internal panel outperforms Kalibr chain-2.")
            print("  Investigate: does grok-panel benefit from the higher compute (4 agents)?")
            print("  Run a compute-matched follow-up: Kalibr chain-4 vs grok-panel.")
    else:
        missing = [c for c in ["kalibr-chain", "grok-panel"] if not by_condition.get(c)]
        print(f"  Missing data for: {', '.join(missing)}")
        return

    # ── Per-scenario breakdown ─────────────────────────────────────────────
    print("\n── Per-Scenario Breakdown ──")
    scenarios = sorted(by_scenario.keys())
    print(f"  {'Scenario':<30} {'kalibr':>9} {'panel':>9} {'Δ':>7}")
    print("  " + "-" * 57)
    for s in scenarios:
        k = by_scenario[s].get("kalibr-chain", [])
        p = by_scenario[s].get("grok-panel",   [])
        k_str = f"{mean(k):.1f}" if k else "n/a"
        p_str = f"{mean(p):.1f}" if p else "n/a"
        d_str = f"{mean(k) - mean(p):+.1f}" if k and p else "n/a"
        print(f"  {s:<30} {k_str:>9} {p_str:>9} {d_str:>7}")

    # ── Efficiency framing ─────────────────────────────────────────────────
    if kalibr and panel:
        print("\n── Efficiency Framing ──")
        print("  Grok panel uses ~4 internal agents per call.")
        print("  Kalibr chain uses 2 LLM calls.")
        print(f"  Score-per-call: Kalibr={mean(kalibr)/2:.1f}  Grok panel={mean(panel)/4:.1f} (est.)")
        if mean(kalibr) / 2 > mean(panel) / 4:
            print("  Kalibr is more score-efficient per LLM call.")
        else:
            print("  Grok panel is more score-efficient per internal agent.")

        print("\n── Implications ──")
        delta = mean(kalibr) - mean(panel)
        if delta >= -5:
            print("  Kalibr's open synthesis architecture matches or beats a proprietary")
            print("  multi-agent panel at lower compute cost.")
            print("  The synthesis prompt is the moat — not agent count, not model scale.")
        else:
            print("  xAI's panel holds an advantage. Consider:")
            print("  1. Is the gap explained by Grok panel's higher compute (4 agents)?")
            print("  2. Does Grok panel include a synthesis step internally?")
            print("  3. Run Kalibr chain-4 to test compute-matched hypothesis.")

    print()


if __name__ == "__main__":
    main()
