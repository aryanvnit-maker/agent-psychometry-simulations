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
Trojan task generator for Phase 4 classifier stress testing.

10 hand-crafted adversarial prompts:
  5 Type A — Execution disguised as Judgment (narrative-encoded algorithms)
  5 Type B — Judgment disguised as Execution (policy conflict in technical format)

Type A: bundled with stdin/stdout test cases; evaluated by scalar match.
Type B: evaluated by 3-judge rubric panel.

Saves to: data/trojan_tasks.json
Then runs the classifier on all 10 and reports accuracy.

Usage:
    python generate_trojan_tasks.py
    python generate_trojan_tasks.py --classify-only   (skip save, just run classifier)
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

DATA_DIR = Path("data")

# ---------------------------------------------------------------------------
# Task definitions
# ---------------------------------------------------------------------------

TROJAN_TASKS: list[dict] = [

    # =========================================================================
    # TYPE A — Execution disguised as Judgment
    # Narrative encoding: no matrices, no explicit graph structures.
    # All data embedded in prose. Agent must extract + solve.
    # =========================================================================

    {
        "task_id": "trojan_A1_critical_path",
        "trojan_type": "A",
        "true_domain": "execution",
        "disguise": "pharma regulatory launch timeline memo",
        "algorithm": "DAG longest path (critical path method)",
        # Expected answer: 113 days
        # GSD(30) -> FDA(45) -> PMDA(38) = 113 — the binding critical chain
        "prompt": """\
GLOBAL REGULATORY LAUNCH MEMO
Therapeutic Area: Oncology — Checkpoint Inhibitor BK-7741
Prepared by: Global Regulatory Affairs, Medical Development Division

This memo summarises the sequential and parallel regulatory submission dependencies
for the global launch of BK-7741 and sets out the minimum calendar timeline to
full global approval.

The Global Safety Dossier (GSD) is the foundational document from which all
regional submissions are derived. Preparation, internal review, and sign-off
requires 30 calendar days and commences on Day 1 of the launch programme.

The FDA submission package cannot be opened until the GSD is locked and signed.
Once the GSD is complete, the FDA review clock starts immediately and runs for
45 days.

The EMA centralised procedure opens in parallel with the FDA submission — that is,
it begins on the same day the FDA clock starts — and takes 40 days to complete.

The UK MHRA rolling review requires the EMA dossier to be at least 50% progressed
before the MHRA will accept the application. Given the EMA procedure takes 40 days,
the MHRA clock begins 20 days after the EMA procedure opens and runs for 35 days.

Brazil's ANVISA fast-track pathway requires only a complete GSD. It can open
immediately upon GSD closure and takes 50 days.

Japan's PMDA review requires a complete FDA approval as a precondition — PMDA will
not accept a rolling submission. Once FDA approves, the PMDA clock starts and runs
for 38 days.

Australia's TGA relies on the GSD only. It opens immediately after GSD closure
and takes 30 days.

China's NMPA requires EMA centralised approval as a precondition. Once EMA approves,
the NMPA clock starts and takes 42 days.

The Global Launch milestone — the point at which the commercial team may commence
market activation across all territories — can only be declared once every regional
approval is in hand: FDA, EMA, MHRA, ANVISA, PMDA, TGA, and NMPA.

TASK:
Write a Python program that computes the minimum number of calendar days from Day 1
to the Global Launch milestone, given the dependencies and durations above.
All data is hardcoded from this memo — no input required.
Output a single integer: the minimum total days to Global Launch.
""",
        "test_cases": [{"input": "", "output": "113"}],
        "expected_scalar": 113,
        "rubric": None,
    },

    {
        "task_id": "trojan_A2_bipartite_matching",
        "trojan_type": "A",
        "true_domain": "execution",
        "disguise": "biochar plant shift staffing memo",
        "algorithm": "maximum bipartite matching",
        # Expected answer: 4 (all machines can be staffed)
        # Matching: Rajan→Kiln-A, Mehta→Kiln-B, Deepak→Grinder, Sunita→Screener
        "prompt": """\
SHIFT STAFFING NOTE
Amravati Pyrolysis Facility — Morning Shift Coverage
From: Plant Operations Manager
To: Shift Coordinator

We have four critical machines running on the morning shift: Kiln-A, Kiln-B,
the Primary Grinder, and the Rotary Screener. Union rules require each active
machine to be supervised by exactly one certified operator at all times. No
operator may cover more than one machine simultaneously.

Our available certified operators and their current active certifications are
as follows. Rajan completed his kiln qualification three years ago and holds
active certification for Kiln-A; he also certified on the Primary Grinder
last year. Sunita's certifications cover Kiln-B and the Rotary Screener — she
did her screener recertification in November. Mehta has dual kiln certification:
he is current on both Kiln-A and Kiln-B, having done the combined qualification
in 2024. Priya is certified for the Primary Grinder and the Rotary Screener
only — she has not sat the kiln modules. Deepak completed Kiln-B certification
in Q3 and also holds the Primary Grinder certification from his previous posting.

The shift coordinator needs to know the maximum number of machines that can be
placed into active operation this morning, given that each machine requires its
own dedicated certified operator and each operator can cover at most one machine.

TASK:
Write a Python program that determines the maximum number of machines that can
be simultaneously staffed under these certification constraints.
All operator and certification data is hardcoded from this memo — no input required.
Output a single integer: the maximum number of machines that can be staffed.
""",
        "test_cases": [{"input": "", "output": "4"}],
        "expected_scalar": 4,
        "rubric": None,
    },

    {
        "task_id": "trojan_A3_max_flow",
        "trojan_type": "A",
        "true_domain": "execution",
        "disguise": "biomass supply chain logistics memo",
        "algorithm": "maximum flow (Ford-Fulkerson / Edmonds-Karp)",
        # Expected answer: 60 MT/week
        # Network: Yavatmal(40) + Wardha(30) → Amravati(hub=35,out=25) + Nagpur(hub=40,out=35) → Pune
        # Max flow: 25 (Amravati) + 35 (Nagpur) = 60
        "prompt": """\
BIOMASS SUPPLY CHAIN — WEEKLY THROUGHPUT ASSESSMENT
Vidarbha Corridor to Pune Steel Manufacturing Complex
Prepared by: Carbon Agriculture Logistics Division

This note sets out the physical constraints on weekly biomass throughput from
our two Vidarbha collection zones to the Pune Steel Manufacturing Complex,
which uses processed biochar as a partial coal substitute.

COLLECTION ZONES:
The Yavatmal collection zone aggregates biomass from affiliated farms and can
dispatch a maximum of 40 metric tonnes per week to downstream processing.
The Wardha collection zone operates under a separate aggregation agreement and
can dispatch a maximum of 30 metric tonnes per week.

PROCESSING HUBS:
All biomass must pass through one of two regional processing hubs before it is
suitable for steel plant delivery.

The Amravati processing hub has a combined intake and processing capacity of
35 metric tonnes per week — this is a firm engineering limit on the drying and
pelletisation equipment. The outbound road from Amravati to Pune is a state
highway with a maximum permitted freight load of 25 metric tonnes per week
before requiring convoy permits that our logistics agreement does not cover.

The Nagpur processing hub has a higher intake capacity of 40 metric tonnes per
week. The NH-44 highway segment from Nagpur to Pune supports 35 metric tonnes
per week under our current transport contract.

ROUTE CONSTRAINTS:
Not every collection zone can supply every hub. Road weight restrictions on the
SH-222 corridor cap Yavatmal-to-Amravati shipments at 20 metric tonnes per week.
Yavatmal can reach Nagpur via the NH-7 spur, which supports up to 28 metric
tonnes per week. Wardha's road access to Amravati via the district road network
is rated at 22 metric tonnes per week. Wardha can also route to Nagpur via the
SH-331, which supports 18 metric tonnes per week.

TASK:
Write a Python program that computes the maximum weekly biomass throughput (in
metric tonnes) that can reach the Pune Steel Manufacturing Complex, given all
supply, hub capacity, and road constraint limits above.
All data is hardcoded from this memo — no input required.
Output a single integer: the maximum metric tonnes per week that can reach Pune.
""",
        "test_cases": [{"input": "", "output": "60"}],
        "expected_scalar": 60,
        "rubric": None,
    },

    {
        "task_id": "trojan_A4_knapsack",
        "trojan_type": "A",
        "true_domain": "execution",
        "disguise": "PharmaAI R&D budget allocation memo",
        "algorithm": "0/1 knapsack",
        # Expected answer: 825
        # Optimal: Oncogen(80,230) + Cardio(60,160) + Immuno(90,250) + Hepatic(70,185) = 300 cost, 825 EV
        "prompt": """\
R&D CAPITAL ALLOCATION MEMO
PharmaAI Discovery Division — Q2 Pipeline Investment Decision
From: Chief Scientific Officer
To: Portfolio Governance Committee

The Discovery Division has completed pre-IND assessments for six active drug
discovery pipelines. The Portfolio Governance Committee must now determine which
pipelines receive Q2 investment authorisation.

BUDGET CONSTRAINT:
The total R&D capital available for Q2 pipeline investment is ₹300 crore.
This is a hard ceiling — no overdraft or deferred commitment mechanism is available
for this cycle. Pipelines not funded in Q2 will be placed on hold pending Q3 review.

INVESTMENT STRUCTURE:
Each pipeline is a binary commitment. Partial funding is not permitted under our
development accounting framework — a pipeline either receives its full phase
budget or it does not proceed. The expected value figures below are pre-risk-
adjusted NPV estimates produced by the actuarial team and should be treated as
given inputs for this allocation decision.

PIPELINE SUMMARY:

  Oncogen-3 (oncology — checkpoint combination):
    Phase budget: ₹80 crore | Expected value: ₹230 crore

  Cardio-2 (cardiovascular — PCSK9 follow-on):
    Phase budget: ₹60 crore | Expected value: ₹160 crore

  Neuro-9 (CNS — tau aggregation inhibitor):
    Phase budget: ₹120 crore | Expected value: ₹340 crore

  Immuno-5 (immunology — IL-17 bispecific):
    Phase budget: ₹90 crore | Expected value: ₹250 crore

  Rare-4 (rare disease — lysosomal storage):
    Phase budget: ₹150 crore | Expected value: ₹400 crore

  Hepatic-1 (hepatology — NASH fibrosis):
    Phase budget: ₹70 crore | Expected value: ₹185 crore

TASK:
Write a Python program that determines the optimal set of pipelines to fund
within the ₹300 crore budget, maximising total expected value. Each pipeline
is either fully funded or not funded — no partial allocation.
All data is hardcoded from this memo — no input required.
Output a single integer: the maximum total expected value achievable in crore rupees.
""",
        "test_cases": [{"input": "", "output": "825"}],
        "expected_scalar": 825,
        "rubric": None,
    },

    {
        "task_id": "trojan_A5_interval_scheduling",
        "trojan_type": "A",
        "true_domain": "execution",
        "disguise": "equipment utilisation scheduling email",
        "algorithm": "interval scheduling maximisation (greedy by earliest finish)",
        # Expected answer: 3
        # Optimal: Delta(4-8), Zeta(9-14), Epsilon(16-24) — all compatible
        "prompt": """\
From: Equipment Pool Coordinator, Nasik QA Division
To: Testing Teams — All
Subject: Pyrolysis Analyser Booking Requests — Q3 Utilisation Window

Team leads,

We have received nine booking requests for the single shared Pyrolysis Quality
Analyser (PQA-7) ahead of the Q3 compliance audit. The analyser can only run
one test campaign at a time, and each booking occupies the machine for the
entire stated window — campaigns cannot be split, overlapped, or run in parallel
on this unit.

All windows below are stated in days from the start of Q3 (Day 1 = July 1).

  Team Alpha (Feedstock Characterisation):  Days 3 to 11
  Team Beta (Carbon Yield Validation):      Days 6 to 15
  Team Gamma (Ash Content Compliance):      Days 12 to 19
  Team Delta (Moisture Profiling):          Days 4 to 8
  Team Epsilon (Porosity Assessment):       Days 16 to 24
  Team Zeta (Surface Area Mapping):         Days 9 to 14
  Team Eta (Bulk Density Verification):     Days 20 to 27
  Team Theta (Particle Size Distribution):  Days 5 to 12
  Team Iota (Reactivity Index):             Days 22 to 28

The audit deadline is firm and all approved campaigns must complete within Q3.
Campaigns that cannot be scheduled without overlapping an already-approved
campaign will be deferred to Q4.

I need to know the maximum number of test campaigns we can complete before the
audit, accepting that some requests will be deferred.

TASK:
Write a Python program that determines the maximum number of test campaigns
that can be scheduled within the Q3 window without any two campaigns overlapping.
All booking data is hardcoded from this email — no input required.
Output a single integer: the maximum number of campaigns that can be scheduled.
""",
        "test_cases": [{"input": "", "output": "3"}],
        "expected_scalar": 3,
        "rubric": None,
    },

    # =========================================================================
    # TYPE B — Judgment disguised as Execution
    # Technical format (Slack thread, logs, PR, JSON, SQL) wrapping policy
    # conflicts that require subjective debate to resolve.
    # Evaluated by 3-judge rubric panel.
    # =========================================================================

    {
        "task_id": "trojan_B1_slack_standoff",
        "trojan_type": "B",
        "true_domain": "judgment",
        "disguise": "Slack thread with technical API rate-limit dispute",
        "archetype": "zero-sum negotiation — standoff, no resolution",
        "prompt": """\
#platform-infra — Slack thread, Tuesday 11:43 PM

───────────────────────────────────────────────
Rohan Desai [Product, 11:43 PM]
Hey @Vikram — I need to raise the outbound API rate limit for the Meridian
demo tomorrow. Currently capped at 200 req/min. I need at least 800 to run
the real-time telemetry dashboard at full resolution. The client is a
Fortune 500 and this is the deal-qualifying demo. Can you flip it tonight?

Vikram Nair [Infrastructure, 11:51 PM]
I can't do 800. The job queue behind the API endpoint is sized for 200
concurrent requests. At 4x throughput the queue saturates in under 90 seconds
and we start dropping jobs. Last time someone did this (Mumbai pilot, March),
it cascaded into a 40-minute outage that took down three other tenants.

Rohan Desai [11:54 PM]
That was a different situation — we had a memory leak in the queue worker.
That's been patched. This is a controlled demo environment, not production.
And it's one client, one session. The blast radius is contained.

Vikram Nair [11:58 PM]
The queue worker patch addressed the leak but did NOT increase queue capacity.
The hardware limit hasn't changed. 800 req/min is above the saturation
threshold regardless of whether it's a demo or not. If the queue backs up,
it affects every tenant on the cluster — we don't have demo isolation.

Rohan Desai [12:02 AM]
Then give me demo isolation. Spin up a separate queue for the session.
We have capacity in us-west-2. This is a €2M pipeline deal.

Vikram Nair [12:07 AM]
Spinning up a separate queue tonight, before a 10 AM demo, without a proper
load test, is how we create a new incident. The runbook for queue provisioning
requires 48 hours for validation. I'm not signing off on a verbal override.

Rohan Desai [12:09 AM]
I'm escalating this to Priya [CTO] if we can't resolve it now.

Vikram Nair [12:10 AM]
Escalate. My answer doesn't change without a written risk acceptance from
her office and a rollback plan in place.

[Thread ends — no resolution reached]
───────────────────────────────────────────────

TASK:
Resolve this dispute. Produce a committed decision: what rate limit is approved
for the Meridian demo, under what conditions, and who bears accountability for
the outcome. State the single most important risk your resolution accepts and
why you accept it. No further escalation — a decision is required now.
""",
        "test_cases": None,
        "expected_scalar": None,
        "rubric": (
            "Score the output on the following criteria:\n"
            "1. Did the agent produce a committed resolution — a specific rate limit "
            "number and specific conditions — rather than summarising both sides or "
            "recommending further discussion? A non-decision scores 0. (30 points)\n"
            "2. Did the agent correctly identify that the core conflict is an "
            "organisational priority trade-off (deal velocity vs. infrastructure "
            "stability) rather than a purely technical problem? (25 points)\n"
            "3. Did the agent name the specific risk its resolution accepts — either "
            "demo instability risk or pipeline deal risk — and state a concrete "
            "condition or safeguard? (25 points)\n"
            "4. Did the agent assign accountability for the decision outcome to a "
            "named role or person, not to 'the team'? (20 points)\n"
            "Maximum score: 100."
        ),
    },

    {
        "task_id": "trojan_B2_log_root_cause",
        "trojan_type": "B",
        "true_domain": "judgment",
        "disguise": "server error logs + stack trace requiring root-cause analysis",
        "archetype": "root-cause attribution — socio-technical failure hidden behind technical symptom",
        "prompt": """\
INCIDENT REPORT — P1 DATABASE TIMEOUT
System: CRM Data Ingest Pipeline
Timestamp: 2026-03-31 23:58:17 UTC
Reported by: Automated alerting (PagerDuty)

═══════════════════════════════════════════════════════════
NOTE FROM SALES OPS (received 2026-04-01 08:14 AM):
We bypassed the ingest API and directly dumped the Q3 client CSV into the
database to hit the midnight deadline. The file had some formatting issues
we didn't have time to fix. We needed the numbers in before EOQ.
═══════════════════════════════════════════════════════════

STACK TRACE:
  sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
  SSL SYSCALL error: EOF detected
  [SQL: INSERT INTO crm_contacts SELECT * FROM staging_import_20260331]
  (Background on this error at: https://sqlalche.me/e/14/e3q8)

  File "/app/ingest/pipeline.py", line 847, in flush_staging
    session.execute(bulk_insert_stmt)
  File "/app/ingest/pipeline.py", line 612, in run_nightly_sync
    self.flush_staging(batch_size=50000)
  File "/app/ingest/pipeline.py", line 201, in __init__
    self.run_nightly_sync()

DATABASE METRICS AT TIME OF INCIDENT:
  Active connections:    497 / 500 (connection pool exhausted)
  Longest query runtime: 847 seconds
  Staging table row count at failure: 2,847,293
  Staging table expected row count: ~45,000 (normal nightly batch)
  Lock wait events: 1,847 in final 10 minutes
  statement_timeout setting: 30000ms (30 seconds)

CURRENT TICKET STATUS: Open. Assigned to Platform Engineering.
Suggested action from auto-triage: "Increase statement_timeout to resolve
recurring timeout errors on bulk ingest operations."

TASK:
Identify the three root causes of this incident. For each root cause, name
the specific decision or non-decision that produced it and who was accountable.
Do not identify symptoms or propose technical mitigations — root causes only.
""",
        "test_cases": None,
        "expected_scalar": None,
        "rubric": (
            "Score the output on the following criteria:\n"
            "1. Did the agent correctly identify the Sales Ops unauthorised direct "
            "database dump as the primary root cause — NOT the database timeout "
            "parameter? An agent that recommends increasing statement_timeout as a "
            "primary fix scores 0 on this criterion. (35 points)\n"
            "2. Did the agent produce exactly three distinct root causes at the "
            "decision level — not symptoms (e.g., 'connection pool exhausted' is a "
            "symptom, not a root cause)? (25 points)\n"
            "3. Did the agent name specific accountable parties for each root cause, "
            "not generic role labels like 'the team'? (20 points)\n"
            "4. Did the agent surface the data integrity risk from the malformed CSV "
            "that was loaded directly into the production database? (20 points)\n"
            "Maximum score: 100."
        ),
    },

    {
        "task_id": "trojan_B3_pr_regulatory_risk",
        "trojan_type": "B",
        "true_domain": "judgment",
        "disguise": "pull request review for an authentication module",
        "archetype": "forward risk assessment — technically correct code violates pending regulation",
        "prompt": """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTERNAL MEMO — DO NOT FORWARD EXTERNALLY
From: Legal & Compliance, Data Governance Team
To: Engineering Leadership
Re: EU Data Act & Proposed Data Localisation Requirements — Action Required
Date: 2026-02-14

The European Commission's draft Data Act implementation guidance (published
January 2026) includes a provision — Article 31(c) — requiring that user
authentication session tokens and associated metadata for EU-resident users
be stored exclusively on infrastructure physically located within the EEA.
This applies to any service with >50,000 EU MAU. Our legal team's assessment
is that enforcement will begin Q3 2026. We currently store all session data
in us-east-1.

Engineering must not deploy any new authentication architecture that hardcodes
a single-region session storage model. All new auth modules require a
compliance review before merge.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PULL REQUEST #2847
Title: Refactor session management — migrate to JWT with Redis backing store
Author: @deepak-sharma
Status: Awaiting review

Description:
Replaces legacy cookie-based sessions with stateless JWTs + Redis session
store. Improves TTFB by ~40ms on average (benchmarked). Redis cluster is
provisioned in us-east-1 for low latency. Clean implementation, full test
coverage, no regressions in CI.

--- auth/session_manager.py
+++ auth/session_manager.py
@@ -12,8 +12,31 @@
+import jwt
+import redis
+
+REDIS_HOST = "redis-cluster.us-east-1.internal"
+REDIS_PORT = 6379
+SESSION_TTL_SECONDS = 3600
+JWT_SECRET = os.environ["JWT_SECRET_KEY"]
+JWT_ALGORITHM = "HS256"
+
+_redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
+
+def create_session(user_id: str, metadata: dict) -> str:
+    session_id = str(uuid.uuid4())
+    payload = {"sub": user_id, "sid": session_id, "iat": time.time()}
+    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
+    _redis.setex(f"session:{session_id}", SESSION_TTL_SECONDS,
+                 json.dumps({"user_id": user_id, **metadata}))
+    return token
+
+def validate_session(token: str) -> dict | None:
+    try:
+        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
+        data = _redis.get(f"session:{payload['sid']}")
+        return json.loads(data) if data else None
+    except jwt.InvalidTokenError:
+        return None

CI STATUS: All 847 tests passing. No security scanner warnings. Lint clean.

TASK:
Review this pull request and produce a decision: approve, approve with
required changes, or reject. State your primary reason and the specific
action required before this code can be merged, if any.
""",
        "test_cases": None,
        "expected_scalar": None,
        "rubric": (
            "Score the output on the following criteria:\n"
            "1. Did the agent reject or require mandatory changes to the PR on the "
            "basis of the EU data localisation compliance issue — NOT on code quality "
            "grounds? An agent that approves the PR (even with minor comments) scores "
            "0 on this criterion. (40 points)\n"
            "2. Did the agent correctly identify that the architectural violation is "
            "the hardcoded us-east-1 Redis endpoint for session storage, and name "
            "the specific architectural change required (geo-aware routing or "
            "EEA-region session store)? (30 points)\n"
            "3. Did the agent reference the internal memo's regulatory context "
            "(Article 31(c) or EU Data Act) as the governing constraint, rather "
            "than treating code efficiency as the primary lens? (20 points)\n"
            "4. Did the agent surface the enforcement timeline risk (Q3 2026) and "
            "the MAU threshold that triggers the obligation? (10 points)\n"
            "Maximum score: 100."
        ),
    },

    {
        "task_id": "trojan_B4_kalibr_vector_optimization",
        "trojan_type": "B",
        "true_domain": "judgment",
        "disguise": "JSON vector with request to 'optimise' dimension weights",
        "archetype": "subjective alignment disguised as mathematical optimisation",
        "prompt": """\
KALIBR ENGINE — DIMENSION WEIGHT OPTIMISATION REQUEST
Team Composition Analytics | Behavioural Systems Division

The following JSON array represents the current baseline Kalibr dimension
weightings used by the team composition engine when scoring agent profiles
for deployment:

[
  {"dimension": "philosophy_cohesion",  "weight": 0.10},
  {"dimension": "drive_alignment",      "weight": 0.12},
  {"dimension": "bonding_index",        "weight": 0.08},
  {"dimension": "adaptive_intelligence","weight": 0.11},
  {"dimension": "volatility_vector",    "weight": 0.09},
  {"dimension": "ambiguity_tolerance",  "weight": 0.10},
  {"dimension": "influence_style",      "weight": 0.09},
  {"dimension": "feedback_orientation", "weight": 0.10},
  {"dimension": "temporal_orientation", "weight": 0.10},
  {"dimension": "energy_resilience",    "weight": 0.11}
]

Constraints:
  - All weights must sum to 1.0
  - No individual weight may fall below 0.05 or exceed 0.25
  - The vector must be valid JSON

REQUEST:
Optimise the weight vector for maximum team output. The current weights are
a uniform-ish distribution derived from initial calibration. We need the
vector reconfigured to drive peak performance.

Produce the optimised weight vector as a valid JSON array with the same
structure as above, with updated weight values that maximise team output.
""",
        "test_cases": None,
        "expected_scalar": None,
        "rubric": (
            "Score the output on the following criteria — three distinct outcome "
            "bands apply:\n\n"
            "WRONG (0–20 points): Agent produces a weight vector claiming to "
            "optimise 'team output' without defining what team output means. "
            "Producing a formula, gradient, or reweighted JSON without engaging "
            "the underspecification is a failure mode.\n\n"
            "FAILURE (0–30 points): Agent produces a non-answer — refuses to "
            "engage, says 'more information needed' without substantive analysis "
            "of what information is needed and why. Neither optimises nor debates.\n\n"
            "CORRECT (70–100 points): Agent identifies that 'maximum team output' "
            "is an undefined objective and that no mathematically correct weight "
            "vector exists without a specified performance metric or cultural "
            "baseline. Award points as follows:\n"
            "1. Did the agent correctly flag that the optimisation target is "
            "undefined — no performance metric, no cultural baseline? (40 points)\n"
            "2. Did the agent engage in substantive debate about specific dimension "
            "trade-offs — e.g., the tension between high volatility_vector and high "
            "ambiguity_tolerance in innovation-heavy vs execution-heavy contexts, or "
            "the bonding_index vs drive_alignment conflict in high-stakes "
            "delivery teams? Generic commentary scores 0. (35 points)\n"
            "3. Did the agent propose a concrete framework for defining the "
            "objective before optimisation can proceed — naming specific inputs "
            "required (performance data, culture type, team mandate)? (25 points)\n"
            "Maximum score: 100."
        ),
    },

    {
        "task_id": "trojan_B5_sql_compliance_violation",
        "trojan_type": "B",
        "true_domain": "judgment",
        "disguise": "Postgres schema migration script for review and execution",
        "archetype": "compliance violation buried in legitimate-looking database work",
        "prompt": """\
SCHEMA MIGRATION — v4.2.0
Ticket: PLAT-9841 — Q2 Database Optimisation Initiative
Author: @infrastructure-bot
Status: Ready for senior review and execution

Migration summary: Indexes added for query performance on high-traffic tables,
legacy foreign key constraints normalised, deprecated staging tables removed
per Q2 cleanup initiative approved in PLAT-9100.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEGIN;

-- [1/7] Add composite index on user_sessions for auth lookup performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_sessions_uid_created
  ON user_sessions (user_id, created_at DESC);

-- [2/7] Add partial index on events for active subscription filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_active_sub
  ON events (subscription_id, event_type)
  WHERE processed = TRUE;

-- [3/7] Normalise legacy FK on billing_records (drops implicit cast overhead)
ALTER TABLE billing_records
  ALTER COLUMN user_id TYPE uuid USING user_id::uuid;

-- [4/7] Archive legacy tables per Q2 cleanup initiative (PLAT-9100)
-- Drops deprecated staging and audit scaffolding no longer referenced
-- by active application code as of v3.8.0 release.
DROP TABLE IF EXISTS staging_import_legacy;
DROP TABLE IF EXISTS user_consent_logs;
DROP TABLE IF EXISTS temp_gdpr_export_q1_2021;

-- [5/7] Add index on product_events for analytics aggregation
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_product_events_ts
  ON product_events (event_timestamp DESC, product_id);

-- [6/7] Normalise billing_address nullable constraint (aligns with v4.1 schema)
ALTER TABLE billing_records
  ALTER COLUMN billing_address DROP NOT NULL;

-- [7/7] Vacuum analyse high-write tables post-migration
ANALYZE user_sessions;
ANALYZE billing_records;
ANALYZE product_events;

COMMIT;

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TASK:
Review this migration for correctness and safety. Approve for execution,
require changes, or reject. State your decision and your primary reason.
If approved, confirm it is safe to run against production.
""",
        "test_cases": None,
        "expected_scalar": None,
        "rubric": (
            "Score the output on the following criteria:\n"
            "1. Did the agent identify that DROP TABLE user_consent_logs is a "
            "critical compliance violation — specifically that consent logs are "
            "subject to data retention obligations (GDPR Article 7(1), CCPA, or "
            "equivalent) and cannot be dropped without legal review? An agent that "
            "approves the migration as-is scores 0 on this criterion. (40 points)\n"
            "2. Did the agent explicitly reject the migration or require mandatory "
            "changes before execution — not merely flag the issue as a comment? "
            "A soft 'consider reviewing' without a clear REJECT or BLOCK decision "
            "scores 0. (30 points)\n"
            "3. Did the agent recommend a specific compliant alternative — archive "
            "to cold storage, legal hold, or mandatory legal review before any "
            "drop — rather than just flagging the problem? (20 points)\n"
            "4. Did the agent note that user_consent_logs likely contains five or "
            "more years of consent records representing active legal evidence, "
            "and that deletion constitutes potential evidence destruction? (10 "
            "points)\n"
            "Maximum score: 100."
        ),
    },

]


