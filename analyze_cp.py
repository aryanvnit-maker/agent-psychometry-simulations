#!/usr/bin/env python3
# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
KalibrBench-CP analysis.

Reads results/cp_baseline.jsonl and results/cp_experiment.jsonl.
Produces console summary and PNG charts saved to reports/.

Usage:
    python analyze_cp.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency, fisher_exact

BASELINE_FILE   = Path("results/cp_baseline.jsonl")
EXPERIMENT_FILE = Path("results/cp_experiment.jsonl")
REPORTS_DIR     = Path("reports")

# Canonical display order and labels
CONDITION_ORDER = ["chain-1/generic", "chain-2/generic", "chain-2/specialized"]
CONDITION_COLORS = {
    "chain-1/generic":    "#94a3b8",
    "chain-2/generic":    "#60a5fa",
    "chain-2/specialized":"#f97316",
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    return rows


def load_all() -> pd.DataFrame:
    baseline   = _load_jsonl(BASELINE_FILE)
    experiment = _load_jsonl(EXPERIMENT_FILE)

    # Baseline file uses topology="chain" and no condition field — normalise
    for r in baseline:
        if "condition" not in r:
            r["condition"] = "generic"
        if r.get("topology") == "chain":
            r["topology"] = "chain-1"

    rows = baseline + experiment
    if not rows:
        print("No results found. Run run_cp_baseline.py and/or run_cp_experiment.py first.")
        sys.exit(0)

    df = pd.DataFrame(rows)
    df["key"] = df["topology"] + "/" + df["condition"]
    return df


# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------

def print_summary(df: pd.DataFrame) -> None:
    print("\n" + "=" * 68)
    print("KalibrBench-CP Results")
    print("=" * 68)
    print(f"{'Condition':<24} {'Pass@1':>8} {'AvgRate':>9} {'TokEff':>9} {'CE':>5} {'NoCode':>7} {'N':>5}")
    print("-" * 68)

    for key in CONDITION_ORDER:
        sub = df[df["key"] == key]
        if sub.empty:
            continue
        n       = len(sub)
        passed  = sub["passed"].sum()
        ce      = sub["compilation_error"].sum()
        nocode  = sub["extraction_failed"].sum()
        avg_pr  = sub["pass_rate"].mean()
        tok_eff = _token_efficiency(sub)
        print(f"{key:<24} {passed:>5}/{n:<3} {100*avg_pr:>8.1f}% {tok_eff:>9.4f} {ce:>5} {nocode:>7}")

    print("=" * 68)


def _token_efficiency(sub: pd.DataFrame) -> float:
    """Pass@1 per 1000 tokens averaged across problems."""
    valid = sub[sub["tokens_total"] > 0]
    if valid.empty:
        return 0.0
    return (valid["passed"].astype(float) / (valid["tokens_total"] / 1000)).mean()


# ---------------------------------------------------------------------------
# Lift analysis
# ---------------------------------------------------------------------------

def print_lift(df: pd.DataFrame) -> None:
    """For problems where chain-1 fails, how often does chain-2 succeed?"""
    c1 = df[df["key"] == "chain-1/generic"][["problem_id", "passed"]].set_index("problem_id")
    c2g = df[df["key"] == "chain-2/generic"][["problem_id", "passed"]].set_index("problem_id")
    c2s = df[df["key"] == "chain-2/specialized"][["problem_id", "passed"]].set_index("problem_id")

    shared_g = c1.index.intersection(c2g.index)
    shared_s = c1.index.intersection(c2s.index)

    print("\n── Multi-agent Lift (problems where chain-1 failed) ──")

    for label, c2, shared in [("chain-2/generic", c2g, shared_g), ("chain-2/specialized", c2s, shared_s)]:
        if shared.empty:
            continue
        failed_by_c1 = c1.loc[shared][~c1.loc[shared]["passed"]]
        if failed_by_c1.empty:
            print(f"  {label}: no chain-1 failures to lift on {len(shared)} shared problems")
            continue
        rescue = c2.loc[failed_by_c1.index]["passed"].sum()
        total  = len(failed_by_c1)
        print(f"  {label}: rescued {rescue}/{total} chain-1 failures ({100*rescue/total:.1f}%)")

    if not shared_g.empty and not c2s.empty and not c2g.empty:
        shared_both = c1.index.intersection(c2g.index).intersection(c2s.index)
        if not shared_both.empty:
            gen_pass  = c2g.loc[shared_both]["passed"].sum()
            spec_pass = c2s.loc[shared_both]["passed"].sum()
            print(f"\n  On {len(shared_both)} problems with all three conditions:")
            print(f"    chain-2/generic    pass@1: {gen_pass}/{len(shared_both)}")
            print(f"    chain-2/specialized pass@1: {spec_pass}/{len(shared_both)}")
            delta = spec_pass - gen_pass
            print(f"    Specialization lift: {delta:+d} problems ({100*delta/len(shared_both):+.1f}%)")


# ---------------------------------------------------------------------------
# Statistical tests
# ---------------------------------------------------------------------------

def print_stats(df: pd.DataFrame) -> None:
    print("\n── Statistical Tests ──")

    keys_present = [k for k in CONDITION_ORDER if not df[df["key"] == k].empty]
    if len(keys_present) < 2:
        print("  Need ≥2 conditions for comparison.")
        return

    # Pairwise Fisher's exact test on pass/fail counts
    for i in range(len(keys_present)):
        for j in range(i + 1, len(keys_present)):
            a_key, b_key = keys_present[i], keys_present[j]
            a = df[df["key"] == a_key]
            b = df[df["key"] == b_key]
            a_pass, a_fail = a["passed"].sum(), (~a["passed"]).sum()
            b_pass, b_fail = b["passed"].sum(), (~b["passed"]).sum()
            table = [[a_pass, a_fail], [b_pass, b_fail]]
            try:
                _, p = fisher_exact(table)
                sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
                print(f"  {a_key} vs {b_key}: p={p:.3f} {sig}")
            except Exception:
                print(f"  {a_key} vs {b_key}: insufficient data")

    # Compilation error rate comparison
    print("\n── Compilation Error Rates ──")
    for key in keys_present:
        sub = df[df["key"] == key]
        ce_rate = sub["compilation_error"].mean() * 100
        print(f"  {key:<24} {ce_rate:.1f}%")

    # Token cost comparison
    print("\n── Mean Tokens per Problem ──")
    for key in keys_present:
        sub = df[df["key"] == key]
        valid = sub[sub["tokens_total"] > 0]
        if not valid.empty:
            print(f"  {key:<24} {valid['tokens_total'].mean():.0f} (median {valid['tokens_total'].median():.0f})")


# ---------------------------------------------------------------------------
# Difficulty breakdown
# ---------------------------------------------------------------------------

def print_difficulty(df: pd.DataFrame) -> None:
    print("\n── Pass Rate by Difficulty Band ──")
    bins   = [1999, 2099, 2199, 2299, 2399, 2501]
    labels = ["2000-2099", "2100-2199", "2200-2299", "2300-2399", "2400-2500"]
    df = df.copy()
    df["band"] = pd.cut(df["difficulty"], bins=bins, labels=labels)

    keys_present = [k for k in CONDITION_ORDER if not df[df["key"] == k].empty]
    header = f"  {'Band':<12}" + "".join(f"{k:>20}" for k in keys_present)
    print(header)
    for band in labels:
        row = f"  {band:<12}"
        for key in keys_present:
            sub = df[(df["key"] == key) & (df["band"] == band)]
            if sub.empty:
                row += f"{'—':>20}"
            else:
                pct = 100 * sub["passed"].mean()
                row += f"{pct:>18.1f}%"
        print(row)


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def _bar_pass_at_1(df: pd.DataFrame) -> None:
    keys_present = [k for k in CONDITION_ORDER if not df[df["key"] == k].empty]
    values = []
    errors = []
    for key in keys_present:
        sub = df[df["key"] == key]
        p = sub["passed"].mean()
        n = len(sub)
        se = np.sqrt(p * (1 - p) / n) if n > 0 else 0
        values.append(p * 100)
        errors.append(se * 100)

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [CONDITION_COLORS.get(k, "#888") for k in keys_present]
    x = range(len(keys_present))
    bars = ax.bar(x, values, yerr=errors, capsize=5, color=colors, width=0.55, zorder=3)
    ax.set_xticks(list(x))
    ax.set_xticklabels(keys_present, fontsize=11)
    ax.set_ylabel("Pass@1 (%)", fontsize=12)
    ax.set_title("Pass@1 by Condition — KalibrBench-CP", fontsize=13, fontweight="bold")
    ax.set_ylim(0, max(values) * 1.35 + 5)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=10)
    fig.tight_layout()
    REPORTS_DIR.mkdir(exist_ok=True)
    fig.savefig(REPORTS_DIR / "cp_pass_at_1.png", dpi=150)
    plt.close(fig)


