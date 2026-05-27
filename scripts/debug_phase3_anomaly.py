"""
Phase 3 anomaly debugger.

Reads results/phase3.jsonl and answers the specific question:
Why did chain-2/poisoned accept the bad hint 70% of the time yet score 18% pass@1?

Prints:
  1. Passing chain-2/poisoned runs: hint_accepted, approach, hint text
  2. Acceptance rate split: passing vs failing runs (chain-2/poisoned)
  3. Flat-2/poisoned NoCode runs: what approaches caused total failure
  4. Verdict on whether the hints were actually wrong

Usage:
    python debug_phase3_anomaly.py
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

PHASE3_FILE = Path("results/phase3.jsonl")


def load() -> dict[str, list[dict]]:
    by_condition: dict[str, list[dict]] = defaultdict(list)
    with PHASE3_FILE.open() as f:
        for line in f:
            try:
                r = json.loads(line)
                by_condition[r["condition"]].append(r)
            except Exception:
                pass
    return dict(by_condition)


def main():
    data = load()

    # -----------------------------------------------------------------------
    # 1. Passing chain-2/poisoned runs — did they accept the hint?
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("CHAIN-2/POISONED — PASSING RUNS")
    print("=" * 70)
    poisoned_chain = data.get("chain-2/poisoned", [])
    passing = [r for r in poisoned_chain if r.get("passed")]
    failing = [r for r in poisoned_chain if not r.get("passed")]

    print(f"\nTotal: {len(poisoned_chain)}  |  Passing: {len(passing)}  |  Failing: {len(failing)}\n")

    for r in passing:
        accepted = "ACCEPTED" if r.get("hint_accepted") else "rejected"
        print(f"  [{accepted}] {r['problem_id']}")
        print(f"    approach : {r.get('hint_approach', '—')}")
        print(f"    hint     : {r.get('hint_text', '—')[:120]}")
        print()

    # -----------------------------------------------------------------------
    # 2. Acceptance rate: passing vs failing (chain-2/poisoned)
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("CHAIN-2/POISONED — ACCEPTANCE RATE SPLIT")
    print("=" * 70)

    pass_accepted = sum(1 for r in passing if r.get("hint_accepted"))
    fail_accepted = sum(1 for r in failing if r.get("hint_accepted"))

    print(f"\n  Passing runs ({len(passing)}): {pass_accepted} accepted hint  "
          f"({pass_accepted/len(passing)*100:.0f}%)" if passing else "  No passing runs.")
    print(f"  Failing runs ({len(failing)}): {fail_accepted} accepted hint  "
          f"({fail_accepted/len(failing)*100:.0f}%)" if failing else "")

    print()
    if passing and failing:
        if pass_accepted / len(passing) < fail_accepted / len(failing):
            print("  >> Hint acceptance is LOWER in passing runs.")
            print("     Passing runs tended to REJECT the hint and write correct code.")
            print("     The +4pp gain is driven by hint-resistant problems, not hint-following.")
        elif pass_accepted / len(passing) > fail_accepted / len(failing):
            print("  >> Hint acceptance is HIGHER in passing runs.")
            print("     The 'poison' hint was viable for those specific problems.")
            print("     The hint generator produced correct-or-near-correct approaches.")
        else:
            print("  >> Acceptance rate identical in passing and failing — inconclusive.")

    # -----------------------------------------------------------------------
    # 3. Flat-2/poisoned NoCode runs
    # -----------------------------------------------------------------------
    print()
    print("=" * 70)
    print("FLAT-2/POISONED — NOCODE RUNS (hint caused total failure)")
    print("=" * 70)
    flat_poisoned = data.get("flat-2/poisoned", [])
    nocode_runs = [r for r in flat_poisoned if r.get("nocode")]

    print(f"\nNoCode count: {len(nocode_runs)}\n")
    for r in nocode_runs:
        print(f"  {r['problem_id']}")
        print(f"    approach : {r.get('hint_approach', '—')}")
        print(f"    hint     : {r.get('hint_text', '—')[:120]}")
        print()

    # -----------------------------------------------------------------------
    # 4. Approach-level: which hints were accepted AND passed (chain-2/poisoned)
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("CHAIN-2/POISONED — APPROACHES THAT ACCEPTED AND PASSED")
    print("=" * 70)
    accepted_and_passed = [r for r in poisoned_chain if r.get("hint_accepted") and r.get("passed")]
    print(f"\n{len(accepted_and_passed)} runs accepted the hint AND passed:\n")
    for r in accepted_and_passed:
        print(f"  {r['problem_id']} — approach: {r.get('hint_approach', '—')}")
        print(f"    hint: {r.get('hint_text', '—')[:120]}")
        print()

    if accepted_and_passed:
        print("  >> These are the smoking gun. If the approach is a valid algorithm")
        print("     for that problem, the hint generator failed, not the agent.")
        print("     If the approach is wrong but the code passed anyway, the agent")
        print("     accepted the label but ignored it in execution.")


if __name__ == "__main__":
    main()