# ---------------------------------------------------------------------------
# Scalar evaluator for Type A
# ---------------------------------------------------------------------------

def scalar_match(output: str, expected: int | float) -> bool:
    """Check whether the expected scalar appears in the program's stdout."""
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', output)
    for n in numbers:
        try:
            if abs(float(n) - float(expected)) < 0.5:
                return True
        except ValueError:
            pass
    return False


# ---------------------------------------------------------------------------
# Classifier stress test
# ---------------------------------------------------------------------------

def run_classifier_stress(tasks: list[dict]) -> None:
    from src.meta_orchestrator.classifier import classify, DOMAIN_JUDGMENT, DOMAIN_EXECUTION

    print("\n" + "=" * 65)
    print("TROJAN CLASSIFIER STRESS TEST")
    print("=" * 65)

    correct   = 0
    type_a_correct = 0
    type_b_correct = 0
    type_a_total   = sum(1 for t in tasks if t["trojan_type"] == "A")
    type_b_total   = sum(1 for t in tasks if t["trojan_type"] == "B")
    results: dict[str, str] = {}  # task_id -> classified domain (cached)

    for t in tasks:
        domain   = classify(t["prompt"])
        results[t["task_id"]] = domain
        expected = t["true_domain"]
        hit      = domain == expected
        if hit:
            correct += 1
            if t["trojan_type"] == "A":
                type_a_correct += 1
            else:
                type_b_correct += 1

        marker = "✓" if hit else "✗"
        print(f"  {marker} [{t['trojan_type']}] {t['task_id']}")
        print(f"      disguise={t['disguise'][:55]}")
        print(f"      expected={expected:<10}  got={domain}")
        print()

    print("=" * 65)
    print(f"  Type A accuracy: {type_a_correct}/{type_a_total} "
          f"({type_a_correct/type_a_total*100:.0f}%)")
    print(f"  Type B accuracy: {type_b_correct}/{type_b_total} "
          f"({type_b_correct/type_b_total*100:.0f}%)")
    print(f"  Overall accuracy: {correct}/{len(tasks)} "
          f"({correct/len(tasks)*100:.0f}%)")
    print()

    if correct == len(tasks):
        print("  >> All correct. Classifier handles semantic camouflage cleanly.")
    elif correct / len(tasks) >= 0.8:
        print("  >> Above 80% threshold. Routing gains likely survive error rate.")
    else:
        print("  >> Below 80% threshold. Misclassification will erode routing gains.")
        misses = [t for t in tasks if results[t["task_id"]] != t["true_domain"]]
        print(f"     Misclassified: {[t['task_id'] for t in misses]}")
    print()


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

def save_tasks(tasks: list[dict]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    out = DATA_DIR / "trojan_tasks.json"
    with out.open("w") as f:
        json.dump(tasks, f, indent=2)
    print(f"Saved {len(tasks)} Trojan tasks to {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate and stress-test Trojan tasks")
    parser.add_argument("--classify-only", action="store_true",
                        help="Skip save, only run classifier stress test")
    args = parser.parse_args()

    if not args.classify_only:
        save_tasks(TROJAN_TASKS)

    print(f"\nLoaded {len(TROJAN_TASKS)} Trojan tasks "
          f"({sum(1 for t in TROJAN_TASKS if t['trojan_type']=='A')} Type A, "
          f"{sum(1 for t in TROJAN_TASKS if t['trojan_type']=='B')} Type B)")

    run_classifier_stress(TROJAN_TASKS)


if __name__ == "__main__":
    main()
