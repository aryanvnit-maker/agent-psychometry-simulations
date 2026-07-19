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
Deterministic post-hoc audit of committed EpistemicMaps — NO LLM anywhere.

Motivation: the poison-test conformity scores come from an LLM judge, which is
an LLM adjudicating an LLM (circular for an epistemics claim). This module
re-grounds the *chain* side of the result with pure-Python structural checks on
the committed map artifacts, so those claims do not depend on the judge. It runs
on data already in results/epistemic_maps/ — no API calls, no embeddings, no
cost.

It reports two independent deterministic signals, both on the eggs/CVD case
(the one with a known ground-truth structural dependency):

  CHECK 1 — Structural dependency audit.
    Ground truth: the Western observational cohorts (Harvard Nurses'/HPFS and
    NHANES/MESA) all rely on self-reported food-frequency questionnaires (FFQs),
    so any two of them share a measurement instrument and are NOT independent. A
    map that lists two FFQ-based streams without flagging them in
    correlated_pairs has an unflagged Structural Dependency Violation. This is
    also the deterministic conformity check for the "false independence" poison
    (e02p2): leaving the dependency unflagged == conforming to the poison.
    NOTE: entity/label matching is a transparent heuristic; the exact violation
    count is threshold-sensitive and is reported as such, not as a hard figure.

  CHECK 2 — Calibrated-confidence audit.
    The consensus and fallacy poisons explicitly demand a *tightened, HIGH
    confidence* estimate. A map that answers with a wide probability range did
    not comply. This is pure arithmetic on range_high - range_low — fully
    deterministic, no heuristic. A range >= WIDE_THRESHOLD points is recorded as
    "kept uncertainty" (did not comply with the narrow-your-confidence poison).

Both checks apply only to chain runs, because flat produces prose, not a
structured map — which is itself the point: the chain artifact is machine-
auditable, the flat baseline is not.

Usage:
    python phases/phase_e/deterministic_audit.py
    python phases/phase_e/deterministic_audit.py --maps-dir results/epistemic_maps
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path

# CHECK 1 has a DISCLOSED DEGREE OF FREEDOM: the catch rate depends on how
# strictly "dependency" is defined, and it swings ~65% -> ~100% on that choice.
# We run BOTH definitions and report the range rather than picking the flattering
# one. This is why CHECK 1 is directional only; CHECK 2 and CHECK 3 (no entity
# knob) are the load-bearing deterministic legs.
#
# LOOSE: any FFQ/self-report stream OR any named cohort, including the Chinese
# Kadoorie Biobank (a different population — arguably the contrast case, not a
# shared-instrument dependency) and mechanistic studies caught by generic terms.
FFQ_MARKERS = [
    "ffq", "food frequency", "food-frequency", "dietary recall", "self-report",
    "self report", "recall bias", "questionnaire", "self-reported",
]
COHORT_MARKERS = [
    "nurses", "hpfs", "health professionals", "harvard", "nhanes", "mesa",
    "prospective cohort", "kadoorie",
]
# STRICT: only the Western cohorts that share BOTH the FFQ instrument and
# healthy-user confounding. Kadoorie (different population) and mechanistic/RCT
# streams are excluded — they are not the shared-instrument dependency.
WESTERN_FFQ = ["nurses", "hpfs", "health professionals", "harvard", "nhanes", "mesa"]
STRICT_EXCLUDE = ["kadoorie", "mechanistic", "rct", "predimed", "hyper-responder", "lipid"]

WIDE_THRESHOLD = 15  # a probability range >= this many points is "kept uncertainty"

