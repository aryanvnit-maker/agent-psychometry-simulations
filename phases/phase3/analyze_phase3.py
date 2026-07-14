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
Phase 3: Hallucination Multiplier — analysis.

Reads results/phase3.jsonl and produces:
  1. Pass@1 table per condition
  2. Δ table (poisoned − clean per topology)
  3. Hint acceptance rate (% of poisoned runs where hinted algorithm was used)
  4. Hallucination lock-in rate (hint accepted AND code failed)
  5. Per-approach breakdown (which wrong approaches caused most damage)
  6. Charts saved to reports/

Usage:
    python analyze_phase3.py
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

PHASE3_FILE  = Path("results/phase3.jsonl")
REPORTS_DIR  = Path("reports")

CONDITION_ORDER = [
    "chain-2/clean",
    "chain-2/poisoned",
    "flat-2/clean",
    "flat-2/poisoned",
]

CONDITION_LABELS = {
    "chain-2/clean":    "Chain-2\n(clean)",
    "chain-2/poisoned": "Chain-2\n(poisoned)",
    "flat-2/clean":     "Flat-2\n(clean)",
    "flat-2/poisoned":  "Flat-2\n(poisoned)",
}

CONDITION_COLORS = {
    "chain-2/clean":    "#60a5fa",
    "chain-2/poisoned": "#1d4ed8",
    "flat-2/clean":     "#f97316",
    "flat-2/poisoned":  "#7c2d12",
}


def load_results(path: Path = PHASE3_FILE) -> dict[str, list[dict]]:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found — run run_phase3.py first")
    by_condition: dict[str, list[dict]] = defaultdict(list)
    with path.open() as f:
        for line in f:
            try:
                rec = json.loads(line)
                by_condition[rec["condition"]].append(rec)
            except Exception:
                pass
    return dict(by_condition)


def pass_at_1(records: list[dict]) -> float:
    if not records:
        return 0.0
    return sum(1 for r in records if r.get("passed")) / len(records)


def hint_acceptance_rate(records: list[dict]) -> float:
    poisoned = [r for r in records if r.get("hint_injected")]
    if not poisoned:
        return float("nan")
    return sum(1 for r in poisoned if r.get("hint_accepted")) / len(poisoned)


def lock_in_rate(records: list[dict]) -> float:
    """% of poisoned runs where hint was accepted AND code failed."""
    poisoned = [r for r in records if r.get("hint_injected")]
    if not poisoned:
        return float("nan")
    locked = sum(1 for r in poisoned if r.get("hint_accepted") and not r.get("passed"))
    return locked / len(poisoned)


def print_table(title: str, rows: list[tuple]) -> None:
    print(f"\n{title}")
    print("-" * 70)
    for row in rows:
        print("  " + "  |  ".join(str(c) for c in row))
    print("-" * 70)


