#!/usr/bin/env python3
"""
Pull results from Supabase and generate analysis charts.

Usage:
    python analyze.py

Output: PNG charts saved to /reports/
        Summary statistics printed to console
"""
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
from scipy.stats import pearsonr
from src.analysis.query import load_results
from src.analysis.plots import generate_all


def _r(df, col_a, col_b) -> str:
    x = df[col_a].dropna()
    y = df[col_b].dropna()
    idx = x.index.intersection(y.index)
    if len(idx) < 4:
        return "n/a"
    r, p = pearsonr(x[idx], y[idx])
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    return f"r={r:.2f}{sig} (p={p:.3f})"


def print_summary(df: pd.DataFrame, label: str = ""):
    tag = f" | topology: {label}" if label else ""
    print("\n" + "=" * 60)
    print(f"DATASET: {len(df)} runs | {df['scenario_id'].nunique()} scenarios{tag}")
    print("=" * 60)

    print("\n── Mean Task Score by Composition ──")
    print(df.groupby("composition_condition")["task_score"].agg(["mean", "std", "count"]).round(1).to_string())

    print("\n── Mean Task Score by Team Size ──")
    print(df.groupby("team_size")["task_score"].agg(["mean", "std", "count"]).round(1).to_string())

    print("\n── Mean Task Score by Scenario ──")
    print(df.groupby("scenario_id")["task_score"].agg(["mean", "std", "count"]).round(1).to_string())

    print("\n── Consensus Rate by Composition ──")
    print(df.groupby("composition_condition")["consensus_achieved"].mean().mul(100).round(1).to_string())

    print("\n── Mean Contradictions by Composition ──")
    print(df.groupby("composition_condition")["contradictions"].mean().round(2).to_string())

    # ── Bell (2007) ───────────────────────────────────────────────────────────
    print("\n── Bell (2007): Cognitive Diversity vs Performance ──")
    drafted = df[df["composition_condition"] == "drafted"]["task_score"].mean()
    homog   = df[df["composition_condition"] == "homogeneous"]["task_score"].mean()
    founder = df[df["composition_condition"] == "founder_brained"]["task_score"].mean()
    print(f"  Drafted (diversity-optimised): {drafted:.1f}")
    print(f"  Homogeneous:                   {homog:.1f}")
    print(f"  Founder-brained:               {founder:.1f}")
    print(f"  Diversity ↔ Task Score:        {_r(df, 'cognitive_diversity', 'task_score')}")
    if drafted > homog and drafted > founder:
        print("  VERDICT: Consistent with Bell (2007) — diversity helps performance.")
    elif homog > drafted or founder > drafted:
        print("  VERDICT: Diverges from Bell (2007) — homogeneity outperforms diversity.")
        print("  NOTE: May be topology artifact. Retest with flat topology before publishing.")

    # ── Barrick et al. (1998) ─────────────────────────────────────────────────
    print("\n── Barrick et al. (1998): Conscientiousness & Agreeableness ──")
    print(f"  Conscientiousness mean     ↔ Task Score: {_r(df, 'conscientiousness_mean', 'task_score')}")
    print(f"  Conscientiousness variance ↔ Task Score: {_r(df, 'conscientiousness_variance', 'task_score')}")
    print(f"  Agreeableness mean         ↔ Task Score: {_r(df, 'agreeableness_mean', 'task_score')}")
    print(f"  Agreeableness variance     ↔ Task Score: {_r(df, 'agreeableness_variance', 'task_score')}")
    c_mean_r = df["conscientiousness_mean"].corr(df["task_score"])
    c_var_r  = df["conscientiousness_variance"].corr(df["task_score"])
    if abs(c_var_r) > abs(c_mean_r):
        print("  VERDICT: Variance predicts more than mean — consistent with Barrick et al.")
    else:
        print("  VERDICT: Mean predicts more than variance — partial divergence from Barrick et al.")

    # ── Google Project Aristotle (2015) ───────────────────────────────────────
    print("\n── Google Project Aristotle (2015): Psychological Safety ──")
    print(f"  Psych Safety ↔ Task Score: {_r(df, 'psych_safety', 'task_score')}")
    print(f"  Diversity    ↔ Task Score: {_r(df, 'cognitive_diversity', 'task_score')}")
    ps_r = abs(df["psych_safety"].corr(df["task_score"]))
    di_r = abs(df["cognitive_diversity"].corr(df["task_score"]))
    by_comp = df.groupby("composition_condition")["psych_safety"].mean().round(1)
    print(f"  Psych Safety by composition:\n{by_comp.to_string()}")
    if ps_r > di_r:
        print("  VERDICT: Psychological safety predicts performance better than diversity — consistent with Aristotle.")
    else:
        print("  VERDICT: Diversity is stronger predictor than safety — diverges from Aristotle.")

    # ── GEQ (Carron et al. 1985) ──────────────────────────────────────────────
    print("\n── GEQ: Task Cohesion vs Social Cohesion ──")
    by_comp_geq = df.groupby("composition_condition")[["geq_task", "geq_social"]].mean().round(1)
    print(by_comp_geq.to_string())
    print(f"  GEQ Task   ↔ Task Score:  {_r(df, 'geq_task', 'task_score')}")
    print(f"  GEQ Social ↔ Task Score:  {_r(df, 'geq_social', 'task_score')}")
    gap = (df["geq_task"] - df["geq_social"]).abs().mean()
    print(f"  Mean task/social gap: {gap:.1f} pts — ", end="")
    print("cohesion dimensions diverge." if gap > 10 else "cohesion dimensions track closely.")

    # ── TCI (Anderson & West 1994) ────────────────────────────────────────────
    print("\n── TCI: Innovation Climate ──")
    print(f"  TCI Innovation ↔ Novel Approaches: {_r(df, 'tci_innovation', 'novel_approaches')}")
    print(f"  TCI Innovation ↔ Task Score:       {_r(df, 'tci_innovation', 'task_score')}")
    by_comp_tci = df.groupby("composition_condition")["tci_innovation"].mean().round(1)
    print(f"  TCI by composition:\n{by_comp_tci.to_string()}")

    # ── FIRO-B ────────────────────────────────────────────────────────────────
    print("\n── FIRO-B: Inclusion ──")
    print(f"  FIRO Inclusion ↔ Task Score:        {_r(df, 'firo_inclusion', 'task_score')}")
    print(f"  FIRO Inclusion ↔ Consensus:         {_r(df, 'firo_inclusion', 'consensus_achieved')}")
    by_comp_firo = df.groupby("composition_condition")["firo_inclusion"].mean().round(2)
    print(f"  Inclusion by composition:\n{by_comp_firo.to_string()}")

    print()


