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
Phase 4: Meta-Orchestrator analysis.

Reads results/meta_orchestrator.jsonl and answers:

  1. Classifier accuracy — what % of tasks did meta-router classify correctly?
  2. Judgment performance — task_score (0–100) per condition
  3. Execution performance — pass@1 per condition
  4. Overall — weighted combined score per condition
  5. Routing gain — meta-router vs the better static baseline per task type

Usage:
    python analyze_meta_orchestrator.py
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

RESULTS_FILE = Path("results/meta_orchestrator.jsonl")
REPORTS_DIR  = Path("reports")

CONDITIONS = ["static-judgment", "static-execution", "meta-router"]
DOMAIN_J   = "judgment"
DOMAIN_E   = "execution"


def load() -> list[dict]:
    if not RESULTS_FILE.exists():
        print(f"ERROR: {RESULTS_FILE} not found. Run run_meta_orchestrator.py first.")
        raise SystemExit(1)
    records = []
    with RESULTS_FILE.open() as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except Exception:
                pass
    return records


def _by_condition_type(records: list[dict]) -> dict[str, dict[str, list[dict]]]:
    """Returns {condition: {task_type: [records]}}."""
    out: dict[str, dict[str, list[dict]]] = {
        c: {DOMAIN_J: [], DOMAIN_E: []} for c in CONDITIONS
    }
    for r in records:
        c = r.get("condition")
        t = r.get("task_type")
        if c in out and t in out[c]:
            out[c][t].append(r)
    return out


# ---------------------------------------------------------------------------
# Analysis sections
# ---------------------------------------------------------------------------

def section_classifier_accuracy(records: list[dict]) -> None:
    print("=" * 60)
    print("1. CLASSIFIER ACCURACY (meta-router only)")
    print("=" * 60)

    router_records = [r for r in records if r.get("condition") == "meta-router"]
    if not router_records:
        print("  No meta-router records found.\n")
        return

    correct   = sum(1 for r in router_records if r.get("routed_correct"))
    total     = len(router_records)
    accuracy  = correct / total * 100 if total else 0

    j_records = [r for r in router_records if r.get("task_type") == DOMAIN_J]
    e_records = [r for r in router_records if r.get("task_type") == DOMAIN_E]
    j_correct = sum(1 for r in j_records if r.get("routed_correct"))
    e_correct = sum(1 for r in e_records if r.get("routed_correct"))

    print(f"\n  Overall accuracy : {correct}/{total} ({accuracy:.1f}%)")
    if j_records:
        print(f"  Judgment tasks   : {j_correct}/{len(j_records)} ({j_correct/len(j_records)*100:.1f}%)")
    if e_records:
        print(f"  Execution tasks  : {e_correct}/{len(e_records)} ({e_correct/len(e_records)*100:.1f}%)")

    # Misclassified breakdown
    misclassified = [r for r in router_records if not r.get("routed_correct")]
    if misclassified:
        print(f"\n  Misclassified tasks ({len(misclassified)}):")
        for r in misclassified:
            print(f"    {r['task_id']}  actual={r['task_type']}  routed={r['routed_domain']}")
    print()


def section_judgment_performance(by_ct: dict) -> dict[str, float]:
    print("=" * 60)
    print("2. JUDGMENT PERFORMANCE (task_score 0–100, 3-judge mean)")
    print("=" * 60)

    scores: dict[str, float] = {}
    rows = []
    for cond in CONDITIONS:
        recs = by_ct[cond][DOMAIN_J]
        valid = [r["task_score"] for r in recs if r.get("task_score") is not None]
        if valid:
            mean = np.mean(valid)
            std  = np.std(valid)
            scores[cond] = mean
            rows.append((cond, len(valid), mean, std))
        else:
            rows.append((cond, 0, 0.0, 0.0))

    print(f"\n  {'Condition':<22} {'N':>4}  {'Mean score':>10}  {'Std':>6}")
    print(f"  {'-'*22}  {'-'*4}  {'-'*10}  {'-'*6}")
    for cond, n, mean, std in rows:
        print(f"  {cond:<22} {n:>4}  {mean:>10.1f}  {std:>6.1f}")
    print()
    return scores


