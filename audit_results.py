import json
from pathlib import Path
from collections import defaultdict

records = [json.loads(l) for l in Path("results/meta_orchestrator.jsonl").read_text().splitlines() if l.strip()]
print(f"Total records: {len(records)}")

errors = [r for r in records if r.get("error")]
print(f"Records with errors: {len(errors)}")
for e in errors:
    print(f"  {e['condition']} :: {e['task_id']} -- {str(e.get('error'))[:100]}")

j_none = [r for r in records if r.get("task_type") == "judgment" and r.get("task_score") is None]
print(f"Judgment with None score: {len(j_none)}")
for r in j_none:
    print(f"  {r['condition']} :: {r['task_id']}")

print()
by_scenario = defaultdict(lambda: defaultdict(list))
for r in records:
    if r.get("task_type") == "judgment":
        scenario = r["task_id"].rsplit("/run", 1)[0]
        by_scenario[scenario][r["condition"]].append(r.get("task_score"))

print("Individual judgment scores per scenario:")
for s in sorted(by_scenario):
    print(f"\n  {s}:")
    for c in ["static-judgment", "static-execution", "meta-router"]:
        scores = by_scenario[s][c]
        print(f"    {c:<25} {scores}")
