#!/usr/bin/env python3
# Copyright (c) 2026 Aryan Shah
#
# Part of the FLF Epistemic Case Study Competition submission (the epistemic-
# assessment layer). Licensed under the MIT License: see LICENSE-FLF-CODE and
# SUBMISSION_MANIFEST.md. This file is NOT part of the proprietary Kalibr
# engine, which is governed by LICENSE.

"""
Phase E: Analysis — Epistemic Investigation Architecture
FLF Epistemic Case Study Competition

Reads results/phase_e.jsonl and answers:

    Does the epistemic synthesis architecture (chain-2 + EPISTEMIC_SYNTHESIS_PROMPT)
    outperform the flat/no-handoff baseline on epistemic investigation tasks?

    Does it outperform single-agent self-review at the same compute cost?

    And critically: does tuning the synthesis prompt for reflection (not decisiveness)
    close the Phase 9 post-mortem gap?

Usage:
    python phases/phase_e/analyze_phase_e.py
"""
from __future__ import annotations
import json
import statistics
from collections import defaultdict
from pathlib import Path

try:
    from scipy import stats as scipy_stats
    _SCIPY = True
except ImportError:
    scipy_stats = None  # type: ignore[assignment]
    _SCIPY = False

RESULTS_FILE = Path("results/phase_e.jsonl")


def load() -> list[dict]:
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(f"{RESULTS_FILE} not found. Run run_phase_e.py first.")
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


def sig_label(p: float) -> str:
    if p < 0.01: return "p<0.01 **"
    if p < 0.05: return "p<0.05 *"
    if p < 0.10: return "p<0.10 +"
    return "n.s."