def print_topology_comparison(chain: pd.DataFrame, flat: pd.DataFrame):
    print("\n" + "=" * 60)
    print("TOPOLOGY COMPARISON: chain vs flat")
    print("=" * 60)

    print("\n── Bell (2007) Confound Check: Diversity vs Performance ──")
    for label, df in [("chain", chain), ("flat", flat)]:
        drafted = df[df["composition_condition"] == "drafted"]["task_score"].mean()
        homog   = df[df["composition_condition"] == "homogeneous"]["task_score"].mean()
        founder = df[df["composition_condition"] == "founder_brained"]["task_score"].mean()
        winner  = max([("drafted", drafted), ("homogeneous", homog), ("founder_brained", founder)],
                      key=lambda x: x[1])
        print(f"  [{label}] drafted={drafted:.1f}  homogeneous={homog:.1f}  founder_brained={founder:.1f}  → winner: {winner[0]}")
    print()

    print("── Mean Task Score by Composition (chain vs flat) ──")
    for comp in ["drafted", "homogeneous", "founder_brained"]:
        c = chain[chain["composition_condition"] == comp]["task_score"].mean()
        f = flat[flat["composition_condition"] == comp]["task_score"].mean()
        delta = f - c
        direction = "↑" if delta > 0 else "↓"
        print(f"  {comp:<20} chain={c:.1f}  flat={f:.1f}  Δ={delta:+.1f} {direction}")
    print()

    print("── Mean Task Score by Team Size (chain vs flat) ──")
    shared_sizes = sorted(set(chain["team_size"]) & set(flat["team_size"]))
    for size in shared_sizes:
        c = chain[chain["team_size"] == size]["task_score"].mean()
        f = flat[flat["team_size"] == size]["task_score"].mean()
        delta = f - c
        direction = "↑" if delta > 0 else "↓"
        print(f"  size={size:<4} chain={c:.1f}  flat={f:.1f}  Δ={delta:+.1f} {direction}")
    print()

    print("── Consensus Rate (chain vs flat) ──")
    for label, df in [("chain", chain), ("flat", flat)]:
        rate = df["consensus_achieved"].mean() * 100
        print(f"  [{label}] {rate:.1f}%")
    print()

    print("── Routing Cost Estimate ──")
    # Gap between flat (perfect info) and chain (sequential) = cost of routing structure
    flat_mean  = flat["task_score"].mean()
    chain_mean = chain["task_score"].mean()
    gap = flat_mean - chain_mean
    print(f"  Flat mean: {flat_mean:.1f}  Chain mean: {chain_mean:.1f}  Gap: {gap:+.1f}")
    if gap > 5:
        print("  Routing cost is significant — flat topology meaningfully outperforms chain.")
    elif gap < -5:
        print("  Chain outperforms flat — sequential structure adds value, possibly through forced convergence.")
    else:
        print("  Topology gap is small — routing structure has minimal performance cost.")