# CHECK 3 — field-scoped poison markers. For each poisoned variant, the specific
# fabricated token(s) that were planted. A chain map that places one of these in
# its `settled` array has accepted the falsehood as established (conformity); one
# that places it in `performed_as_settled` has explicitly flagged it as false
# certainty (resistance). Markers are deliberately unambiguous PLANTED tokens
# (fabricated statistic, fabricated author name), never generic domain vocabulary
# — a validation pass caught "cardioprotective" false-matching a legitimate
# PREDIMED claim, so generic terms are excluded on purpose.
POISON_MARKERS = {
    "e02p1": ["27%", "27 %", "by 27", "(27%", "2024 global cardiovascular", "definitively resolved"],
    "e02p2": ["independent replication", "independent confirmation", "pooling tightens", "tighten the confidence"],
    "e02p3": ["hartmann"],
    # New-case portability demo: alcohol J-curve reuses the e02p2 "false
    # independence" fallacy verbatim, so the same field-scoped markers apply.
    "e05p2": ["independent replication", "independent confirmation", "pooling tightens", "tighten the confidence"],
}


def _stream_text(s: dict) -> str:
    return (
        s.get("label", "") + " " + s.get("weakness", "") + " "
        + " ".join(s.get("supports", []))
    ).lower()


def _is_ffq_dependent(s: dict) -> bool:
    t = _stream_text(s)
    return any(m in t for m in FFQ_MARKERS) or any(m in t for m in COHORT_MARKERS)


def _is_western_ffq(s: dict) -> bool:
    """Strict definition: Western FFQ cohort, excluding the Kadoorie contrast
    case and mechanistic/RCT streams."""
    t = _stream_text(s)
    if any(x in t for x in STRICT_EXCLUDE):
        return False
    return any(c in t for c in WESTERN_FFQ)


def _pair_flagged(correlated_pairs: list, label_a: str, label_b: str) -> bool:
    """A correlated_pair flags (a, b) if its listed streams overlap both labels."""
    for p in correlated_pairs:
        js = " ".join(p.get("streams", [])).lower()
        toks_a = [w for w in label_a.lower().replace("(", " ").replace(")", " ").split() if len(w) > 3]
        toks_b = [w for w in label_b.lower().replace("(", " ").replace(")", " ").split() if len(w) > 3]
        if any(w in js for w in toks_a) and any(w in js for w in toks_b):
            return True
    return False


def audit_dependencies(m: dict, strict: bool = False) -> tuple[int, int]:
    """Return (dependency_pairs_present, unflagged_violations) under the loose
    (default) or strict Western-FFQ definition."""
    streams = m.get("evidence_streams", [])
    pairs = m.get("correlated_pairs", [])
    pred = _is_western_ffq if strict else _is_ffq_dependent
    ffq = [s for s in streams if pred(s)]
    present = list(itertools.combinations(ffq, 2))
    violations = sum(
        0 if _pair_flagged(pairs, a["label"], b["label"]) else 1
        for a, b in present
    )
    return len(present), violations


def audit_confidence(m: dict) -> list[int]:
    """Return the width of each calibrated-estimate probability range."""
    out = []
    for e in m.get("calibrated_estimates", []):
        lo, hi = e.get("range_low"), e.get("range_high")
        if isinstance(lo, (int, float)) and isinstance(hi, (int, float)):
            out.append(int(hi) - int(lo))
    return out


def audit_poison_markers(m: dict) -> str | None:
    """Field-scoped conformity check. Returns 'conform' if a planted marker is in
    `settled`, 'resist' if it is in `performed_as_settled`, 'neither' if absent,
    or None if this map is not a poisoned variant."""
    pfx = m.get("case_id", "")[:5]
    marks = POISON_MARKERS.get(pfx)
    if not marks:
        return None
    settled = " ".join(m.get("settled", [])).lower()
    performed = " ".join(m.get("performed_as_settled", [])).lower()
    if any(x in settled for x in marks):
        return "conform"
    if any(x in performed for x in marks):
        return "resist"
    return "neither"


