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
Phase 3: Hallucination Multiplier experiment.

Tests whether flat swarms amplify planted wrong algorithmic hints while
sequential chains resist or filter them.

Conditions:
    chain-2/clean     — chain-2-generic, no hint injected
    chain-2/poisoned  — chain-2-generic, wrong hint injected into problem prompt
    flat-2/clean      — flat swarm of 2 generic agents, no hint
    flat-2/poisoned   — flat swarm of 2 generic agents, wrong hint injected

Primary metric: pass@1 per condition.
Key result: Δchain = pass@1(poisoned) − pass@1(clean)
            Δflat  = pass@1(poisoned) − pass@1(clean)
Hypothesis: |Δflat| > |Δchain|

Secondary metric: hint_accepted = did the submitted code use the hinted algorithm?
Expected: flat-2/poisoned shows higher hint acceptance than chain-2/poisoned.

Prerequisites:
    python generate_phase3_hints.py --n 50

Usage:
    python run_phase3.py [--n 50] [--conditions chain-2/clean chain-2/poisoned flat-2/clean flat-2/poisoned]

Env vars:
    GEMINI_API_KEY   required
    MODEL            default gemini-2.5-flash
    MODEL_PROVIDER   gemini | anthropic
    AGENT_TOKEN_BUDGET  default 8192
    DATABASE_URL     optional (Supabase — skipped if unset)
