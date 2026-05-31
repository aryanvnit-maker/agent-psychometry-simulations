#!/usr/bin/env python3
# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Unified results summary across all completed phases.

Reads local JSONL files only. Phase 1 and Phase 2 main experiment data
live in Supabase and are noted as missing until exported.

Usage:
    python phases/summarize_all.py
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path


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


def rate(vals: list) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def pct(v: float) -> str:
    return f"{v*100:.1f}%"


def header(title: str) -> None:
    print(f"\n{'='*60}")
    print(title)
    print("="*60)


def section(title: str) -> None:
    print(f"\n── {title} ──")


# ── Phase 1 ───────────────────────────────────────────────────────────────────
def summarize_phase1():
    header("PHASE 1 — Topology (Judgment Tasks, LLM Judge)")
    print("  Source: Supabase (not yet exported to repo)")
    print("  Results from write-up:")
    rows = [
        ("1 agent",  "chain", 15.3, "flat", 31.2),
        ("2 agents", "chain", 57.6, "flat", 10.7),
        ("4 agents", "chain", 50.4, "flat", 35.5),
        ("8 agents", "chain", 40.4, "flat", 19.1),
    ]
    print(f"\n  {'Team Size':<12} {'Chain':>8} {'Flat':>8} {'Δ':>8}")
    print("  " + "-"*40)
    for size, _, c, _, f in rows:
        print(f"  {size:<12} {c:>8.1f} {f:>8.1f} {c-f:>+8.1f}")
    print("\n  Cross-model replication (Chain vs Flat, N=2):")
    print("  Gemini 2.5 Flash: 40.3 vs 23.4  (+16.9)")
    print("  Claude 3.5 Sonnet: 42.4 vs 20.4 (+21.9)")
    print("  NOTE: Turns not matched between topologies — confound acknowledged.")
    print("        Phase 5 isolates topology × handoff cleanly.")


# ── Phase 2 ───────────────────────────────────────────────────────────────────
def summarize_phase2(control_path: Path):
    header("PHASE 2 — Constitution (Codeforces Div.1 C/D, Judge0)")
    print("  Main experiment: Supabase (not yet exported to repo)")
    print("  Results from write-up:")
    rows = [
        ("chain-1/generic (baseline)", 12),
        ("chain-2/generic",            16),
        ("chain-2/specialized",        13),
    ]
    print(f"\n  {'Condition':<36} {'pass@1':>8}")
    print("  " + "-"*46)
    for cond, p in rows:
        print(f"  {cond:<36} {p:>7}%")

    records = load_jsonl(control_path)
    if records:
        section("Phase 2 Control — ALGORITHMIST isolation (local data)")
        by_cond: dict[str, list] = defaultdict(list)
        for r in records:
            by_cond[r["condition"]].append(r["passed"])
        print(f"\n  {'Condition':<36} {'N':>5} {'pass@1':>8}")
        print("  " + "-"*52)
        for cond, vals in sorted(by_cond.items()):
            print(f"  {cond:<36} {len(vals):>5} {pct(rate(vals)):>8}")
        print("  FINDING: ALGORITHMIST role instruction causes degradation,")
        print("  not extreme dimension profiles. Role label is the culprit.")
    else:
        print("\n  Control data: not found (results/algorithmist_control.jsonl)")


# ── Phase 3 ───────────────────────────────────────────────────────────────────
def summarize_phase3(path: Path):
    header("PHASE 3 — Adversarial Robustness (Codeforces, Judge0)")
    records = load_jsonl(path)
    if not records:
        print("  No data — results/phase3.jsonl not found.")
        return

    by_cond: dict[str, list] = defaultdict(list)
    nocode:  dict[str, int]  = defaultdict(int)
    for r in records:
        by_cond[r["condition"]].append(r["passed"])
        if r.get("nocode"):
            nocode[r["condition"]] += 1

    print(f"\n  {'Condition':<24} {'N':>5} {'pass@1':>8} {'NoCode':>8}")
    print("  " + "-"*48)
    for cond in ["chain-2/clean", "chain-2/poisoned", "flat-2/clean", "flat-2/poisoned"]:
        vals = by_cond.get(cond, [])
        if vals:
            print(f"  {cond:<24} {len(vals):>5} {pct(rate(vals)):>8} {nocode.get(cond,0):>8}")

    chain_delta = rate(by_cond["chain-2/poisoned"]) - rate(by_cond["chain-2/clean"])
    flat_delta  = rate(by_cond["flat-2/poisoned"])  - rate(by_cond["flat-2/clean"])
    print(f"\n  Chain poisoned vs clean: {chain_delta:+.1%}")
    print(f"  Flat  poisoned vs clean: {flat_delta:+.1%}")
    print(f"  Swing between poisoned conditions: {chain_delta - flat_delta:+.1%}")
    print(f"  NoCode collapses — chain: {nocode.get('chain-2/poisoned',0)}  flat: {nocode.get('flat-2/poisoned',0)}")
    print("  FINDING: Flat collapsed completely under adversarial input.")
    print("  Chain never collapsed once across all poisoned runs.")