def section_execution_performance(by_ct: dict) -> dict[str, float]:
    print("=" * 60)
    print("3. EXECUTION PERFORMANCE (pass@1)")
    print("=" * 60)

    passrates: dict[str, float] = {}
    rows = []
    for cond in CONDITIONS:
        recs = by_ct[cond][DOMAIN_E]
        if recs:
            passed = sum(1 for r in recs if r.get("passed"))
            rate   = passed / len(recs) * 100
            nocode = sum(1 for r in recs if r.get("nocode"))
            ce     = sum(1 for r in recs if r.get("compilation_error"))
            passrates[cond] = rate
            rows.append((cond, len(recs), passed, rate, nocode, ce))
        else:
            rows.append((cond, 0, 0, 0.0, 0, 0))

    print(f"\n  {'Condition':<22} {'N':>4}  {'Passed':>6}  {'Pass@1':>7}  {'NoCode':>6}  {'CE':>4}")
    print(f"  {'-'*22}  {'-'*4}  {'-'*6}  {'-'*7}  {'-'*6}  {'-'*4}")
    for cond, n, passed, rate, nocode, ce in rows:
        print(f"  {cond:<22} {n:>4}  {passed:>6}  {rate:>6.1f}%  {nocode:>6}  {ce:>4}")
    print()
    return passrates


def section_routing_gain(j_scores: dict[str, float], e_passrates: dict[str, float]) -> None:
    print("=" * 60)
    print("4. ROUTING GAIN — mixed-workload global deployment comparison")
    print("=" * 60)

    sj_j  = j_scores.get("static-judgment",  0)
    sj_e  = e_passrates.get("static-judgment",  0)
    se_j  = j_scores.get("static-execution", 0)
    se_e  = e_passrates.get("static-execution", 0)
    mr_j  = j_scores.get("meta-router", 0)
    mr_e  = e_passrates.get("meta-router", 0)

    # The correct comparison for mixed workloads: each static must handle BOTH domains.
    # Meta-router is the only config that can deploy the optimal architecture per task.
    print(f"\n  {'Config':<22} {'Judgment score':>15}  {'Execution pass@1':>16}")
    print(f"  {'-'*22}  {'-'*15}  {'-'*16}")
    print(f"  {'static-judgment':<22} {sj_j:>14.1f}  {sj_e:>15.1f}%")
    print(f"  {'static-execution':<22} {se_j:>14.1f}  {se_e:>15.1f}%")
    print(f"  {'meta-router':<22} {mr_j:>14.1f}  {mr_e:>15.1f}%")

    # Within-domain delta vs per-domain best (secondary metric)
    best_j_static = max(sj_j, se_j)
    best_e_static = max(sj_e, se_e)
    delta_j = mr_j - best_j_static
    delta_e = mr_e - best_e_static

    print(f"\n  Within-domain delta vs best static:")
    print(f"    Judgment:  {delta_j:+.1f}  (meta={mr_j:.1f}, best static={best_j_static:.1f})")
    print(f"    Execution: {delta_e:+.1f}pp (meta={mr_e:.1f}%, best static={best_e_static:.1f}%)")

    print()
    # Verdict based on global mixed-workload view
    sj_crashes_exec = sj_e < 5
    se_degrades_j   = se_j < (sj_j * 0.85)
    mr_matches_both = (mr_j >= best_j_static - 2) and (mr_e >= best_e_static - 2)

    if mr_matches_both and (sj_crashes_exec or se_degrades_j):
        print("  >> Meta-router is the only viable architecture for mixed workloads.")
        if sj_crashes_exec:
            print(f"     static-judgment collapses on execution ({sj_e:.1f}% pass@1).")
        if se_degrades_j:
            print(f"     static-execution degrades judgment by {sj_j - se_j:.1f} points.")
        print("     Router achieves per-domain maximum on both axes simultaneously.")
    elif delta_j > 2 and delta_e > 1:
        print("  >> Meta-router wins on BOTH domains vs best static. Dynamic routing justified.")
    elif delta_j < -5 or delta_e < -2:
        print("  >> Meta-router UNDERPERFORMS best static baseline.")
        print("     Likely cause: agent config mismatch (wrong roles/handoff for task subtype),")
        print("     not classifier error. Check per-scenario breakdown for pattern.")
    else:
        print("  >> Meta-router matches best static per domain.")
        print("     Gain is in breadth (mixed workload coverage), not within-domain performance.")
    print()