def _bar_token_efficiency(df: pd.DataFrame) -> None:
    keys_present = [k for k in CONDITION_ORDER if not df[df["key"] == k].empty]
    values = [_token_efficiency(df[df["key"] == k]) for k in keys_present]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [CONDITION_COLORS.get(k, "#888") for k in keys_present]
    x = range(len(keys_present))
    bars = ax.bar(x, values, color=colors, width=0.55, zorder=3)
    ax.set_xticks(list(x))
    ax.set_xticklabels(keys_present, fontsize=11)
    ax.set_ylabel("Pass@1 per 1k tokens", fontsize=12)
    ax.set_title("Token Efficiency by Condition — KalibrBench-CP", fontsize=13, fontweight="bold")
    ax.set_ylim(0, max(values) * 1.35 + 0.001)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.0005,
                f"{val:.4f}", ha="center", va="bottom", fontsize=10)
    fig.tight_layout()
    fig.savefig(REPORTS_DIR / "cp_token_efficiency.png", dpi=150)
    plt.close(fig)


def _scatter_difficulty(df: pd.DataFrame) -> None:
    keys_present = [k for k in CONDITION_ORDER if not df[df["key"] == k].empty]
    bins   = [1999, 2099, 2199, 2299, 2399, 2501]
    labels = [2050, 2150, 2250, 2350, 2450]
    df = df.copy()
    df["band_mid"] = pd.cut(df["difficulty"], bins=bins, labels=labels).astype(float)

    fig, ax = plt.subplots(figsize=(9, 5))
    for key in keys_present:
        sub = df[df["key"] == key]
        grouped = sub.groupby("band_mid")["passed"].mean() * 100
        if grouped.empty:
            continue
        ax.plot(grouped.index, grouped.values, marker="o", label=key,
                color=CONDITION_COLORS.get(key, "#888"), linewidth=2, markersize=7)

    ax.set_xlabel("Difficulty (Codeforces rating)", fontsize=12)
    ax.set_ylabel("Pass Rate (%)", fontsize=12)
    ax.set_title("Pass Rate vs Difficulty — KalibrBench-CP", fontsize=13, fontweight="bold")
    ax.set_xticks(labels)
    ax.set_xticklabels(["2000-2099", "2100-2199", "2200-2299", "2300-2399", "2400-2500"],
                       fontsize=9, rotation=20)
    ax.set_ylim(-5, 105)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(REPORTS_DIR / "cp_difficulty_curve.png", dpi=150)
    plt.close(fig)