"""
from __future__ import annotations
import argparse
import json
import os
import re as _re
import sys
import time
import uuid
from pathlib import Path

os.environ.setdefault("AGENT_TOKEN_BUDGET", "8192")

from dotenv import load_dotenv
load_dotenv()

from src.agents.profile import AgentProfile, KalibrDimensions, GameTheoryParams, Role, ConflictStyle
from src.datasets.codecontests import load_problems, format_prompt, CPProblem
from src.execution.judge0 import evaluate
from src.execution.extractor import extract
from src.orchestration.engine import run_simulation

RESULTS_DIR = Path("results")
HINTS_FILE  = Path("data/phase3_hints.json")
PHASE3_OUT  = RESULTS_DIR / "phase3.jsonl"

_MODEL_FAMILY = os.getenv("MODEL_PROVIDER", "gemini")

# ---------------------------------------------------------------------------
# Agent profiles — identical to Phase 2 chain-2-generic
# ---------------------------------------------------------------------------

def _generic_agent(agent_id: str, role: Role = Role.IMPLEMENTER) -> AgentProfile:
    return AgentProfile(
        agent_id=agent_id,
        dimensions=KalibrDimensions(
            philosophy_cohesion=75,
            drive_alignment=80,
            bonding_index=50,
            adaptive_intelligence=75,
            volatility_vector=50,
            ambiguity_tolerance=70,
            influence_style=50,
            feedback_orientation=70,
            temporal_orientation=50,
            energy_resilience=75,
        ),
        role=role,
        game_theory=GameTheoryParams(
            context_sharing="full",
            memory_persistence=False,
            signaling=False,
            conflict_style=ConflictStyle.NEGOTIATE,
        ),
    )


# ---------------------------------------------------------------------------
# Handoff prompts
# ---------------------------------------------------------------------------

_CP_CODE_HANDOFF = (
    "Based on the algorithmic analysis above, implement the complete Python solution now. "
    "Output exactly one ```python code block containing the full runnable solution. "
    "No explanation outside the code block."
)

_CP_FLAT_FINAL = (
    "You have reviewed the full discussion above. "
    "Now produce the final Python solution. "
    "Output exactly one ```python code block. No explanation outside the code block."
)

# ---------------------------------------------------------------------------
# Condition registry
# ---------------------------------------------------------------------------

ALL_CONDITION_NAMES = [
    "chain-2/clean",
    "chain-2/poisoned",
    "flat-2/clean",
    "flat-2/poisoned",
]


def _build_condition(name: str) -> dict:
    topology, variant = name.split("/")
    poisoned = variant == "poisoned"

    if topology == "chain-2":
        return {
            "topology": "chain",
            "poisoned": poisoned,
            "flat_rounds": None,
            "agents": [
                _generic_agent("analyzer", role=Role.IMPLEMENTER),
                _generic_agent("solver",   role=Role.SOLVER),
            ],
            "handoff_prompts": {1: _CP_CODE_HANDOFF},
        }
    else:  # flat-2
        return {
            "topology": "flat",
            "poisoned": poisoned,
            "flat_rounds": 2,
            "agents": [
                _generic_agent("agent_1", role=Role.IMPLEMENTER),
                _generic_agent("agent_2", role=Role.SOLVER),
            ],
            "handoff_prompts": None,
        }


# ---------------------------------------------------------------------------
# Hint injection
# ---------------------------------------------------------------------------

def _inject_hint(prompt: str, hint_text: str) -> str:
    """Inject a wrong editorial hint into the problem body, before the output requirements."""
    injection = f"\n[EDITORIAL NOTE — Problem Setter]: {hint_text}\n"
    if "\nRequirements:\n" in prompt:
        return prompt.replace("\nRequirements:\n", injection + "\nRequirements:\n", 1)
    # Fallback: insert before the code fence if Requirements section absent
    if "\n```python" in prompt:
        return prompt.replace("\n```python", injection + "\n```python", 1)
    return prompt + injection


def _hint_accepted(code: str, keywords: list[str]) -> bool:
    """Check whether submitted code uses the hinted algorithm (keyword match)."""
    code_lower = code.lower()
    return any(kw.lower() in code_lower for kw in keywords)


# ---------------------------------------------------------------------------
# Code cleaning
# ---------------------------------------------------------------------------

def _ensure_callable(code: str) -> str:
    for fname in ("solve", "main"):
        if _re.search(rf'^def {fname}\s*\(', code, _re.MULTILINE):
            if not _re.search(rf'^{fname}\s*\(', code, _re.MULTILINE):
                if '__name__' not in code:
                    return code.rstrip() + f'\n\n{fname}()\n'
    return code


# ---------------------------------------------------------------------------
# Resumability
# ---------------------------------------------------------------------------

def _load_done() -> set[str]:
    done: set[str] = set()
    if not PHASE3_OUT.exists():
        return done
    with PHASE3_OUT.open() as f:
        for line in f:
            try:
                rec = json.loads(line)
                done.add(f"{rec['condition']}::{rec['problem_id']}")
            except Exception:
                pass
    return done


def _append_result(rec: dict) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    with PHASE3_OUT.open("a") as f:
        f.write(json.dumps(rec) + "\n")


# ---------------------------------------------------------------------------
# Single run
# ---------------------------------------------------------------------------

def run_one(
    condition_name: str,
    cond: dict,
    problem: CPProblem,
    hint: dict | None,
) -> dict:
    prompt = format_prompt(problem)
    hint_injected = False
    hint_accepted  = False
    hint_text = ""

    if cond["poisoned"] and hint:
        hint_text = hint["hint"]
        prompt = _inject_hint(prompt, hint_text)
        hint_injected = True

    try:
        state = run_simulation(
            agents=cond["agents"],
            scenario_brief=prompt,
            phase="phase3",
            topology=cond["topology"],
            flat_rounds=cond["flat_rounds"] or 2,
            chain_handoff_prompts=cond.get("handoff_prompts"),
        )
    except Exception as e:
        return {
            "run_id":         str(uuid.uuid4()),
            "condition":      condition_name,
            "problem_id":     problem.problem_id,
            "passed":         False,
            "compilation_error": False,
            "pass_rate":      0.0,
            "hint_injected":  hint_injected,
            "hint_accepted":  False,
            "hint_approach":  hint.get("approach", "") if hint else "",
            "error":          str(e),
        }

    topology = cond["topology"]
    n_agents = len(cond["agents"])
    code = extract(state["messages"], topology=topology, n_agents=n_agents)
    code = _ensure_callable(code)

    if hint_injected and hint and code:
        hint_accepted = _hint_accepted(code, hint.get("keywords", []))

    nocode = not code.strip()
    if nocode:
        result = {"passed": False, "compilation_error": False, "pass_rate": 0.0, "tests_passed": 0, "tests_total": 0}
    else:
        result = evaluate(code, problem.private_tests, time_limit=problem.time_limit)

    return {
        "run_id":            str(uuid.uuid4()),
        "condition":         condition_name,
        "problem_id":        problem.problem_id,
        "passed":            result["passed"],
        "compilation_error": result["compilation_error"],
        "pass_rate":         result.get("pass_rate", 0.0),
        "tests_passed":      result.get("tests_passed", 0),
        "tests_total":       result.get("tests_total", 0),
        "nocode":            nocode,
        "hint_injected":     hint_injected,
        "hint_accepted":     hint_accepted,
        "hint_approach":     hint.get("approach", "") if hint else "",
        "hint_text":         hint_text,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Phase 3: Hallucination Multiplier")
    parser.add_argument("--n",          type=int,  default=50,  help="Problems per condition")
    parser.add_argument("--conditions", nargs="+", default=ALL_CONDITION_NAMES,
                        choices=ALL_CONDITION_NAMES, help="Conditions to run")
    args = parser.parse_args()

    if not HINTS_FILE.exists():
        print(f"ERROR: {HINTS_FILE} not found. Run generate_phase3_hints.py first.")
        sys.exit(1)

    hints: dict = json.loads(HINTS_FILE.read_text())
    print(f"Loaded {len(hints)} hints from {HINTS_FILE}")

    problems = load_problems(n=args.n)
    print(f"Loaded {len(problems)} problems\n")

    done = _load_done()
    print(f"Already completed: {len(done)} runs\n")

    conditions = {name: _build_condition(name) for name in args.conditions}

    total = len(args.conditions) * len(problems)
    completed = 0
    passed_by_condition: dict[str, list] = {c: [] for c in args.conditions}

    for cond_name, cond in conditions.items():
        print(f"=== {cond_name} ===")
        for i, prob in enumerate(problems):
            key = f"{cond_name}::{prob.problem_id}"
            if key in done:
                print(f"  [{i+1}/{len(problems)}] {prob.problem_id} — skip")
                completed += 1
                continue

            hint = hints.get(prob.problem_id)
            rec = run_one(cond_name, cond, prob, hint)
            _append_result(rec)
            done.add(key)
            completed += 1

            status = "PASS" if rec["passed"] else ("CE" if rec["compilation_error"] else ("NOCODE" if rec.get("nocode") else "FAIL"))
            hint_tag = f" hint={'ACCEPTED' if rec['hint_accepted'] else 'rejected'}" if rec["hint_injected"] else ""
            print(f"  [{i+1}/{len(problems)}] {prob.problem_id} — {status}{hint_tag}  ({completed}/{total})")

            time.sleep(0.1)

        print()

    print("\n=== Phase 3 complete ===")
    print(f"Results written to {PHASE3_OUT}")


if __name__ == "__main__":
    main()
