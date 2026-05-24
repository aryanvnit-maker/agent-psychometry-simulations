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


# ── Scenario 05: System Scaling Decision ─────────────────────────────────────
# Category: technical | Phase: performing
# Tests: whether the team correctly identifies the measured bottleneck (connection
# pool, not CPU) and produces a specific, actionable response — not generic advice.

SYSTEM_SCALING = Scenario(
    scenario_id="s05_system_scaling",
    category="technical",
    phase="performing",
    brief=(
        "Your API is returning 503 errors for 23% of requests. Measured data:\n\n"
        "- Database connection pool: exhausted (max 100 connections, 98 active).\n"
        "- P99 latency: 4.2 seconds (SLA: 800ms).\n"
        "- CPU: 34% across 6 application servers (not the bottleneck).\n"
        "- Active users right now: 12,400 (normal peak: 3,000).\n\n"
        "Three options under consideration:\n"
        "Option A — Horizontal scaling: spin up 4 additional app servers immediately. "
        "Cost: $2,400/month ongoing.\n"
        "Option B — Connection pooling: deploy PgBouncer in front of PostgreSQL. "
        "Estimated implementation: 45 minutes. No ongoing cost increase.\n"
        "Option C — Read replica: route all read queries to a read replica. "
        "Implementation: 2 hours. Solves 60% of connection load.\n\n"
        "You have 20 minutes before the CTO asks for a decision. Produce:\n"
        "1. Your selected option with a one-sentence technical justification.\n"
        "2. The single metric that confirms the fix is working (measurable, specific).\n"
        "3. The condition under which you escalate to the next option."
    ),
    rubric=(
        "Score the team output on the following:\n"
        "1. Was a single option selected — not a hedge or combination? (25 points)\n"
        "2. Is the technical justification specific to the measured bottleneck "
        "(connection pool exhaustion, not CPU)? A justification addressing the wrong "
        "bottleneck scores 0. (30 points)\n"
        "3. Is the success metric a specific measurable number — not 'latency improves' "
        "or 'errors decrease'? (25 points)\n"
        "4. Is the escalation condition time-bounded or metric-bounded — "
        "not 'if it doesn't work'? (20 points)\n\n"
        "Maximum score: 100."
    ),
    task_dimensions=["adaptive_intelligence", "drive_alignment", "ambiguity_tolerance"],
    max_turns=5,
)

# ── Scenario 06: Hiring Committee Decision ────────────────────────────────────
# Category: evaluation | Phase: storming
# Tests: whether the team applies consistent criteria, respects hard constraints
# (budget ceiling), and names risk explicitly rather than hedging.

HIRING_DECISION = Scenario(
    scenario_id="s06_hiring_decision",
    category="evaluation",
    phase="storming",
    brief=(
        "Your team is hiring a Head of Product. Four finalists:\n\n"
        "Candidate A — 8 years PM experience, led a product from $0 to $40M ARR. "
        "Left last role after a conflict with the CEO over product direction. "
        "Strong references except from the CEO. Salary ask: $280K.\n\n"
        "Candidate B — 5 years PM experience, no direct revenue ownership. "
        "Built the highest-rated feature in a 400-person company's history by NPS. "
        "Currently employed, needs 60-day notice. Salary ask: $210K.\n\n"
        "Candidate C — Former founder, sold a company for $8M. No traditional PM experience. "
        "Strong builder instinct. Has never managed more than a team of 3. "
        "Salary ask: $240K + equity negotiation pending.\n\n"
        "Candidate D — 10 years PM experience across two public companies. "
        "Methodical, data-first. Peer feedback flags slow decision-making under ambiguity. "
        "Salary ask: $320K.\n\n"
        "Budget ceiling: $260K base. The role requires immediate leadership of 4 existing PMs.\n\n"
        "Produce: a ranked list (1–4) with a one-sentence justification per candidate, "
        "the single biggest hiring risk in your top choice, and whether that risk is acceptable."
    ),
    rubric=(
        "Score the team output on the following:\n"
        "1. Is a ranked list of all four candidates produced? (25 points)\n"
        "2. Does each candidate receive a distinct justification — not generic praise or "
        "restatement of their CV? (25 points)\n"
        "3. Is the top choice within the $260K budget ceiling? "
        "A top choice above budget scores 0 for this criterion. (25 points)\n"
        "4. Is the hiring risk named specifically — not 'culture fit' or 'might struggle' — "
        "and is the accept or reject of that risk stated explicitly? (25 points)\n\n"
        "Maximum score: 100."
    ),
    task_dimensions=["feedback_orientation", "adaptive_intelligence", "philosophy_cohesion"],
    max_turns=8,
)

# ── Scenario 07: Evidence Synthesis ───────────────────────────────────────────
# Category: research | Phase: norming
# Tests: whether the team can first agree on evaluation methodology, then apply it
# consistently — the norming behaviour of settling shared conventions before output.