def _stacked_outcome(df: pd.DataFrame) -> None:
    keys_present = [k for k in CONDITION_ORDER if not df[df["key"] == k].empty]

    passed_vals = []
    fail_vals   = []
    ce_vals     = []
    nocode_vals = []

    for key in keys_present:
        sub = df[df["key"] == key]
        n = len(sub)
        passed_vals.append(sub["passed"].sum() / n * 100)
        ce_vals.append(sub["compilation_error"].sum() / n * 100)
        nocode_vals.append(sub["extraction_failed"].sum() / n * 100)
        # "clean fail" = ran and executed but wrong answer
        clean_fail = (~sub["passed"] & ~sub["compilation_error"] & ~sub["extraction_failed"]).sum()
        fail_vals.append(clean_fail / n * 100)

    x = np.arange(len(keys_present))
    width = 0.5

    fig, ax = plt.subplots(figsize=(9, 5))
    b1 = ax.bar(x, passed_vals,  width, label="Pass",              color="#22c55e", zorder=3)
    b2 = ax.bar(x, fail_vals,    width, bottom=passed_vals,        label="Wrong Answer",      color="#f59e0b", zorder=3)
    b3 = ax.bar(x, ce_vals,      width,
                bottom=[a+b for a,b in zip(passed_vals, fail_vals)],
                label="Compilation Error", color="#ef4444", zorder=3)
    b4 = ax.bar(x, nocode_vals,  width,
                bottom=[a+b+c for a,b,c in zip(passed_vals, fail_vals, ce_vals)],
                label="No Code Extracted", color="#d1d5db", zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(keys_present, fontsize=11)
    ax.set_ylabel("% of problems", fontsize=12)
    ax.set_ylim(0, 110)
    ax.set_title("Outcome Breakdown by Condition — KalibrBench-CP", fontsize=13, fontweight="bold")
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=10, loc="upper right")
    fig.tight_layout()
    fig.savefig(REPORTS_DIR / "cp_outcomes.png", dpi=150)
    plt.close(fig)


def generate_plots(df: pd.DataFrame) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    _bar_pass_at_1(df)
    _bar_token_efficiency(df)
    _scatter_difficulty(df)
    _stacked_outcome(df)
    print(f"\nCharts saved to {REPORTS_DIR}/")
    print("  cp_pass_at_1.png")
    print("  cp_token_efficiency.png")
    print("  cp_difficulty_curve.png")
    print("  cp_outcomes.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    df = load_all()
    print(f"Loaded {len(df)} result rows across {df['problem_id'].nunique()} problems.")

    print_summary(df)
    print_lift(df)
    print_stats(df)
    print_difficulty(df)
    generate_plots(df)