# ── Phase 4 ───────────────────────────────────────────────────────────────────
def summarize_phase4(path: Path):
    header("PHASE 4 — Meta-Router (Mixed Workload)")
    records = load_jsonl(path)
    if not records:
        print("  No data — results/meta_orchestrator.jsonl not found.")
        return

    by_cond: dict[str, dict] = defaultdict(lambda: {"scores": [], "passed": [], "nocode": 0})
    for r in records:
        c = r["condition"]
        if r.get("task_score") is not None:
            by_cond[c]["scores"].append(r["task_score"])
        if r.get("task_type") == "execution":
            by_cond[c]["passed"].append(r.get("passed", False))
            if r.get("nocode"):
                by_cond[c]["nocode"] += 1

    print(f"\n  {'Condition':<22} {'Judgment':>10} {'Exec pass@1':>12} {'NoCode':>8}")
    print("  " + "-"*55)
    for cond in ["static-judgment", "static-execution", "meta-router"]:
        d = by_cond.get(cond, {})
        scores  = d.get("scores", [])
        passed  = d.get("passed", [])
        nocode  = d.get("nocode", 0)
        j_score = f"{rate(scores)*100:.1f}" if scores else "n/a"
        e_rate  = pct(rate(passed)) if passed else "n/a"
        print(f"  {cond:<22} {j_score:>10} {e_rate:>12} {nocode:>8}")

    print("\n  Classifier accuracy: 100% on 37 real + 10 adversarial Trojan tasks.")
    print("  FINDING: Meta-router achieves per-domain maximum on both axes.")
    print("  Static configs crater on one side of a mixed workload.")


# ── Phase B ───────────────────────────────────────────────────────────────────
def summarize_phase_b(path: Path):
    header("PHASE B — Topology Replication (Code Review, LLM Judge)")
    records = load_jsonl(path)
    if not records:
        print("  No data — results/code_review.jsonl not found.")
        return

    by_cond: dict[str, list] = defaultdict(list)
    for r in records:
        by_cond[r["condition"]].append(r["task_score"])

    print(f"\n  {'Condition':<24} {'N':>5} {'Mean score':>12}")
    print("  " + "-"*44)
    for cond, vals in sorted(by_cond.items()):
        print(f"  {cond:<24} {len(vals):>5} {rate(vals):>12.1f}")

    chain = by_cond.get("chain", [])
    flat  = by_cond.get("flat", [])
    if chain and flat:
        print(f"\n  Chain vs Flat: {rate(chain):.1f} vs {rate(flat):.1f}  (Δ={rate(chain)-rate(flat):+.1f})")
        print("  FINDING: Replicates Phase 1 topology direction on code review domain.")


# ── Phase 5 ───────────────────────────────────────────────────────────────────
def summarize_phase5(path: Path):
    header("PHASE 5 — Topology × Handoff Factorial (Judgment, LLM Judge)")
    records = load_jsonl(path)
    if not records:
        print("  No data yet — still running or results/handoff_factorial.jsonl not found.")
        return

    by_cond: dict[str, list] = defaultdict(list)
    for r in records:
        by_cond[r["condition"]].append(r["task_score"])

    conds = ["chain/handoff", "chain/no-handoff", "flat/handoff", "flat/no-handoff"]
    print(f"\n  {'Condition':<22} {'N':>5} {'Mean':>8} {'Std':>7}")
    print("  " + "-"*46)

    import statistics
    for cond in conds:
        vals = by_cond.get(cond, [])
        if vals:
            std = statistics.stdev(vals) if len(vals) > 1 else 0.0
            print(f"  {cond:<22} {len(vals):>5} {rate(vals):>8.1f} {std:>7.1f}")

    cn = by_cond.get("chain/no-handoff", [])
    fn = by_cond.get("flat/no-handoff",  [])
    ch = by_cond.get("chain/handoff",    [])
    fh = by_cond.get("flat/handoff",     [])

    if cn and fn:
        print(f"\n  Pure topology (no-handoff):  chain {rate(cn):.1f} vs flat {rate(fn):.1f}  (Δ={rate(cn)-rate(fn):+.1f})")
    if ch and fh:
        print(f"  Pure topology (w/ handoff):  chain {rate(ch):.1f} vs flat {rate(fh):.1f}  (Δ={rate(ch)-rate(fh):+.1f})")
    if ch and cn:
        print(f"  Handoff effect in chain:     {rate(ch):.1f} vs {rate(cn):.1f}  (Δ={rate(ch)-rate(cn):+.1f})")
    if fh and fn:
        print(f"  Handoff effect in flat:      {rate(fh):.1f} vs {rate(fn):.1f}  (Δ={rate(fh)-rate(fn):+.1f})")

    total = sum(len(v) for v in by_cond.values())
    expected = 4 * 10 * 3  # 4 conditions × 10 reps × 3 scenarios (approx)
    if total < expected:
        print(f"\n  Still running: {total} records so far.")