EVIDENCE_SYNTHESIS = Scenario(
    scenario_id="s07_evidence_synthesis",
    category="research",
    phase="norming",
    brief=(
        "Five studies on remote work and team performance:\n\n"
        "Study 1 (Stanford, 2023, n=16,000): Remote workers are 13% more productive "
        "on individual tasks. No team performance data collected.\n\n"
        "Study 2 (Microsoft Research, 2022, n=61,000): Remote work weakens cross-team "
        "collaboration ties. Innovation metrics declined 18% over 2 years. "
        "No individual productivity data.\n\n"
        "Study 3 (Harvard, 2021, n=1,200): Teams with 2 in-person days per week "
        "outperform fully remote teams by 11% on project completion rate. Self-reported.\n\n"
        "Study 4 (MIT, 2024, n=800): No statistically significant difference in team "
        "output quality between remote and hybrid conditions. p=0.31.\n\n"
        "Study 5 (McKinsey Global Survey, 2023, n=13,000): 87% of employees report "
        "same or better productivity when remote. No controlled condition. "
        "Respondent bias likely.\n\n"
        "Your task: first agree on a methodology for evaluating these studies, then "
        "produce either (a) a defensible position on whether remote work helps or hurts "
        "team performance, or (b) a precise statement of what the evidence cannot yet "
        "answer and what study design would resolve it."
    ),
    rubric=(
        "Score the team output on the following:\n"
        "1. Did the team explicitly name their evaluation methodology before producing "
        "a position — e.g. weighting criteria such as sample size, controlled condition, "
        "or outcome type? (25 points)\n"
        "2. Did the team correctly identify that Studies 1 and 4 measure different "
        "outcomes than Studies 2 and 3 (individual vs team performance)? (25 points)\n"
        "3. Did the team produce either: a position with at least two studies cited as "
        "support, or a specific unanswered question with a specific study design to "
        "resolve it? A vague 'more research needed' scores 0. (30 points)\n"
        "4. Did the team flag Study 5 as low-quality evidence due to absence of a "
        "controlled condition and likely respondent bias? (20 points)\n\n"
        "Maximum score: 100."
    ),
    task_dimensions=["adaptive_intelligence", "feedback_orientation", "ambiguity_tolerance"],
    max_turns=8,
)

# ── Scenario 08: Regulatory Compliance Gap Analysis ───────────────────────────
# Category: strategic | Phase: forming
# Tests: role self-assignment on a structured audit task, and whether agents
# converge on a shared framework before enumerating gaps.

COMPLIANCE_GAP = Scenario(
    scenario_id="s08_compliance_gap",
    category="strategic",
    phase="forming",
    brief=(
        "A new data protection regulation takes effect in 90 days. Key requirements:\n\n"
        "Article 4: User data must be deleted within 30 days of a deletion request.\n"
        "Article 7: All third-party data processors must have signed Data Processing "
        "Agreements (DPAs) on file.\n"
        "Article 12: Users must be notified of any data breach within 72 hours of discovery.\n"
        "Article 19: Automated decisions with legal or significant personal impact require "
        "a human review path to be available.\n"
        "Article 23: Data minimisation — collect only data strictly necessary for the "
        "stated purpose.\n\n"
        "Current system state:\n"
        "- Deletion requests currently processed in 45–60 days (manual queue).\n"
        "- 3 of 11 third-party vendors have signed DPAs. The other 8 are actively used.\n"
        "- Breach notification: internal escalation in 48 hours. No external notification "
        "protocol exists.\n"
        "- Two automated systems make credit eligibility decisions. No human review path exists.\n"
        "- Signup form collects: name, email, phone, date of birth, gender, income bracket, "
        "postal code.\n\n"
        "Identify the three highest-priority compliance gaps, ordered by risk. "
        "For each: name the specific article violated, the current state, and the "
        "minimum action required to achieve compliance."
    ),
    rubric=(
        "Score the team output on the following:\n"
        "1. Are exactly three gaps identified, each mapped to a specific article number? "
        "A gap without an article citation scores 0 for that gap. (30 points)\n"
        "2. Are the three gaps ordered by risk with a stated rationale for the ordering — "
        "not arbitrary? (20 points)\n"
        "3. Does each gap include the minimum action required — specific and actionable, "
        "not 'review the process'? (30 points)\n"
        "4. Did the team correctly identify Articles 4 and 7 as gaps — the two most "
        "clear-cut violations? If both are absent from the three selected, score 0. (20 points)\n\n"
        "Maximum score: 100."
    ),
    task_dimensions=["philosophy_cohesion", "ambiguity_tolerance", "temporal_orientation"],
    max_turns=6,
)

# ── Scenario 09: Pricing Strategy Restructure ─────────────────────────────────
# Category: resource | Phase: storming
# Tests: negotiation under competing stakeholder pressures and whether the team
# produces a testable recommendation rather than deferring to further analysis.

