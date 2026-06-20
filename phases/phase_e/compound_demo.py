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
Phase E — Compound Demo: v1 → v2 epistemic map compounding.

Demonstrates the FLF "living document" pattern:
1. Loads a v1 EpistemicMap for COVID-19 origins from results/epistemic_maps/
   (produced by run_phase_e.py kalibr-chain condition).
2. Presents new evidence (Rootclaim post-debate response, Weissman Bayesian
   analysis, Chinese CDC supplementary market sampling data).
3. Runs kalibr-chain again with a CONTINUATION brief that includes the v1 map.
4. Parses the v2 EpistemicMap — which should extend v1 with updated estimates
   and newly resolved cruxes.
5. Prints a human-readable diff.

Usage:
    python phases/phase_e/compound_demo.py
    python phases/phase_e/compound_demo.py --v1-map results/epistemic_maps/<run_id>.json
    python phases/phase_e/compound_demo.py --dry-run   (shows continuation brief, no API call)

Output:
    results/epistemic_maps/<new_run_id>_v2.json
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import traceback
import uuid
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(override=True)

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.pool import initialise_pool
from src.agents.team import draft_team
from src.orchestration.engine import run_simulation
from src.evaluation.epistemic_schema import (
    EpistemicMap,
    EPISTEMIC_MAP_JSON_SCHEMA,
    parse_epistemic_map,
)

MAPS_DIR = Path("results/epistemic_maps")
SEED     = 99  # different from run_phase_e.py to get a different agent pair

NEW_COVID_EVIDENCE = """\
New evidence to integrate into the v1 map:

1. ROOTCLAIM POST-DEBATE RESPONSE (Saar Wilf, 2024):
   After losing the structured Rootclaim debate to Peter Miller on lab-origin
   hypothesis, Wilf published a critique arguing the debate format disadvantaged
   complex Bayesian updating. His prior on lab origin (60%) remained stable
   post-debate. Miller's win is contested as rhetorical rather than evidential.
   Implication: the debate itself is contested as an epistemic update.

2. WEISSMAN INDEPENDENT BAYESIAN ANALYSIS (Michael Weissman, 2023):
   An independent physicist applied Bayesian methods to the published evidence.
   Estimated posterior for lab origin: ~20-40% depending on base rate priors
   for zoonotic spillover near high-risk labs. Key finding: the furin cleavage
   site alone is insufficient to shift the estimate dramatically — it is a
   weak-to-moderate update depending on base rate assumptions.

3. CHINESE CDC SUPPLEMENTARY MARKET SAMPLING (Worobey et al. re-analysis, 2024):
   Additional market sampling data reinforced animal stall clustering. However:
   (a) sampling occurred weeks after initial outbreak; (b) no live animal tested
   positive; (c) market clustering is consistent with multiple scenarios.
"""

CONTINUATION_PROMPT_TEMPLATE = """\
You previously produced the following structured epistemic map (v1) for {label}:

PRIOR MAP (v1):
{v1_json}

New evidence has since emerged:
{new_evidence}

Your task: produce an UPDATED epistemic map (v2) that integrates this new evidence.

Rules:
- Set "version": 2 and "extends_version": 1
- In "new_evidence": list each piece of new evidence you integrated
- Update crux statuses if any crux has been partially or fully resolved
- Update probability ranges if the new evidence shifts them
- Add correlated pairs if the new evidence reveals new dependencies
- Do NOT re-state settled claims from v1 in "performed_as_settled" unless re-contested

Produce a valid JSON object matching this schema:
{schema}

Output ONLY the JSON — no prose before or after.
"""

CONTINUATION_SYNTHESIS_PROMPT = (
    "OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN.\n"
    "You are the terminal epistemic synthesis agent updating a prior map.\n"
    "Integrate the new evidence above into the v2 JSON EpistemicMap.\n"
    "Preserve uncertainty where warranted. Output ONLY the JSON — no prose.\n\n"
    f"Schema reference:\n{EPISTEMIC_MAP_JSON_SCHEMA}"
)