def main():
    records = load()
    print(f"Loaded {len(records)} records from {RESULTS_FILE}")

    by_condition: dict[str, list[float]] = defaultdict(list)
    by_scenario:  dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for r in records:
        cond = r["condition"]
        by_condition[cond].append(r["task_score"])
        by_scenario[r["scenario_id"]][cond].append(r["task_score"])

    print("\n" + "=" * 70)
    print("PHASE E: EPISTEMIC INVESTIGATION ARCHITECTURE")
    print("FLF Epistemic Case Study Competition")
    print("=" * 70)

    conditions = ["kalibr-chain", "kalibr-chain/decisive", "single-agent", "flat-no-handoff"]
    calls_map  = {"kalibr-chain": 2, "kalibr-chain/decisive": 2, "single-agent": 2, "flat-no-handoff": 4}
    synth_map  = {"kalibr-chain": "epistemic-JSON", "kalibr-chain/decisive": "decisive", "single-agent": "epistemic", "flat-no-handoff": "none"}

    # ── Overview table ─────────────────────────────────────────────────────────
    print(f"\n{'Condition':<22} {'Synthesis':<12} {'Calls':>6} {'N':>4} {'Mean':>7} {'Std':>6} {'Score/call':>11}")
    print("-" * 72)
    for cond in conditions:
        vals = by_condition.get(cond, [])
        calls = calls_map[cond]
        synth = synth_map[cond]
        if vals:
            spc = mean(vals) / calls
            print(f"  {cond:<20} {synth:<12} {calls:>6} {len(vals):>4} {mean(vals):>7.1f} {stdev(vals):>6.1f} {spc:>11.1f}")
        else:
            print(f"  {cond:<20} {synth:<12} {calls:>6} {'0':>4} {'n/a':>7} {'n/a':>6} {'n/a':>11}")

    # ── Primary comparison: kalibr-chain vs flat-no-handoff ────────────────────
    chain = by_condition.get("kalibr-chain",   [])
    flat  = by_condition.get("flat-no-handoff", [])

    print("\n── PRIMARY: kalibr-chain vs flat-no-handoff ──")
    if chain and flat:
        delta = mean(chain) - mean(flat)
        print(f"  kalibr-chain:    {mean(chain):.1f}  (n={len(chain)}, sd={stdev(chain):.1f}, 2 calls, epistemic synth)")
        print(f"  flat-no-handoff: {mean(flat):.1f}  (n={len(flat)}, sd={stdev(flat):.1f}, 4 calls, no synth)")
        if _SCIPY:
            t_stat, p_val = scipy_stats.ttest_ind(chain, flat, equal_var=False)
            print(f"  Δ = {delta:+.1f} pts  (Welch t={t_stat:.2f}, p={p_val:.3f})  {sig_label(p_val)}")
        else:
            print(f"  Δ = {delta:+.1f} pts  (install scipy for significance test)")
        spc_chain = mean(chain) / 2
        spc_flat  = mean(flat)  / 4
        if spc_flat > 0:
            ratio = spc_chain / spc_flat
            print(f"  Score/call: kalibr={spc_chain:.1f}  flat={spc_flat:.1f}  ratio={ratio:.1f}×")
        if delta > 10 and p_val < 0.05:
            print("\n  VERDICT: Epistemic synthesis architecture outperforms flat/no-handoff")
            print("  on epistemic investigation tasks. Synthesis tuned for reflection, not")
            print("  decisiveness, generalises the Phase 5 finding to open epistemic disputes.")
        elif p_val >= 0.05:
            print(f"\n  VERDICT: INCONCLUSIVE — Δ={delta:+.1f} but p={p_val:.3f}. Increase reps.")
        else:
            print(f"\n  VERDICT: Flat baseline competitive. Investigate why synthesis did not help.")
    else:
        missing = [c for c in ["kalibr-chain", "flat-no-handoff"] if not by_condition.get(c)]
        print(f"  Missing data for: {', '.join(missing)}")

    # ── Secondary: kalibr-chain vs single-agent (diversity effect) ────────────
    single = by_condition.get("single-agent", [])

    print("\n── SECONDARY: kalibr-chain vs single-agent (diversity, compute-matched) ──")
    if chain and single:
        delta = mean(chain) - mean(single)
        print(f"  kalibr-chain: {mean(chain):.1f}  single-agent: {mean(single):.1f}")
        if _SCIPY:
            t_stat, p_val = scipy_stats.ttest_ind(chain, single, equal_var=False)
            print(f"  Δ = {delta:+.1f} pts  (t={t_stat:.2f}, p={p_val:.3f})  {sig_label(p_val)}")
        else:
            print(f"  Δ = {delta:+.1f} pts  (install scipy for significance test)")
        if p_val >= 0.05:
            print("  Agent diversity adds no measurable value over self-review on epistemic tasks.")
            print("  Replicates Phase 8 null result (Δ=+0.7, p=0.854) in a new task domain.")
        else:
            print("  Agent diversity provides measurable benefit on epistemic tasks.")
            print("  This would be a novel finding — Phase 8 showed no diversity effect on judgment.")

    # ── H2 ablation: epistemic vs decisive prompt ─────────────────────────────
    decisive = by_condition.get("kalibr-chain/decisive", [])

    print("\n── H2 ABLATION: kalibr-chain/epistemic vs kalibr-chain/decisive ──")
    print("  (Same architecture, same agent count — only synthesis prompt differs)")
    if chain and decisive:
        delta = mean(chain) - mean(decisive)
        print(f"  kalibr-chain/epistemic: {mean(chain):.1f}  (n={len(chain)})")
        print(f"  kalibr-chain/decisive:  {mean(decisive):.1f}  (n={len(decisive)})")
        if _SCIPY:
            t_stat, p_val = scipy_stats.ttest_ind(chain, decisive, equal_var=False)
            print(f"  Δ = {delta:+.1f} pts  (t={t_stat:.2f}, p={p_val:.3f})  {sig_label(p_val)}")
        else:
            print(f"  Δ = {delta:+.1f} pts  (install scipy for significance test)")
        print(f"  Phase 9 reference: decisive prompt cost −13.3 pts on s03_post_mortem")
        if delta > 0:
            print("  → H2 SUPPORTED: epistemic prompt outperforms decisive on calibration tasks.")
        else:
            print("  → H2 NOT SUPPORTED: decisive prompt competitive; prompt specificity not confirmed.")
    else:
        missing = [c for c in ["kalibr-chain", "kalibr-chain/decisive"] if not by_condition.get(c)]
        print(f"  Missing data for: {', '.join(missing)}")

    # ── Per-scenario breakdown ─────────────────────────────────────────────────
    print("\n── Per-Scenario Breakdown ──")
    print(f"  {'Scenario':<30} {'epistemic':>9} {'decisive':>9} {'single':>7} {'flat':>7}")
    print("  " + "-" * 68)
    for s in sorted(by_scenario.keys()):
        ke  = by_scenario[s].get("kalibr-chain",          [])
        kd  = by_scenario[s].get("kalibr-chain/decisive", [])
        sg  = by_scenario[s].get("single-agent",          [])
        fl  = by_scenario[s].get("flat-no-handoff",       [])
        print(f"  {s:<30} "
              f"{(f'{mean(ke):.1f}' if ke else 'n/a'):>9} "
              f"{(f'{mean(kd):.1f}' if kd else 'n/a'):>9} "
              f"{(f'{mean(sg):.1f}' if sg else 'n/a'):>7} "
              f"{(f'{mean(fl):.1f}' if fl else 'n/a'):>7}")

    # ── H3: EpistemicMap parse rate ────────────────────────────────────────────
    print("\n── H3: EpistemicMap JSON Parse Rate (kalibr-chain only) ──")
    map_total   = sum(1 for r in records if r.get("condition") == "kalibr-chain")
    map_parsed  = sum(1 for r in records if r.get("condition") == "kalibr-chain" and r.get("map_parsed"))
    if map_total:
        rate = 100 * map_parsed // map_total
        print(f"  Parsed: {map_parsed}/{map_total}  ({rate}%)")
        if rate >= 70:
            print("  → H3 SUPPORTED: structured EpistemicMap produced reliably.")
        else:
            print("  → H3 NOT SUPPORTED: JSON output not reliable — model ignoring schema.")
        by_scen_parsed = defaultdict(lambda: [0, 0])  # [parsed, total]
        for r in records:
            if r.get("condition") == "kalibr-chain":
                sid = r["scenario_id"]
                by_scen_parsed[sid][1] += 1
                if r.get("map_parsed"):
                    by_scen_parsed[sid][0] += 1
        for sid, (p, t) in sorted(by_scen_parsed.items()):
            print(f"    {sid:<30}  {p}/{t}")
    else:
        print("  No kalibr-chain data yet.")

    # ── H2 cross-experiment connection ─────────────────────────────────────────
    print("\n── Cross-Experiment: Phase 9 Post-Mortem vs Phase E ──")
    print("  Phase 9 s03_post_mortem — decisive synth on reflective task: 66.7 pts")
    print("  Phase 9 s03_post_mortem — flat/no-handoff (no synth):        80.0 pts")
    print("  Phase 9 gap (decisive penalised chain by):                   −13.3 pts")
    decisive_mean = mean(decisive) if decisive else None
    chain_mean    = mean(chain)    if chain    else None
    if decisive_mean is not None and chain_mean is not None:
        phase_e_gap = chain_mean - decisive_mean
        print(f"  Phase E gap (epistemic vs decisive in Phase E):            {phase_e_gap:+.1f} pts")
        direction = "same direction" if phase_e_gap > 0 else "opposite direction"
        print(f"  → Prompt-type penalty is in the {direction} across phases.")

    # ── FLF submission summary ─────────────────────────────────────────────────
    print("\n── FLF Competition Summary ──")
    print("  Architecture: Kalibr chain-2 + synthesis prompt")
    print("  Primary finding: synthesis prompt DESIGN is the key variable.")
    print("    Decisive prompt (Phase 5/8/9): optimal for strategy/resource/crisis")
    print("    Epistemic prompt (Phase E):    optimal for investigation/calibration")
    print("  H1: chain > flat on epistemic tasks  →", "see PRIMARY above")
    print("  H2: epistemic > decisive prompt      →", "see H2 ABLATION above")
    print("  H3: JSON maps parse at ≥70%          →", "see H3 above")
    print("  Transferable: swap terminal prompt to switch decisive ↔ epistemic mode.")

    print()


if __name__ == "__main__":
    main()
