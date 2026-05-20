from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import pearsonr
from pathlib import Path

OUTPUT_DIR = Path("reports")
OUTPUT_DIR.mkdir(exist_ok=True)

COMP_COLORS = {
    "drafted":        "#2196F3",
    "homogeneous":    "#F44336",
    "founder_brained":"#FF9800",
}
COMP_LABELS = {
    "drafted":        "Drafted (diversity-optimised)",
    "homogeneous":    "Homogeneous",
    "founder_brained":"Founder-brained",
}


def plot_bell_curve(df: pd.DataFrame):
    """
    Cognitive diversity (x) vs task score (y) — scatter + trend line.
    The agent-equivalent of Bell (2007)'s curvilinear diversity-performance curve.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    for comp, grp in df.groupby("composition_condition"):
        ax.scatter(
            grp["cognitive_diversity"], grp["task_score"],
            label=COMP_LABELS.get(comp, comp),
            color=COMP_COLORS.get(comp, "grey"),
            alpha=0.7, s=60,
        )

    # Fit a quadratic trend over all points (tests curvilinear hypothesis)
    x = df["cognitive_diversity"].values
    y = df["task_score"].values
    if len(x) > 3:
        coeffs = np.polyfit(x, y, 2)
        x_line = np.linspace(x.min(), x.max(), 200)
        y_line = np.polyval(coeffs, x_line)
        ax.plot(x_line, y_line, "k--", linewidth=1.5, label="Quadratic trend (all)")

        r, p = pearsonr(x, y)
        ax.set_title(
            f"Cognitive Diversity vs Task Score\n"
            f"Agent-equivalent of Bell (2007) — r={r:.2f}, p={p:.3f}",
            fontsize=13,
        )

    ax.set_xlabel("Cognitive Diversity Score (mean σ across 10 dimensions)", fontsize=11)
    ax.set_ylabel("Mean Task Score (0–100)", fontsize=11)
    ax.legend()
    ax.set_ylim(0, 105)
    fig.tight_layout()
    path = OUTPUT_DIR / "bell_curve.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_team_size_effect(df: pd.DataFrame):
    """
    Team size (x) vs mean task score (y), one line per composition.
    Shows where coordination costs start exceeding coordination benefits.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    for comp, grp in df.groupby("composition_condition"):
        means = grp.groupby("team_size")["task_score"].mean()
        ax.plot(
            means.index, means.values,
            marker="o", linewidth=2,
            color=COMP_COLORS.get(comp, "grey"),
            label=COMP_LABELS.get(comp, comp),
        )
        # Shade std dev band
        stds = grp.groupby("team_size")["task_score"].std().fillna(0)
        ax.fill_between(
            means.index,
            means.values - stds.values,
            means.values + stds.values,
            alpha=0.1,
            color=COMP_COLORS.get(comp, "grey"),
        )

    ax.set_xlabel("Team Size", fontsize=11)
    ax.set_ylabel("Mean Task Score (0–100)", fontsize=11)
    ax.set_title("Team Size vs Performance by Composition", fontsize=13)
    ax.set_xticks([1, 2, 4, 8, 16])
    ax.legend()
    ax.set_ylim(0, 105)
    fig.tight_layout()
    path = OUTPUT_DIR / "team_size_effect.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_instrument_proxies(df: pd.DataFrame):
    """
    Heatmap: composition (rows) × instrument proxy (cols).
    Shows which cohesion dimensions differ most between compositions.
    """
    proxies = {
        "GEQ Task":    "geq_task",
        "GEQ Social":  "geq_social",
        "TCI Innov.":  "tci_innovation",
        "FIRO Incl.":  "firo_inclusion",
        "Task Score":  "task_score",
        "Novel Appr.": "novel_approaches",
        "Contradict.": "contradictions",
    }

    comps = ["drafted", "homogeneous", "founder_brained"]
    data = []
    for comp in comps:
        grp = df[df["composition_condition"] == comp]
        row = [grp[col].mean() for col in proxies.values()]
        data.append(row)

    matrix = np.array(data, dtype=float)
    # Normalise each column to 0-1 for display
    col_min = matrix.min(axis=0)
    col_max = matrix.max(axis=0)
    col_range = np.where(col_max - col_min == 0, 1, col_max - col_min)
    norm = (matrix - col_min) / col_range

    fig, ax = plt.subplots(figsize=(11, 4))
    im = ax.imshow(norm, cmap="RdYlGn", aspect="auto", vmin=0, vmax=1)

    ax.set_xticks(range(len(proxies)))
    ax.set_xticklabels(list(proxies.keys()), fontsize=10)
    ax.set_yticks(range(len(comps)))
    ax.set_yticklabels([COMP_LABELS[c] for c in comps], fontsize=10)

    for i in range(len(comps)):
        for j in range(len(proxies)):
            ax.text(j, i, f"{matrix[i, j]:.1f}", ha="center", va="center",
                    fontsize=9, color="black")

    plt.colorbar(im, ax=ax, label="Normalised score (green = higher)")
    ax.set_title("Instrument Proxy Scores by Composition (mean across all scenarios & team sizes)",
                 fontsize=12)
    fig.tight_layout()
    path = OUTPUT_DIR / "instrument_proxies.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_scenario_breakdown(df: pd.DataFrame):
    """
    Mean task score per scenario, broken down by composition.
    """
    scenarios = df["scenario_id"].unique()
    comps     = ["drafted", "homogeneous", "founder_brained"]
    x         = np.arange(len(scenarios))
    width     = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, comp in enumerate(comps):
        means = [
            df[(df["scenario_id"] == s) & (df["composition_condition"] == comp)]["task_score"].mean()
            for s in scenarios
        ]
        ax.bar(x + i * width, means, width,
               label=COMP_LABELS.get(comp, comp),
               color=COMP_COLORS.get(comp, "grey"),
               alpha=0.85)

    ax.set_xticks(x + width)
    ax.set_xticklabels(scenarios, rotation=15, fontsize=10)
    ax.set_ylabel("Mean Task Score (0–100)", fontsize=11)
    ax.set_title("Task Score by Scenario and Composition", fontsize=13)
    ax.legend()
    ax.set_ylim(0, 105)
    fig.tight_layout()
    path = OUTPUT_DIR / "scenario_breakdown.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def generate_all(df: pd.DataFrame):
    print(f"\nGenerating charts from {len(df)} runs...\n")
    plot_bell_curve(df)
    plot_team_size_effect(df)
    plot_instrument_proxies(df)
    plot_scenario_breakdown(df)
    print("\nAll charts saved to /reports/")
