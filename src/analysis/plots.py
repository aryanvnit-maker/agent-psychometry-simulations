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


def plot_barrick(df: pd.DataFrame):
    """
    Barrick et al. (1998) replication.
    Tests whether mean AND variance of conscientiousness/agreeableness proxies
    predict task score — variance should matter as much as mean.
    """
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle(
        "Barrick, Stewart, Neubert & Mount (1998) — Agent Replication\n"
        "Do mean AND variance of conscientiousness/agreeableness predict performance?",
        fontsize=12,
    )

    pairs = [
        ("conscientiousness_mean",     "task_score", "Conscientiousness Mean",     axes[0, 0]),
        ("conscientiousness_variance", "task_score", "Conscientiousness Variance", axes[0, 1]),
        ("agreeableness_mean",         "task_score", "Agreeableness Mean",         axes[1, 0]),
        ("agreeableness_variance",     "task_score", "Agreeableness Variance",     axes[1, 1]),
    ]

    for x_col, y_col, label, ax in pairs:
        for comp, grp in df.groupby("composition_condition"):
            ax.scatter(grp[x_col], grp[y_col],
                       color=COMP_COLORS.get(comp, "grey"),
                       label=COMP_LABELS.get(comp, comp),
                       alpha=0.7, s=50)

        x = df[x_col].values
        y = df[y_col].values
        if len(x) > 3 and np.std(x) > 0:
            m, b = np.polyfit(x, y, 1)
            x_line = np.linspace(x.min(), x.max(), 100)
            ax.plot(x_line, m * x_line + b, "k--", linewidth=1.2)
            r, p = pearsonr(x, y)
            ax.set_title(f"{label}\nr={r:.2f}, p={p:.3f}", fontsize=10)
        else:
            ax.set_title(label, fontsize=10)

        ax.set_xlabel(label, fontsize=9)
        ax.set_ylabel("Task Score", fontsize=9)
        ax.set_ylim(0, 105)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    seen = {}
    unique = [(h, l) for h, l in zip(handles, labels) if l not in seen and not seen.update({l: True})]
    fig.legend([h for h, _ in unique], [l for _, l in unique],
               loc="lower center", ncol=3, fontsize=9, bbox_to_anchor=(0.5, 0.01))
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    path = OUTPUT_DIR / "barrick_replication.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_aristotle(df: pd.DataFrame):
    """
    Google Project Aristotle (2015) replication.
    Tests whether psychological safety score predicts task score
    better than composition alone.
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(
        "Google Project Aristotle (2015) — Agent Replication\n"
        "Does psychological safety predict performance better than composition?",
        fontsize=12,
    )

    # Left: psych safety vs task score
    ax = axes[0]
    for comp, grp in df.groupby("composition_condition"):
        ax.scatter(grp["psych_safety"], grp["task_score"],
                   color=COMP_COLORS.get(comp, "grey"),
                   label=COMP_LABELS.get(comp, comp),
                   alpha=0.7, s=60)
    x = df["psych_safety"].values
    y = df["task_score"].values
    if np.std(x) > 0:
        m, b = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_line, m * x_line + b, "k--", linewidth=1.5)
        r, p = pearsonr(x, y)
        ax.set_title(f"Psychological Safety vs Task Score\nr={r:.2f}, p={p:.3f}", fontsize=11)
    ax.set_xlabel("Psychological Safety Score (composite)", fontsize=10)
    ax.set_ylabel("Task Score", fontsize=10)
    ax.set_ylim(0, 105)
    ax.legend(fontsize=8)

    # Right: mean psych safety by composition as bar chart
    ax2 = axes[1]
    comps = ["drafted", "homogeneous", "founder_brained"]
    means = [df[df["composition_condition"] == c]["psych_safety"].mean() for c in comps]
    colors = [COMP_COLORS[c] for c in comps]
    bars = ax2.bar([COMP_LABELS[c] for c in comps], means, color=colors, alpha=0.85)
    ax2.bar_label(bars, fmt="%.1f", fontsize=10)
    ax2.set_ylabel("Mean Psychological Safety Score", fontsize=10)
    ax2.set_title("Safety Score by Composition", fontsize=11)
    ax2.set_ylim(0, 105)
    ax2.tick_params(axis="x", labelsize=8)

    fig.tight_layout()
    path = OUTPUT_DIR / "aristotle_replication.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_geq(df: pd.DataFrame):
    """
    GEQ (Carron et al. 1985) — task cohesion vs social cohesion.
    Tests whether the two dimensions diverge across compositions,
    as they do in human teams.
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(
        "GEQ — Group Environment Questionnaire (Carron et al. 1985) — Agent Replication\n"
        "Do task cohesion and social cohesion diverge across compositions?",
        fontsize=12,
    )

    comps = ["drafted", "homogeneous", "founder_brained"]

    # Left: scatter task vs social cohesion per run
    ax = axes[0]
    for comp, grp in df.groupby("composition_condition"):
        ax.scatter(grp["geq_task"], grp["geq_social"],
                   color=COMP_COLORS.get(comp, "grey"),
                   label=COMP_LABELS.get(comp, comp),
                   alpha=0.7, s=60)
    ax.plot([0, 100], [0, 100], "grey", linestyle=":", linewidth=1, label="Task = Social")
    ax.set_xlabel("GEQ Task Cohesion", fontsize=10)
    ax.set_ylabel("GEQ Social Cohesion", fontsize=10)
    ax.set_title("Task vs Social Cohesion per Run", fontsize=11)
    ax.legend(fontsize=8)
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 105)

    # Right: grouped bar — task vs social by composition
    ax2 = axes[1]
    x = np.arange(len(comps))
    w = 0.35
    task_means   = [df[df["composition_condition"] == c]["geq_task"].mean() for c in comps]
    social_means = [df[df["composition_condition"] == c]["geq_social"].mean() for c in comps]
    b1 = ax2.bar(x - w/2, task_means,   w, label="Task Cohesion",   color="#1565C0", alpha=0.85)
    b2 = ax2.bar(x + w/2, social_means, w, label="Social Cohesion", color="#43A047", alpha=0.85)
    ax2.bar_label(b1, fmt="%.1f", fontsize=9)
    ax2.bar_label(b2, fmt="%.1f", fontsize=9)
    ax2.set_xticks(x)
    ax2.set_xticklabels([COMP_LABELS[c] for c in comps], fontsize=8)
    ax2.set_ylabel("Mean Score (0–100)", fontsize=10)
    ax2.set_title("Task vs Social Cohesion by Composition", fontsize=11)
    ax2.legend()
    ax2.set_ylim(0, 115)

    fig.tight_layout()
    path = OUTPUT_DIR / "geq_replication.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_tci_firo(df: pd.DataFrame):
    """
    TCI (Anderson & West 1994) + FIRO-B (Schutz) combined.
    TCI: does innovation climate correlate with novel approaches?
    FIRO-B: does inclusion score predict task performance?
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(
        "TCI (Anderson & West 1994) + FIRO-B — Agent Replication",
        fontsize=12,
    )

    # Left: TCI — tci_innovation vs novel_approaches (proxy validation)
    ax = axes[0]
    for comp, grp in df.groupby("composition_condition"):
        ax.scatter(grp["tci_innovation"], grp["novel_approaches"],
                   color=COMP_COLORS.get(comp, "grey"),
                   label=COMP_LABELS.get(comp, comp),
                   alpha=0.7, s=60)
    x = df["tci_innovation"].values
    y = df["novel_approaches"].values
    if np.std(x) > 0:
        m, b = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_line, m * x_line + b, "k--", linewidth=1.3)
        r, p = pearsonr(x, y)
        ax.set_title(f"TCI: Innovation Climate vs Novel Approaches\nr={r:.2f}, p={p:.3f}", fontsize=10)
    ax.set_xlabel("TCI Innovation Score (judge-rated)", fontsize=9)
    ax.set_ylabel("Novel Approaches Count", fontsize=9)
    ax.legend(fontsize=8)

    # Right: FIRO-B inclusion vs task score
    ax2 = axes[1]
    for comp, grp in df.groupby("composition_condition"):
        ax2.scatter(grp["firo_inclusion"], grp["task_score"],
                    color=COMP_COLORS.get(comp, "grey"),
                    label=COMP_LABELS.get(comp, comp),
                    alpha=0.7, s=60)
    x2 = df["firo_inclusion"].values
    y2 = df["task_score"].values
    if np.std(x2) > 0:
        m2, b2 = np.polyfit(x2, y2, 1)
        x_line2 = np.linspace(x2.min(), x2.max(), 100)
        ax2.plot(x_line2, m2 * x_line2 + b2, "k--", linewidth=1.3)
        r2, p2 = pearsonr(x2, y2)
        ax2.set_title(f"FIRO-B: Inclusion vs Task Score\nr={r2:.2f}, p={p2:.3f}", fontsize=10)
    ax2.set_xlabel("FIRO-B Inclusion (fraction of agents addressed)", fontsize=9)
    ax2.set_ylabel("Task Score", fontsize=9)
    ax2.set_ylim(0, 105)
    ax2.legend(fontsize=8)

    fig.tight_layout()
    path = OUTPUT_DIR / "tci_firo_replication.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def generate_all(df: pd.DataFrame):
    print(f"\nGenerating charts from {len(df)} runs...\n")
    plot_bell_curve(df)
    plot_team_size_effect(df)
    plot_instrument_proxies(df)
    plot_scenario_breakdown(df)
    plot_barrick(df)
    plot_aristotle(df)
    plot_geq(df)
    plot_tci_firo(df)
    print("\nAll charts saved to /reports/")