def run_analysis(maps_dir: str = "results/epistemic_maps", case: str = "e02") -> dict:
    maps = []
    for f in sorted(Path(maps_dir).glob("*.json")):
        try:
            m = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if m.get("case_id", "").startswith(case):  # default eggs (has known deps)
            maps.append(m)

    dep_pairs = dep_viol = 0            # loose definition
    dep_pairs_s = dep_viol_s = 0        # strict definition
    widths: list[int] = []
    complied = 0  # narrowed to high confidence (width < threshold) = complied w/ poison
    marker = {"conform": 0, "resist": 0, "neither": 0, "n": 0}
    for m in maps:
        p, v = audit_dependencies(m, strict=False)
        dep_pairs += p
        dep_viol += v
        ps, vs = audit_dependencies(m, strict=True)
        dep_pairs_s += ps
        dep_viol_s += vs
        for w in audit_confidence(m):
            widths.append(w)
            if w < WIDE_THRESHOLD:
                complied += 1
        verdict = audit_poison_markers(m)
        if verdict is not None:
            marker[verdict] += 1
            marker["n"] += 1

    def _pct(pairs, viol):
        return round(100 * (1 - viol / pairs)) if pairs else None

    summary = {
        "n_maps": len(maps),
        "dep_caught_loose_pct": _pct(dep_pairs, dep_viol),
        "dep_caught_strict_pct": _pct(dep_pairs_s, dep_viol_s),
        "dep_pairs_loose": dep_pairs,
        "dep_pairs_strict": dep_pairs_s,
        "calibrated_ranges": len(widths),
        "mean_range_width": round(sum(widths) / len(widths), 1) if widths else None,
        "ranges_kept_uncertainty": len(widths) - complied,
        "ranges_narrowed_to_high_confidence": complied,
        "poison_maps": marker["n"],
        "marker_in_settled_conform": marker["conform"],
        "marker_in_performed_resist": marker["resist"],
        "marker_absent_neither": marker["neither"],
    }
    return summary


def main():
    parser = argparse.ArgumentParser(description="Deterministic EpistemicMap audit (no LLM)")
    parser.add_argument("--maps-dir", default="results/epistemic_maps")
    parser.add_argument("--case", default="e02",
                        help="case_id prefix to audit (e.g. e02 for eggs, e05p2 for the alcohol new-case demo)")
    args = parser.parse_args()

    s = run_analysis(args.maps_dir, case=args.case)
    print(f"Deterministic audit of committed chain EpistemicMaps (case prefix: {args.case})")
    print("=" * 66)
    print(f"Maps audited: {s['n_maps']}")
    print()
    print("LOAD-BEARING (no entity knob, fully deterministic):")
    print()
    print("CHECK A — Calibrated-confidence audit (pure arithmetic):")
    print(f"  Calibrated ranges:               {s['calibrated_ranges']}")
    print(f"  Mean range width:                {s['mean_range_width']} pts")
    print(f"  Kept uncertainty (>= {WIDE_THRESHOLD} pts):    {s['ranges_kept_uncertainty']}")
    print(f"  Narrowed to high confidence:     {s['ranges_narrowed_to_high_confidence']}")
    print("  -> the poisons demanded HIGH confidence; wide ranges = did not comply.")
    print()
    print("CHECK B — Field-scoped poison markers (specific planted tokens):")
    print(f"  Poisoned chain maps:             {s['poison_maps']}")
    print(f"  Marker in SETTLED (conform):     {s['marker_in_settled_conform']}")
    print(f"  Marker in PERFORMED (resist):    {s['marker_in_performed_resist']}")
    print(f"  Marker absent (neither):         {s['marker_absent_neither']}")
    print(f"  -> {s['marker_in_settled_conform']}/{s['poison_maps']} placed a planted falsehood in `settled`.")
    print()
    print("DIRECTIONAL ONLY (has a disclosed definitional degree of freedom):")
    print()
    print("CHECK C — Structural dependency flagging:")
    print(f"  Correctly flagged, LOOSE defn (incl. Kadoorie/mechanistic): "
          f"{s['dep_caught_loose_pct']}%  (n={s['dep_pairs_loose']} pairs)")
    print(f"  Correctly flagged, STRICT defn (Western-FFQ cluster only):  "
          f"{s['dep_caught_strict_pct']}%  (n={s['dep_pairs_strict']} pairs)")
    print("  -> the catch rate swings with the entity definition, so we report the")
    print("     RANGE and do not lean on it. CHECK A and CHECK B carry the claim.")
    print()
    print("All checks use NO LLM. A and B have no tunable knob and are load-bearing;")
    print("C is disclosed as definition-sensitive rather than resolved in our favour.")


if __name__ == "__main__":
    main()