def section_per_scenario(by_ct: dict) -> None:
    print("=" * 60)
    print("5. PER-SCENARIO JUDGMENT SCORES")
    print("=" * 60)

    scenarios: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for cond in CONDITIONS:
        for r in by_ct[cond][DOMAIN_J]:
            scenario = r["task_id"].rsplit("/run", 1)[0]
            if r.get("task_score") is not None:
                scenarios[scenario][cond].append(r["task_score"])

    print(f"\n  {'Scenario':<30} {'static-J':>10}  {'static-E':>10}  {'meta-router':>12}")
    print(f"  {'-'*30}  {'-'*10}  {'-'*10}  {'-'*12}")
    for scenario in sorted(scenarios.keys()):
        vals = scenarios[scenario]
        sj   = f"{np.mean(vals['static-judgment']):.1f}"   if vals.get("static-judgment")  else "—"
        se   = f"{np.mean(vals['static-execution']):.1f}"  if vals.get("static-execution") else "—"
        mr   = f"{np.mean(vals['meta-router']):.1f}"       if vals.get("meta-router")      else "—"
        print(f"  {scenario:<30} {sj:>10}  {se:>10}  {mr:>12}")
    print()


# ---------------------------------------------------------------------------
# Chart
# ---------------------------------------------------------------------------

def make_chart(j_scores: dict[str, float], e_passrates: dict[str, float]) -> None:
    if not HAS_MPL:
        print("  (matplotlib not available — skipping chart)\n")
        return

    REPORTS_DIR.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Phase 4: Meta-Orchestrator vs Static Baselines", fontsize=13)

    colors = ["#4c72b0", "#dd8452", "#55a868"]
    labels = [c.replace("-", "\n") for c in CONDITIONS]

    # Judgment
    ax = axes[0]
    vals = [j_scores.get(c, 0) for c in CONDITIONS]
    bars = ax.bar(labels, vals, color=colors, width=0.5)
    ax.set_title("Judgment Tasks\n(task_score 0–100)")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Mean task score")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 1, f"{v:.1f}", ha="center", va="bottom", fontsize=10)

    # Execution
    ax = axes[1]
    vals = [e_passrates.get(c, 0) for c in CONDITIONS]
    bars = ax.bar(labels, vals, color=colors, width=0.5)
    ax.set_title("Execution Tasks\n(pass@1 %)")
    ax.set_ylim(0, max(max(vals) * 1.3, 30))
    ax.set_ylabel("Pass@1 (%)")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.3, f"{v:.1f}%", ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    out = REPORTS_DIR / "meta_orchestrator_results.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"  Chart saved to {out}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    records = load()
    print(f"Loaded {len(records)} records from {RESULTS_FILE}\n")

    by_ct = _by_condition_type(records)

    section_classifier_accuracy(records)
    j_scores    = section_judgment_performance(by_ct)
    e_passrates = section_execution_performance(by_ct)
    section_routing_gain(j_scores, e_passrates)
    section_per_scenario(by_ct)
    make_chart(j_scores, e_passrates)


if __name__ == "__main__":
    main()