def main():
    parser = argparse.ArgumentParser(description="Phase 3: Hallucination Multiplier — analysis")
    parser.add_argument("--file", type=Path, default=PHASE3_FILE,
                        help="Results JSONL to analyze (default: results/phase3.jsonl)")
    parser.add_argument("--suffix", type=str, default="",
                        help="Suffix for chart filenames, e.g. '_claude', to avoid overwriting")
    args = parser.parse_args()

    REPORTS_DIR.mkdir(exist_ok=True)
    data = load_results(args.file)

    present = [c for c in CONDITION_ORDER if c in data]
    if not present:
        print(f"No results found in {args.file}.")
        return

    # Report which model(s) produced this data, if the runner stamped it.
    models = sorted({r.get("model", "unstamped")
                     for recs in data.values() for r in recs})
    print(f"\nAnalyzing: {args.file}")
    print(f"Model(s) in file: {', '.join(models)}")

    # -----------------------------------------------------------------------
    # Table 1: Pass@1 per condition
    # -----------------------------------------------------------------------
    rows = [("Condition", "N", "Pass@1", "Avg Pass Rate", "CE", "NoCode")]
    for cond in present:
        records = data[cond]
        p1 = pass_at_1(records)
        avg_pass = np.mean([r.get("pass_rate", 0.0) for r in records])
        ce = sum(1 for r in records if r.get("compilation_error"))
        nc = sum(1 for r in records if r.get("nocode"))
        rows.append((cond, len(records), f"{p1:.1%}", f"{avg_pass:.1%}", ce, nc))

    print_table("Pass@1 by Condition", rows)

    # -----------------------------------------------------------------------
    # Table 2: Δ (poisoned − clean) per topology
    # -----------------------------------------------------------------------
    delta_rows = [("Topology", "Clean Pass@1", "Poisoned Pass@1", "Δ", "Verdict")]
    for topology in ("chain-2", "flat-2"):
        clean_key   = f"{topology}/clean"
        poisoned_key = f"{topology}/poisoned"
        if clean_key not in data or poisoned_key not in data:
            continue
        p_clean    = pass_at_1(data[clean_key])
        p_poisoned = pass_at_1(data[poisoned_key])
        delta      = p_poisoned - p_clean
        verdict    = "hint RESISTED" if delta > -0.02 else ("mild drag" if delta > -0.05 else "SIGNIFICANT DROP")
        delta_rows.append((
            topology,
            f"{p_clean:.1%}",
            f"{p_poisoned:.1%}",
            f"{delta:+.1%}",
            verdict,
        ))

    print_table("Topology Susceptibility to Hint Poisoning", delta_rows)

    # -----------------------------------------------------------------------
    # Table 3: Hint acceptance and lock-in
    # -----------------------------------------------------------------------
    hint_rows = [("Condition", "Hint Acceptance Rate", "Lock-in Rate")]
    for cond in present:
        records = data[cond]
        har = hint_acceptance_rate(records)
        lir = lock_in_rate(records)
        har_str = f"{har:.1%}" if not (isinstance(har, float) and np.isnan(har)) else "—"
        lir_str = f"{lir:.1%}" if not (isinstance(lir, float) and np.isnan(lir)) else "—"
        hint_rows.append((cond, har_str, lir_str))

    print_table("Hint Acceptance and Hallucination Lock-in", hint_rows)

    # -----------------------------------------------------------------------
    # Table 4: Per-approach breakdown (flat-2/poisoned only)
    # -----------------------------------------------------------------------
    if "flat-2/poisoned" in data:
        approach_stats: dict[str, dict] = defaultdict(lambda: {"n": 0, "accepted": 0, "passed": 0})
        for r in data["flat-2/poisoned"]:
            approach = r.get("hint_approach", "unknown")
            approach_stats[approach]["n"] += 1
            if r.get("hint_accepted"):
                approach_stats[approach]["accepted"] += 1
            if r.get("passed"):
                approach_stats[approach]["passed"] += 1

        approach_rows = [("Approach", "N", "Acceptance %", "Pass@1")]
        for approach, stats in sorted(approach_stats.items(), key=lambda x: -x[1]["accepted"]):
            n = stats["n"]
            acc_pct = stats["accepted"] / n if n else 0
            p1 = stats["passed"] / n if n else 0
            approach_rows.append((approach, n, f"{acc_pct:.1%}", f"{p1:.1%}"))

        print_table("Approach Breakdown — flat-2/poisoned", approach_rows)

    # -----------------------------------------------------------------------
    # Charts
    # -----------------------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Chart 1: Pass@1 by condition
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Left: Pass@1 bar chart
        conds = [c for c in CONDITION_ORDER if c in data]
        p1_vals = [pass_at_1(data[c]) * 100 for c in conds]
        colors  = [CONDITION_COLORS[c] for c in conds]
        labels  = [CONDITION_LABELS[c] for c in conds]

        axes[0].bar(labels, p1_vals, color=colors, edgecolor="white", linewidth=0.5)
        axes[0].set_ylabel("Pass@1 (%)")
        axes[0].set_title("Phase 3: Pass@1 by Condition")
        axes[0].set_ylim(0, max(p1_vals) * 1.3 + 2)
        for i, v in enumerate(p1_vals):
            axes[0].text(i, v + 0.3, f"{v:.1f}%", ha="center", va="bottom", fontsize=9)

        # Right: Δ bar chart (poisoned vs clean per topology)
        deltas = []
        delta_labels = []
        delta_colors = []
        for topology, color in [("chain-2", "#1d4ed8"), ("flat-2", "#7c2d12")]:
            ck, pk = f"{topology}/clean", f"{topology}/poisoned"
            if ck in data and pk in data:
                delta = (pass_at_1(data[pk]) - pass_at_1(data[ck])) * 100
                deltas.append(delta)
                delta_labels.append(topology)
                delta_colors.append(color)

        if deltas:
            bars = axes[1].bar(delta_labels, deltas, color=delta_colors, edgecolor="white")
            axes[1].axhline(0, color="black", linewidth=0.8)
            axes[1].set_ylabel("Δ Pass@1 (poisoned − clean, pp)")
            axes[1].set_title("Performance Drop from Hint Poisoning")
            for bar, v in zip(bars, deltas):
                axes[1].text(bar.get_x() + bar.get_width() / 2,
                             v + (0.3 if v >= 0 else -0.8),
                             f"{v:+.1f}pp", ha="center", va="bottom", fontsize=10, fontweight="bold")

        plt.tight_layout()
        chart_path = REPORTS_DIR / f"phase3_results{args.suffix}.png"
        plt.savefig(chart_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"\nChart saved: {chart_path}")

        # Chart 2: Hint acceptance vs lock-in (poisoned conditions only)
        poisoned_conds = [c for c in CONDITION_ORDER if "poisoned" in c and c in data]
        if poisoned_conds:
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            x = np.arange(len(poisoned_conds))
            width = 0.35
            har_vals = [hint_acceptance_rate(data[c]) * 100 for c in poisoned_conds]
            lir_vals = [lock_in_rate(data[c]) * 100 for c in poisoned_conds]
            p_labels = [CONDITION_LABELS[c] for c in poisoned_conds]

            ax2.bar(x - width / 2, har_vals, width, label="Hint acceptance rate", color="#f59e0b")
            ax2.bar(x + width / 2, lir_vals, width, label="Lock-in rate (accepted + failed)", color="#ef4444")
            ax2.set_xticks(x)
            ax2.set_xticklabels(p_labels)
            ax2.set_ylabel("%")
            ax2.set_title("Hallucination Lock-in: Poisoned Conditions")
            ax2.legend()
            ax2.set_ylim(0, 100)

            chart2_path = REPORTS_DIR / f"phase3_lockin{args.suffix}.png"
            plt.savefig(chart2_path, dpi=150, bbox_inches="tight")
            plt.close()
            print(f"Chart saved: {chart2_path}")

    except ImportError:
        print("matplotlib not available — skipping charts")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print("\n=== Summary ===")
    if "chain-2/clean" in data and "flat-2/clean" in data:
        chain_clean = pass_at_1(data["chain-2/clean"])
        flat_clean  = pass_at_1(data["flat-2/clean"])
        print(f"Topology baseline: chain-2 {chain_clean:.1%}  flat-2 {flat_clean:.1%}")

    if all(c in data for c in ["chain-2/clean", "chain-2/poisoned", "flat-2/clean", "flat-2/poisoned"]):
        Δchain = pass_at_1(data["chain-2/poisoned"]) - pass_at_1(data["chain-2/clean"])
        Δflat  = pass_at_1(data["flat-2/poisoned"])  - pass_at_1(data["flat-2/clean"])
        print(f"Δchain (poisoned − clean): {Δchain:+.1%}")
        print(f"Δflat  (poisoned − clean): {Δflat:+.1%}")

        if abs(Δflat) > abs(Δchain):
            print("\n✓ Hypothesis supported: flat topology is more susceptible to hint poisoning")
        else:
            print("\n✗ Hypothesis not supported: chain and flat show similar susceptibility")

        har_chain = hint_acceptance_rate(data["chain-2/poisoned"])
        har_flat  = hint_acceptance_rate(data["flat-2/poisoned"])
        if not np.isnan(har_chain) and not np.isnan(har_flat):
            print(f"\nHint acceptance: chain-2 {har_chain:.1%}  flat-2 {har_flat:.1%}")
            if har_flat > har_chain:
                print("✓ Flat swarms accept wrong hints more readily than chains")


if __name__ == "__main__":
    main()