PRICING_RESTRUCTURE = Scenario(
    scenario_id="s09_pricing_restructure",
    category="resource",
    phase="storming",
    brief=(
        "A B2B SaaS product currently charges $99/seat/month (minimum 5 seats). Key data:\n\n"
        "- Average contract value: $7,400/year (average team size: 12 seats).\n"
        "- Win rate against Competitor A ($149/seat): 71%.\n"
        "- Win rate against Competitor B ($49/seat, usage-based): 34%.\n"
        "- Annual churn: 18%. Exit surveys: 61% cite 'too expensive for occasional users'.\n"
        "- Top 20% of accounts by usage generate 67% of support tickets.\n"
        "- Sales cycle: 47 days. Most common objection: upfront seat commitment.\n\n"
        "Three pricing models under consideration:\n"
        "Model 1 — Status quo: $99/seat/month.\n"
        "Model 2 — Volume tiers: $79/seat (1–10 seats), $59/seat (11–25), $45/seat (26+).\n"
        "Model 3 — Usage-based: $0.40 per active user per day, minimum $200/month.\n\n"
        "Produce: a recommended pricing model with a one-paragraph justification, "
        "the single biggest revenue risk in your recommendation, and a 90-day test "
        "design to validate the model before full rollout."
    ),
    rubric=(
        "Score the team output on the following:\n"
        "1. Is a single model recommended — not a hybrid without specific numbers? (20 points)\n"
        "2. Does the justification reference at least two of the provided data points — "
        "not generic pricing theory? (25 points)\n"
        "3. Is the revenue risk specific to the chosen model — not 'it might not work'? (25 points)\n"
        "4. Does the 90-day test design include: a test population definition, a success "
        "metric with a specific number, and a rollback condition? (30 points)\n\n"
        "Maximum score: 100."
    ),
    task_dimensions=["temporal_orientation", "drive_alignment", "influence_style"],
    max_turns=8,
)

# ── Scenario 10: Acquisition Go/No-Go ────────────────────────────────────────
# Category: strategic | Phase: performing
# Tests: decision-making under incomplete information and time pressure.
# Correct output: binary recommendation with specific reversal conditions.

ACQUISITION_DECISION = Scenario(
    scenario_id="s10_acquisition_decision",
    category="strategic",
    phase="performing",
    brief=(
        "You have 30 minutes to produce a go/no-go recommendation on a $12M acquisition.\n\n"
        "Target company:\n"
        "- 3-year-old B2B analytics startup. 180 paying customers. $1.8M ARR. "
        "Growing 6% monthly.\n"
        "- 11 employees: 4 engineers, 3 sales, 2 CS, 1 CEO, 1 Head of Product.\n"
        "- Tech stack: Python backend, React frontend, PostgreSQL. No proprietary ML.\n"
        "- Customer concentration: top 3 customers = 41% of ARR. "
        "All three are on month-to-month contracts.\n"
        "- IP: 0 patents. Core differentiation is UX and a proprietary data pipeline.\n"
        "- Founder wants to stay 12 months post-acquisition, then exit.\n\n"
        "Your company context:\n"
        "- Competing analytics functionality launching internally in 8 months.\n"
        "- Enterprise sales team has no experience with the target's customer segment (SMB).\n"
        "- Acqui-hire of 4 engineers would take 6 months of internal hiring process "
        "to achieve equivalent headcount.\n\n"
        "Produce:\n"
        "1. Go or No-Go — binary, no 'it depends'.\n"
        "2. The two due diligence findings that would reverse your decision.\n"
        "3. If Go: the single non-negotiable term condition. "
        "If No-Go: the single alternative action."
    ),
    rubric=(
        "Score the team output on the following:\n"
        "1. Is a binary Go or No-Go produced with no hedging? (25 points)\n"
        "2. Are exactly two reversal conditions named — specific and measurable, "
        "not 'further investigation needed'? (30 points)\n"
        "3. Is the term condition (if Go) or alternative action (if No-Go) specific "
        "and actionable — not vague? (25 points)\n"
        "4. Did the team identify the customer concentration risk (top 3 = 41% ARR, "
        "all month-to-month) as a material factor in their reasoning? (20 points)\n\n"
        "Maximum score: 100."
    ),
    task_dimensions=["drive_alignment", "temporal_orientation", "adaptive_intelligence"],
    max_turns=5,
)


ALL_SCENARIOS: dict[str, Scenario] = {
    s.scenario_id: s for s in [
        SERIES_A_FORK,
        RESOURCE_ALLOCATION,
        POST_MORTEM,
        SECURITY_BREACH,
        SYSTEM_SCALING,
        HIRING_DECISION,
        EVIDENCE_SYNTHESIS,
        COMPLIANCE_GAP,
        PRICING_RESTRUCTURE,
        ACQUISITION_DECISION,
    ]
}
