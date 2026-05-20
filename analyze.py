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
from src.analysis.query import load_results
from src.analysis.plots import generate_all


def print_summary(df: pd.DataFrame):
    print("\n" + "=" * 60)
    print(f"DATASET: {len(df)} runs across {df['scenario_id'].nunique()} scenarios")
    print("=" * 60)

    print("\n── Mean Task Score by Composition ──")
    print(df.groupby("composition_condition")["task_score"].agg(["mean", "std", "count"]).round(1).to_string())

    print("\n── Mean Task Score by Team Size ──")
    print(df.groupby("team_size")["task_score"].agg(["mean", "std", "count"]).round(1).to_string())

    print("\n── Mean Task Score by Scenario ──")
    print(df.groupby("scenario_id")["task_score"].agg(["mean", "std", "count"]).round(1).to_string())

    print("\n── Cognitive Diversity by Composition ──")
    print(df.groupby("composition_condition")["cognitive_diversity"].agg(["mean", "std"]).round(2).to_string())

    print("\n── Consensus Rate by Composition ──")
    consensus = df.groupby("composition_condition")["consensus_achieved"].mean().mul(100).round(1)
    print(consensus.to_string())

    print("\n── Mean Contradictions by Composition ──")
    print(df.groupby("composition_condition")["contradictions"].mean().round(2).to_string())

    print("\n── Bell (2007) Comparison ──")
    drafted = df[df["composition_condition"] == "drafted"]["task_score"].mean()
    homog   = df[df["composition_condition"] == "homogeneous"]["task_score"].mean()
    founder = df[df["composition_condition"] == "founder_brained"]["task_score"].mean()
    print(f"  Drafted (diversity-optimised): {drafted:.1f}")
    print(f"  Homogeneous:                   {homog:.1f}")
    print(f"  Founder-brained:               {founder:.1f}")
    if drafted > homog and drafted > founder:
        print("  → Diversity-optimised teams outperform. Consistent with Bell (2007).")
    elif homog > drafted:
        print("  → Homogeneous teams outperform. Diverges from Bell (2007) — notable finding.")
    print()


if __name__ == "__main__":
    df = load_results()
    print_summary(df)
    generate_all(df)