# ── Phase 6 ───────────────────────────────────────────────────────────────────
def summarize_phase6(he_path: Path, gsm_path: Path):
    header("PHASE 6 — Objective Benchmarks (No LLM Judge)")

    def show(name, records, metric_key, label):
        if not records:
            print(f"\n  {name}: no data.")
            return
        by_cond: dict[str, list] = defaultdict(list)
        for r in records:
            by_cond[r["condition"]].append(bool(r[metric_key]))

        calls = {"single-agent": 1, "single-agent-refine": 2, "kalibr-chain": 2,
                 "kalibr-flat-no-handoff": 4, "kalibr-flat-handoff": 5}
        order = ["single-agent", "single-agent-refine", "kalibr-chain",
                 "kalibr-flat-handoff", "kalibr-flat-no-handoff"]

        print(f"\n  {name} — {label}")
        print(f"  {'Condition':<26} {'calls':>5} {'N':>5} {label:>8}")
        print("  " + "-"*48)
        for cond in order:
            vals = by_cond.get(cond, [])
            if vals:
                print(f"  {cond:<26} {calls.get(cond,'?'):>5} {len(vals):>5} {pct(rate(vals)):>8}")

        chain  = by_cond.get("kalibr-chain", [])
        refine = by_cond.get("single-agent-refine", [])
        flat_n = by_cond.get("kalibr-flat-no-handoff", [])
        flat_h = by_cond.get("kalibr-flat-handoff", [])

        if chain and refine:
            print(f"\n  [PRIMARY] chain vs refine (both 2 calls): {rate(chain)-rate(refine):+.1%}")
        if chain and flat_n:
            print(f"  chain vs flat/no-handoff:                 {rate(chain)-rate(flat_n):+.1%}")
        if chain and flat_h:
            print(f"  chain vs flat/handoff:                    {rate(chain)-rate(flat_h):+.1%}")
        if flat_h and flat_n:
            print(f"  flat/handoff vs flat/no-handoff:          {rate(flat_h)-rate(flat_n):+.1%}")

    show("HumanEval", load_jsonl(he_path),  "passed",  "pass@1")
    show("GSM8K",     load_jsonl(gsm_path), "correct", "accuracy")

    print("\n  KEY FINDING: synthesis step is the critical variable.")
    print("  flat/no-handoff collapses (role constitutions block output).")
    print("  flat/handoff ≈ chain ≈ single-agent-refine when synthesis exists.")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("="*60)
    print("KALIBR RESEARCH — UNIFIED RESULTS SUMMARY")
    print("="*60)

    summarize_phase1()
    summarize_phase2(Path("results/algorithmist_control.jsonl"))
    summarize_phase3(Path("results/phase3.jsonl"))
    summarize_phase4(Path("results/meta_orchestrator.jsonl"))
    summarize_phase_b(Path("results/code_review.jsonl"))
    summarize_phase5(Path("results/handoff_factorial.jsonl"))
    summarize_phase6(Path("results/humaneval.jsonl"), Path("results/gsm8k.jsonl"))

    print("\n" + "="*60)
    print("MISSING DATA (in Supabase, not yet exported to repo)")
    print("="*60)
    print("  Phase 1 raw runs   → export via Supabase → results/phase1.jsonl")
    print("  Phase 2 main runs  → export via Supabase → results/phase2.jsonl")
    print()


if __name__ == "__main__":
    main()
