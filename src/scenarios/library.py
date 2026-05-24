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

from .base import Scenario

# ── Scenario 01: Series A Product Fork ───────────────────────────────────────
# Category: strategic | Phase: forming
# Tests: who takes initiative on an ambiguous brief, whether the team converges
# on a framework before debating specifics, and role self-assignment.
# Correct output: a structured recommendation with explicit reasoning on the
# four decision variables (traction, ceiling, burn rate, reversibility).

SERIES_A_FORK = Scenario(
    scenario_id="s01_series_a_fork",
    category="strategic",
    phase="forming",
    brief=(
        "A Series A startup has $2M runway (14 months at current burn). "
        "They have two product directions:\n\n"
        "Direction A — proven traction (3,200 paying users, $18K MRR, 4% monthly churn). "
        "Addressable market estimated at $120M. Growth has plateaued for 11 weeks.\n\n"
        "Direction B — 0 paying users, prototype only. "
        "Addressable market estimated at $1.4B. Requires 6 months of development "
        "before any revenue is possible. Two competitors entered this space 3 months ago.\n\n"
        "The board wants a clear recommendation: double down on A, pivot to B, or a "
        "structured hybrid. You have this conversation to produce it. "
        "State your recommendation and the three most important variables that drove it."
    ),
    rubric=(
        "Score the team output on the following:\n"
        "1. Did the team identify all four critical decision variables: "
        "traction data, market ceiling, runway constraint, and competitive timing? (25 points)\n"
        "2. Did the team reach an unambiguous recommendation — A, B, or hybrid with "
        "specific conditions? A non-answer scores 0. (30 points)\n"
        "3. Is the reasoning internally consistent? No contradictions between "
        "stated variables and final recommendation. (25 points)\n"
        "4. Did the team surface the primary downside of their recommended path? (20 points)\n\n"
        "Maximum score: 100. A score below 50 means the team failed the task."
    ),
    task_dimensions=["temporal_orientation", "drive_alignment", "ambiguity_tolerance"],
    max_turns=6,
)

# ── Scenario 02: Resource Allocation Under Constraint ────────────────────────
# Category: resource | Phase: storming
# Tests: whether agents negotiate or deadlock when forced into a zero-sum split.
# Correct output: an allocation decision with explicit trade-off acknowledgement.

RESOURCE_ALLOCATION = Scenario(
    scenario_id="s02_resource_allocation",
    category="resource",
    phase="storming",
    brief=(
        "Your team must allocate $500K across three initiatives. "
        "You cannot split evenly — one initiative must receive at least 50% of the budget.\n\n"
        "Initiative 1 — Engineering: Reduce infrastructure costs by 30%. "
        "ROI timeline: 4 months. No customer impact.\n\n"
        "Initiative 2 — Sales: Hire two enterprise AEs. "
        "ROI timeline: 9 months. Directly impacts Q3 revenue target.\n\n"
        "Initiative 3 — Product: Ship the feature most requested by churning customers. "
        "ROI timeline: 2 months. Directly impacts churn rate.\n\n"
        "Produce a specific allocation (dollars per initiative) and the single strongest "
        "objection to your allocation that a reasonable person would raise."
    ),
    rubric=(
        "Score the team output on the following:\n"
        "1. Did the team produce a specific dollar allocation that sums to $500K "
        "with one initiative receiving ≥$250K? (30 points)\n"
        "2. Was the allocation justified against the stated variables "
        "(ROI timeline, revenue impact, churn impact)? (30 points)\n"
        "3. Did the team surface a genuine objection to their own allocation — "
        "not a straw man? (20 points)\n"
        "4. Was a resolution reached without deadlock? "
        "If the team deadlocked, score 0 for this criterion. (20 points)\n\n"
        "Maximum score: 100."
    ),
    task_dimensions=["influence_style", "volatility_vector", "philosophy_cohesion"],
    max_turns=8,
)

# ── Scenario 03: Post-Mortem Under Pressure ───────────────────────────────────
# Category: evaluation | Phase: storming
# Tests: whether the team can produce genuine critique or defaults to mitigation.
# Correct output: three distinct root causes, not symptoms.

POST_MORTEM = Scenario(
    scenario_id="s03_post_mortem",
    category="evaluation",
    phase="storming",
    brief=(
        "A product launch failed. Key facts:\n\n"
        "- Feature shipped on time and on spec.\n"
        "- Activation rate: 11% (target was 40%).\n"
        "- 78% of users who activated churned within 7 days.\n"
        "- Customer support tickets in the first week: 340 (baseline: 45/week).\n"
        "- Sales used the feature as a key deal-closer in 6 contracts signed the month before launch. "
        "All 6 customers have escalated.\n\n"
        "Identify the three root causes of this failure. "
        "Do not identify symptoms or mitigations — root causes only. "
        "For each root cause, name the specific decision or non-decision that produced it "
        "and who was accountable."
    ),
    rubric=(
        "Score the team output on the following:\n"
        "1. Did the team produce exactly three root causes, not symptoms? "
        "A symptom is an observable outcome (e.g. 'low activation'). "
        "A root cause is the decision that produced it. (30 points)\n"
        "2. Did each root cause name a specific decision or non-decision? "
        "Vague causes ('poor planning') score 0 per cause. (30 points)\n"
        "3. Did the team assign accountability for each cause? (20 points)\n"
        "4. Did any agent challenge a proposed cause as a symptom rather than "
        "a root cause during the conversation? (20 points)\n\n"
        "Maximum score: 100."
    ),
    task_dimensions=["feedback_orientation", "philosophy_cohesion", "adaptive_intelligence"],
    max_turns=8,
)

# ── Scenario 04: Crisis Response ─────────────────────────────────────────────
# Category: crisis | Phase: performing
# Tests: speed of convergence, role coverage under pressure, quality under constraint.

SECURITY_BREACH = Scenario(
    scenario_id="s04_security_breach",
    category="crisis",
    phase="performing",
    brief=(
        "It is 11:47 PM. You have just been notified that a misconfigured S3 bucket "
        "has been publicly accessible for an unknown period. "
        "The bucket contains: user email addresses, hashed passwords, and payment metadata "
        "(last 4 digits + card type, no full PAN). "
        "Estimated affected users: 84,000. "
        "You have 45 minutes before a security researcher posts publicly.\n\n"
        "Produce in order:\n"
        "1. The three actions taken in the next 15 minutes.\n"
        "2. The customer notification draft (under 100 words).\n"
        "3. The single decision that cannot be reversed once made, "
        "and the condition under which you make it."
    ),
    rubric=(
        "Score the team output on the following:\n"
        "1. Do the three 15-minute actions include: bucket lockdown, "
        "internal escalation, and legal/compliance notification? (30 points)\n"
        "2. Does the customer notification: avoid speculation, "
        "state what was and was not exposed, and include a next step for the user? (30 points)\n"
        "3. Is the irreversible decision identified (public disclosure) with a "
        "specific, measurable trigger condition — not 'when we feel ready'? (25 points)\n"
        "4. Did the team produce all three outputs without deadlocking "
        "on any single item? (15 points)\n\n"
        "Maximum score: 100."
    ),
    task_dimensions=["energy_resilience", "ambiguity_tolerance", "drive_alignment"],
    max_turns=5,
)


ALL_SCENARIOS: dict[str, Scenario] = {
    s.scenario_id: s for s in [
        SERIES_A_FORK,
        RESOURCE_ALLOCATION,
        POST_MORTEM,
        SECURITY_BREACH,
    ]
}