def _find_latest_covid_map() -> Path | None:
    if not MAPS_DIR.exists():
        return None
    candidates = []
    for p in MAPS_DIR.glob("*.json"):
        if "_v2" in p.name:
            continue
        try:
            data = json.loads(p.read_text())
            if data.get("case_id") == "e01_covid_origins":
                candidates.append(p)
        except Exception:
            pass
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def diff_maps(v1: EpistemicMap, v2: EpistemicMap) -> None:
    print("\n" + "=" * 60)
    print("EPISTEMIC MAP DIFF: v1 → v2")
    print("=" * 60)

    v1_cruxes = {c.question: c for c in v1.cruxes}
    v2_cruxes = {c.question: c for c in v2.cruxes}

    any_change = False
    for q, c2 in v2_cruxes.items():
        c1 = v1_cruxes.get(q)
        if c1 and c1.status != c2.status:
            print(f"\nCrux status changed:")
            print(f"  Q: {q[:80]}")
            print(f"  {c1.status} → {c2.status}")
            any_change = True
    new_cruxes = set(v2_cruxes) - set(v1_cruxes)
    for q in new_cruxes:
        print(f"\nNew crux: {q[:80]}")
        any_change = True
    if not any_change:
        print("\nNo crux changes.")

    v1_ests = {e.hypothesis: e for e in v1.calibrated_estimates}
    v2_ests = {e.hypothesis: e for e in v2.calibrated_estimates}
    print("\nProbability range changes:")
    est_changed = False
    for hyp, e2 in v2_ests.items():
        e1 = v1_ests.get(hyp)
        if e1 and (e1.range_low != e2.range_low or e1.range_high != e2.range_high):
            print(f"  {hyp[:60]}")
            print(f"    {e1.range_low}-{e1.range_high}%  →  {e2.range_low}-{e2.range_high}%")
            est_changed = True
    if not est_changed:
        print("  No range changes.")

    if v2.new_evidence:
        print("\nNew evidence integrated:")
        for ev in v2.new_evidence:
            print(f"  • {ev}")

    new_settled = set(v2.settled) - set(v1.settled)
    if new_settled:
        print("\nNewly settled:")
        for s in new_settled:
            print(f"  ✓ {s[:80]}")

    new_contested = set(v2.performed_as_settled) - set(v1.performed_as_settled)
    if new_contested:
        print("\nNewly flagged as performed-as-settled:")
        for s in new_contested:
            print(f"  ! {s[:80]}")


def run_compound_demo(v1_path: Path | None = None, dry_run: bool = False) -> None:
    if v1_path is None:
        v1_path = _find_latest_covid_map()
    if v1_path is None:
        print("No v1 COVID-19 epistemic map found in results/epistemic_maps/")
        print("Run: python phases/phase_e/run_phase_e.py --conditions kalibr-chain")
        return

    v1_data = json.loads(v1_path.read_text())
    v1      = EpistemicMap(**v1_data)
    print(f"Loaded v1 map: {v1_path.name}")
    print(f"  case_id={v1.case_id}  cruxes={len(v1.cruxes)}  estimates={len(v1.calibrated_estimates)}")

    continuation_brief = CONTINUATION_PROMPT_TEMPLATE.format(
        label="COVID-19 Origins",
        v1_json=v1_path.read_text(),
        new_evidence=NEW_COVID_EVIDENCE,
        schema=EPISTEMIC_MAP_JSON_SCHEMA,
    )

    if dry_run:
        print("\n[dry-run] Continuation brief (first 800 chars):")
        print(continuation_brief[:800])
        print("...")
        return

    run_id  = str(uuid.uuid4())
    pool    = initialise_pool(seed=SEED)
    workers = [a for a in pool if not a.is_judge]

    from src.scenarios.epistemic import COVID_ORIGINS
    team, _ = draft_team(workers, 2, COVID_ORIGINS.task_dimensions, "drafted")

    print(f"\nRunning kalibr-chain continuation (run_id={run_id[:8]}…)")
    try:
        state = run_simulation(
            agents=team,
            scenario_brief=continuation_brief,
            phase=COVID_ORIGINS.phase,
            topology="chain",
            chain_handoff_prompts={1: CONTINUATION_SYNTHESIS_PROMPT},
            default_handoff=None,
        )
    except Exception as e:
        print(f"ERROR in simulation: {e}")
        traceback.print_exc()
        return

    last_assistant = next(
        (m["content"] for m in reversed(state["messages"])
         if isinstance(m, dict) and m.get("role") == "assistant"),
        ""
    )
    v2 = parse_epistemic_map(last_assistant)

    if v2 is None:
        print("Could not parse v2 EpistemicMap. Raw output (first 500 chars):")
        print(last_assistant[:500])
        return

    v2.case_id         = "e01_covid_origins"
    v2.version         = 2
    v2.extends_version = 1

    out_path = MAPS_DIR / f"{run_id}_v2.json"
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(v2.model_dump_json(indent=2))
    print(f"Saved v2 map: {out_path.name}")

    diff_maps(v1, v2)

    print(f"\n{'='*60}")
    print(f"v1: {v1_path}")
    print(f"v2: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Phase E compound demo: v1 → v2")
    parser.add_argument("--v1-map",  type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run_compound_demo(v1_path=args.v1_map, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