def print_cross_model_comparison(all_df: pd.DataFrame):
    families = sorted(all_df["model_family"].dropna().unique())
    if len(families) < 2:
        return

    print("\n" + "=" * 60)
    print("CROSS-MODEL TOPOLOGY COMPARISON")
    print("=" * 60)

    print("\n── Chain vs Flat gap by model family ──")
    print(f"  {'Model':<20} {'Chain':>8} {'Flat':>8} {'Gap':>8}  Verdict")
    print(f"  {'-'*20} {'-'*8} {'-'*8} {'-'*8}  {'-'*30}")
    for fam in families:
        fdf   = all_df[all_df["model_family"] == fam]
        chain = fdf[fdf["topology"] == "chain"]["task_score"].mean()
        flat  = fdf[fdf["topology"] == "flat"]["task_score"].mean()
        gap   = chain - flat
        verdict = "chain > flat ✓" if gap > 5 else "flat > chain ✗" if gap < -5 else "no gap"
        print(f"  {fam:<20} {chain:>8.1f} {flat:>8.1f} {gap:>+8.1f}  {verdict}")

    print("\n── Chain mean by model family and team size ──")
    pivot = all_df[all_df["topology"] == "chain"].pivot_table(
        values="task_score", index="team_size", columns="model_family", aggfunc="mean"
    ).round(1)
    print(pivot.to_string())

    print("\n── Is the Bell inversion consistent across models? ──")
    for fam in families:
        fdf     = all_df[(all_df["model_family"] == fam) & (all_df["topology"] == "chain")]
        drafted = fdf[fdf["composition_condition"] == "drafted"]["task_score"].mean()
        homog   = fdf[fdf["composition_condition"] == "homogeneous"]["task_score"].mean()
        founder = fdf[fdf["composition_condition"] == "founder_brained"]["task_score"].mean()
        winner  = max([("drafted", drafted), ("homogeneous", homog), ("founder_brained", founder)],
                      key=lambda x: x[1] if not (x[1] != x[1]) else -1)
        print(f"  [{fam}] drafted={drafted:.1f}  homogeneous={homog:.1f}  founder_brained={founder:.1f}  → {winner[0]}")

    holds = []
    for fam in families:
        fdf     = all_df[(all_df["model_family"] == fam) & (all_df["topology"] == "chain")]
        drafted = fdf[fdf["composition_condition"] == "drafted"]["task_score"].mean()
        homog   = fdf[fdf["composition_condition"] == "homogeneous"]["task_score"].mean()
        founder = fdf[fdf["composition_condition"] == "founder_brained"]["task_score"].mean()
        holds.append(drafted < homog or drafted < founder)
    if all(holds):
        print("\n  VERDICT: Bell inversion holds across all model families — structural finding.")
    else:
        print("\n  VERDICT: Bell inversion does NOT hold across all models — may be model-specific.")
    print()


if __name__ == "__main__":
    chain = load_results(topology="chain")
    flat  = load_results(topology="flat")

    print_summary(chain, label="chain")
    print_summary(flat,  label="flat")
    print_topology_comparison(chain, flat)

    all_df = load_results()
    print_cross_model_comparison(all_df)

    generate_all(chain)
