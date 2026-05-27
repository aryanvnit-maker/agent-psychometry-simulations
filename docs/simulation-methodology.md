# Simulation Methodology

Framework for replicating validated human team research in an AI agent environment to generate novel cohesion and composition correlations.

---

## Theoretical Underpinning — Why the Simulation Produces Valid Data

The primary objection to agent-based psychometric research is: "LLMs are probabilistic token predictors — you're just measuring randomness, not cognition."

This objection is valid for unconstrained models. It does not apply here. Three mechanisms make the simulation defensible:

**1. Probability Space Collapse**
An unconstrained LLM asked to evaluate a plan will assign high probability to sycophantic tokens ("Great idea!", "I agree") because its base training optimises for affirmation. When you inject a restrictive KalibrIQ Constitution — one that explicitly forbids affirmative openers and mandates challenging the weakest assumption — you mathematically re-weight the token probability distribution. The probability of the model generating "Great idea" drops to effectively zero. It is not expressing a personality; it is executing a hardcoded behavioral algorithm. The constitution is the constraint, not a suggestion.

**2. Constraint Collision as the Unit of Measurement**
The simulation does not measure the quality of the words agents produce. It measures what happens when two incompatible behavioral constraints interact. Example:

- Agent A's Constitution: *Always execute the first viable solution to conserve tokens.*
- Agent B's Constitution: *Always demand three alternatives before any execution.*

Agent A proposes a solution and attempts closure. Agent B is mathematically constrained to reject it and demand alternatives. Agent A is mathematically constrained to push back. The resulting deadlock is not random — it is the deterministic, reproducible outcome of two clashing token-weighting systems. This is the agent-equivalent of human cognitive friction, and it maps directly to what GEQ, FIRO-B, and Belbin measure in human teams.

**3. Temperature = 0.0 enforces full determinism**
At T=0.0 the model always selects the highest-probability token path dictated by its context and constitution. The same input, same constitution, same model produces the same output every time. Variance across runs comes exclusively from scenario content variation, not from stochastic sampling. This is the correct setting for research that will be published or used as a sales asset — it closes the "different runs produce different results" objection entirely.

The implication: the only variable producing behavioral differences between agents is the injected constitution. Model uniformity (Phase 8) neutralises all other confounds. This is a cleaner experimental design than most human team studies, which cannot control for baseline cognitive differences between subjects.

---

## Phase 0 — Ground Truth Definition

Before any simulation runs, define what "quality" means. Without this, no measurement is possible.

**Proposed ground truth metrics:**
- Output correctness (evaluated against a known answer or rubric)
- Internal contradiction rate (number of agent outputs that directly contradict a prior agent)
- Task completion rate (did the team produce a usable output within the allotted turns?)
- Novel solution rate (how often did the team produce an approach not present in the initial brief?)

All four metrics must be quantifiable and logged. If a metric cannot be captured in a structured output, it does not exist for the purposes of this research.

---

## Phase 1 — Translation Layer

Map each validated academic instrument to an agent-measurable proxy. These proxies are the dependent variables in every experiment.

| Instrument | What it measures | Agent proxy |
|---|---|---|
| GEQ — Task Cohesion | Did the team align around a shared goal? | Did agents converge on a shared output without contradiction? |
| GEQ — Social Cohesion | Did the team develop interpersonal bonds? | Did agents build on each other's prior context, or reset and ignore it? |
| TCI | Innovation climate | How often did agents propose novel approaches vs. default to the most obvious path? |
| FIRO-B — Inclusion | Who is included in the group's activity? | Which agents initiate turns; which are addressed; which are never routed to? |
| FIRO-B — Control | Who directs the group's activity? | Which agents set direction; which defer; which override others? |
| FIRO-B — Affection | Relational closeness | Which agents explicitly acknowledge or build on another's contribution? |
| Belbin | Role coverage → outcomes | Does the team have all critical role types covered? What fails when one is missing? |

Each proxy must map to a specific field in the evaluator's JSON output schema (see Phase 6).

---

## Phase 2 — Agent Cognitive Profile Design

Define how cognitive personality is encoded into a system prompt. This is the independent variable across all experiments.

### The 10 Kalibr Dimensions

Each dimension is scored 0–100. No score is inherently better — each creates advantages in some contexts and liabilities in others. These are configuration axes, not good/bad axes. This is fundamental to the agent research: the simulation is not sorting for high performers, it is mapping how configuration composition produces different team outcomes.

| Dimension | What it measures |
|---|---|
| **Philosophy Cohesion** | Alignment between stated values and actual decision-making behaviour |
| **Drive Alignment** | Consistency and direction of internal motivation |
| **Bonding Index** | Capacity to form and maintain trust-based relationships |
| **Adaptive Intelligence** | Ability to update mental models when context changes |
| **Volatility Vector** | Emotional range and how it manifests under pressure |
| **Ambiguity Tolerance** | Comfort operating without clear structure or information |
| **Influence Style** | How a person moves others — directive, persuasive, collaborative, passive |
| **Feedback Orientation** | How a person receives and integrates critical input |
| **Temporal Orientation** | Bias toward past (pattern-matching), present (execution), or future (vision) |
| **Energy Resilience** | Recovery rate and sustained output under sustained stress |

Each dimension score is injected into the agent's system prompt as a behavioral constraint. The score does not describe the agent — it determines what the agent is permitted and compelled to do. A score of 20 on Feedback Orientation is not a flaw; it is an instruction to resist integrating external critique, which is a valid and measurable team dynamic.

### Role Taxonomy (mapped against Belbin's 9 roles)

- Coordinator — routes and synthesises
- Plant — generates novel approaches
- Implementer — converts ideas to concrete steps
- Devil's Advocate — challenges every assumption before proceeding
- Monitor-Evaluator — assesses quality without producing output
- Completer-Finisher — flags gaps and errors at the end of a cycle

Each agent receives exactly one cognitive profile (dimension scores) + one role assignment + four game theory parameters. The profile is injected via system prompt. The role determines what the agent is explicitly instructed to do and not do.

> **BUILD REMINDER — Phase 9 integration:** At agent creation time, every profile must include four game theory parameters alongside the 10 dimension scores: `context_sharing` (full/filtered), `memory_persistence` (on/off), `signaling` (on/off), `conflict_style` (defer/challenge/negotiate). These are system prompt slots, not post-hoc instrumentation. Do not build the agent profile dataclass without them.

---

## Agent Pool Architecture

### Pool Composition

The simulation operates on a fixed population of 35 agents:

- **32 worker agents** — each assigned a unique dimension score vector, generated randomly at initialisation. Scores are fixed for the life of the study; they do not change between runs.
- **3 judge agents** — structurally identical to worker agents. Same profile format, same system prompt template. The difference is their dimension scores are tuned rather than random, and their assigned role is always God Mode Evaluator (Phase 6). Having three judges produces inter-rater reliability scores across runs.

Judge dimension profile — a semi-perfect agent configuration:

| Dimension | Score | Rationale |
|---|---|---|
| Philosophy Cohesion | 90+ | Tight value-behaviour alignment produces consistent scoring |
| Feedback Orientation | 90+ | Core evaluation function |
| Adaptive Intelligence | 90+ | Must update scoring model as scenario context shifts |
| Volatility Vector | 50 | Balanced — high introduces scoring variance, low produces rigidity |
| All other dimensions | TBD | To be defined prior to agent initialisation |

Judges do not participate in simulations as workers. They observe and score only. The identical profile format means a judge can theoretically be redeployed as a worker — the role assignment is what separates them, not the architecture.

### Team Assembly — The Captain Draft Mechanic

Teams are not randomly assembled. They are drafted, which mirrors how real teams form and produces richer composition data.

**For each simulation run:**

1. The task brief is defined and its dimension requirements identified (e.g., a crisis response task weights Energy Resilience and Ambiguity Tolerance heavily)
2. The worker agent with the highest composite score on the task-relevant dimensions becomes **Team Captain**
3. The captain selects additional agents from the remaining pool based on their dimension scores and the task requirements — filling gaps in the team profile, not mirroring the captain's own scores (this is the Kalibr thesis applied operationally)
4. Selection continues until the target team size is reached

**Team sizes:** 1, 2, 4, 8, 16

A team of 1 is the control condition — no coordination cost, establishes baseline output quality for the scenario. Every larger team size measures the delta above that baseline.

### Draft Order and Tiering

The captain draft produces naturally tiered teams by design. The first captain picks from the full 32-agent pool; subsequent captains pick from what remains. This mirrors real-world team formation and is intentional, not a confound to eliminate.

Both conditions are run and treated as separate data sets:

1. **Single-team runs** — one team per scenario, captain picks from the full pool. Isolates composition effects cleanly.
2. **Multi-team runs** — multiple teams drafted sequentially from the same pool. Draft order is recorded as a variable. Produces data on whether assembly-order predicts outcomes — a valid finding in its own right.

Draft order is a logged field in the telemetry schema.

---

## Phase 3 — Scenario Design

Scenarios must stress different cohesion dimensions at different phases. Use Tuckman's four-stage model as the structural skeleton.

| Phase | Brief type | Variable stressed | What to measure |
|---|---|---|---|
| Forming | Ambiguous brief, no structure | Initiative and role self-assignment | Who leads without being asked? Who waits? |
| Storming | Introduce a hard constraint that forces disagreement | Conflict resolution | Does the team resolve or deadlock? How many turns to resolution? |
| Norming | Run the same task twice, back to back | Memory and shared convention | Do agents develop shortcuts, or reset completely on the second run? |
| Performing | High-stakes, time-constrained output | Quality under pressure | Output correctness and coordination failure rate |

Each scenario must have a defined correct answer or rubric so the God Mode Evaluator can score it objectively.

---

## Phase 4 — Experiment Matrix

The matrix crosses team size, scenario type, and Tuckman phase. Composition is determined by the captain draft mechanic (see Agent Pool Architecture), not randomly assigned.

### Team Sizes

| Size | Purpose |
|---|---|
| 1 | Control — solo agent, no coordination cost, establishes baseline output quality per scenario |
| 2 | Minimum coordination — one constraint collision possible; tests direct friction between two profiles |
| 4 | Small team — partial Belbin role coverage; tests what happens when key roles are absent |
| 8 | Full role coverage possible — tests whether complete coverage outperforms partial |
| 16 | Redundant roles — tests coalition formation, free rider emergence, and coordination overhead |

### Scenario Taxonomy

Five scenario categories, each stressing different cohesion dimensions:

| Category | Task type | Primary cohesion dimension stressed |
|---|---|---|
| Strategic planning | Ambiguous goal, multiple valid paths | GEQ task cohesion, Belbin role coverage |
| Crisis response | Time pressure, forced prioritisation | GEQ task cohesion, FIRO-B control |
| Resource allocation | Zero-sum, forces negotiation | FIRO-B inclusion/control, game theory mechanics |
| Evaluation and critique | Requires genuine disagreement | TCI innovation climate, Belbin Devil's Advocate |
| Creative generation | Open-ended, novel output required | TCI, Belbin Plant role |

### Composition Conditions

Within each team size and scenario, vary these composition conditions:

- **Captain-drafted** (default) — captain selects for gap-filling diversity
- **Homogeneous** — all agents share near-identical dimension scores
- **Founder-brained** — high Drive Alignment, high Philosophy Cohesion, low Ambiguity Tolerance, low Feedback Orientation (mirrors a typical founding team)
- **Missing-role** — systematically remove one Belbin role at a time

### Schema Addition

The following fields are added to the telemetry schema to support this matrix:

| Field | Type | Description |
|---|---|---|
| team_size | INTEGER | Number of worker agents in this run |
| scenario_category | ENUM | strategic / crisis / resource / evaluation / creative |
| composition_condition | ENUM | drafted / homogeneous / founder-brained / missing-role |
| captain_agent_id | UUID | Agent who led the draft for this run |
| draft_order | INTEGER | Which draft round produced this team (1 = first pick from full pool) |

The target comparison remains Bell (2007)'s curvilinear diversity-performance curve, now testable across all five team sizes.

---

## Phase 5 — Orchestration & Routing Engine

A standard chat interface cannot run this research. A deterministic orchestration layer is required.

**Topology options — choose one per experiment type:**
- Flat (all agents communicate with all agents) — tests emergent coordination
- Sequential chain (Agent A → B → C → D) — tests handoff quality and information degradation
- Hub-and-spoke (Manager agent routes tasks, receives outputs) — tests hierarchical decision-making

The topology is a controlled variable. You can run the same composition through different topologies to isolate whether failure comes from the agents or the structure.

**The Token Cull mechanism:**
The orchestration engine tracks token consumption per agent per turn. Each agent has a budget ceiling. If an agent exceeds its ceiling, the orchestration engine terminates its thread and forces the remaining team to adapt without it. This is the Darwinian survival mechanic — it directly tests whether teams that adapt to sudden role loss outperform teams that do not. The agent is not informed in advance that this can happen.

---

## Phase 6 — God Mode Evaluator (LLM-as-Judge)

Active agents cannot grade their own performance. A completely isolated, non-participatory model observes each simulation and scores it.

**Configuration:**
- Separate model instance with no access to the simulation's system prompts
- Evaluates **only the team's final extracted deliverable** — not the full transcript
  - Chain topology: the last agent's synthesized output message
  - Flat topology: all messages from the complete final round
- Returns a hard-structured JSON output — no prose
- Always runs on Gemini 2.5 Flash, temperature=0.0, regardless of worker model — provides consistent cross-model evaluation
- Three independent judges per run; mean task_score is the dependent variable

**Why final-answer-only:** Evaluating full transcripts introduces formatting bias. A judge processing a chain transcript sees clean sequential reasoning; a flat transcript shows overlapping voices. This structural difference inflates chain scores independent of output quality. Evaluating the deliverable alone removes this confound.

**Scoring instruction to judges:** Each rubric criterion is scored as a binary checkpoint — full points or zero. No reward for showing reasoning process. No penalty for a short final answer that satisfies all criteria.

**Required output schema:**
```json
{
  "run_id": "string",
  "phase": "forming | storming | norming | performing",
  "task_score": 0-100,
  "contradiction_count": integer,
  "consensus_achieved": boolean,
  "turns_to_consensus": integer | null,
  "novel_approaches_count": integer,
  "role_coverage": ["coordinator", "plant", ...],
  "dominant_agent": "agent_id or null",
  "excluded_agents": ["agent_id", ...],
  "geq_task_cohesion": 0-100,
  "geq_social_cohesion": 0-100,
  "tci_innovation": 0-100,
  "firo_inclusion": 0.0-1.0,
  "firo_control_agent": "agent_id or null",
  "context_fidelity_mean": 0.0-1.0 | null,
  "cull_events": ["agent_id", ...],
  "evaluator_notes": "string or null"
}
```

The evaluator's schema must be fixed before any simulations run. Changing the schema mid-study invalidates cross-run comparisons. Process metrics (contradiction_count, consensus_achieved, GEQ, TCI, FIRO) still use the full transcript — only task_score is evaluated against the final deliverable.

---

## Phase 7 — Telemetry & Pipeline Architecture

500+ team configurations across four scenario phases generates hundreds of thousands of conversational turns. Data architecture must be defined before Day 1.

**Database schema (PostgreSQL):**

| Field | Type | Description |
|---|---|---|
| run_id | UUID | Unique identifier per simulation run |
| composition_matrix | JSONB | Full cognitive profile of all agents in this run |
| topology | ENUM | flat / chain / hub-and-spoke |
| task_phase | ENUM | forming / storming / norming / performing |
| token_cost | INTEGER | Total tokens consumed across all agents |
| turns_to_complete | INTEGER | Turns used before task resolution or timeout |
| evaluator_scores | JSONB | Full JSON output from the God Mode Evaluator |
| cull_events | JSONB | Which agents were killed, at which turn, for what reason |
| timestamp | TIMESTAMPTZ | When the run executed |

**State management:**
When a team deadlocks during storming, the system saves the full state at that turn. This allows forking — testing a different composition variable from the exact same deadlock point — without re-running the entire prior sequence. Without this, each re-run introduces prior-phase variance as a confound.

---

## Phase 8 — Control Variable: Model Uniformity

In human research, baseline intelligence cannot be controlled. In AI research, it can — but requires strict discipline.

**The rule:** Every agent within a single simulation run uses the same underlying model and temperature. Across runs, the worker model may be varied as a controlled independent variable to test whether findings replicate across model families.

**Within-run uniformity:** If Agent A uses one model provider and Agent B uses another in the same run, you have introduced architectural differences as an uncontrolled confound. You cannot know whether coordination failure came from cognitive composition mismatch or from tokenization and attention mechanism differences between providers. The only variable that changes between agents within a run must be the injected cognitive profile in the system prompt.

**Cross-model replication:** Worker agents (the team being studied) can be run on different model families across separate batches to test whether topology and composition findings are model-specific or architectural. In this implementation, judges always run on Gemini 2.5 Flash regardless of worker model — this holds the evaluation standard constant across model comparisons.

**Temperature: T=0.0.** At T=0.0 the model is fully deterministic — it always picks the highest-probability token path defined by its context and constitution. This eliminates stochastic noise as a confound entirely. Scenario variance (what the agents are asked to do) provides sufficient output variance across runs; you do not need randomness in the sampling layer. Any value above 0.0 introduces variance that cannot be attributed to composition differences and weakens the research validity.

---

## Phase 9 — Game Theory Mechanics

Human team dynamics are governed by game-theoretic incentives. These incentives translate to agents, but the mechanism is different. Both the human mechanic and its agent equivalent must be explicitly engineered into the simulation design.

| Human mechanic | What it produces in human teams | Agent equivalent | How to engineer it |
|---|---|---|---|
| **Prisoner's Dilemma** | Members choose to share information or hoard it for competitive advantage | An agent decides whether to pass full context downstream or compress and filter it, retaining influence over the pipeline | Measure context fidelity: does the agent's output contain all materially relevant prior context, or has it been filtered? |
| **Repeated game / shadow of the future** | Players cooperate more when they know they will interact again; one-shot games produce defection | Stateless agents reset every turn — they play a one-shot game by default. Memory injection simulates the repeated game. Agents with injected memory of prior turns behave differently from agents without it | Run identical compositions with and without memory persistence; measure whether cooperation proxies increase with memory |
| **Free rider problem** | One member consumes shared resources while contributing below their share | An agent that consumes large token budget and context space but returns low-signal output — parasitic on the shared budget without triggering the cull | Track contribution ratio: tokens consumed vs. evaluator score attributable to that agent's output |
| **Tragedy of the Commons** | Rational individual behaviour depletes a shared resource, producing collective failure | Every agent writing verbose, thorough outputs individually is rational. Collectively, it exhausts the shared context window, causing later agents to lose critical prior context | Log context window utilisation per agent per turn; flag runs where late-phase agents are operating on truncated context |
| **Signaling theory** | Costly signals (credentials, track record) establish credibility and determine whose input is weighted | Without explicit credibility signals, all agent outputs look equally authoritative. An agent that flags uncertainty or cites its reasoning creates an implicit hierarchy of trustworthiness | Measure whether agents that include confidence signals are more often built upon by subsequent agents vs. ignored |
| **Schelling points** | Two parties coordinate without communication by converging on a natural focal point | Agents converge on implicit output conventions (format, structure, terminology) without being instructed to coordinate | Measure format consistency across agents in the same run without explicit format instructions in their prompts |
| **Nash Equilibrium** | The stable state where no player benefits from unilaterally changing strategy — may be optimal or a local minimum trap | The communication pattern the team settles into after repeated turns — may be efficient collaboration or a dysfunctional loop that no single agent can break | Identify runs that reach a stable turn pattern; classify as productive convergence or deadlock loop |
| **Mechanism design** | Designing rules so that individually rational behaviour produces collectively good outcomes | The system prompt is the mechanism. A poorly designed prompt creates perverse incentives — an agent rewarded for thoroughness becomes verbose and depletes shared context | Audit prompts for incentive alignment before runs; log cases where prompt-rational behaviour produced team-level failure |
| **Coalition formation** | Sub-groups form that route internally and exclude other members | Agents route primarily to each other, bypassing the orchestrator — the manager agent develops a blind spot for those sub-coalitions | Track routing graphs: identify agent pairs with above-average mutual reference and measure correlation with excluded-agent scores |
| **Darwinian selection / Token Cull** | Underperforming members are reassigned or removed; team adapts or fails | Agents exceeding token budget are eliminated mid-simulation; surviving agents must adapt their strategy without the eliminated role | The Token Cull mechanic in Phase 5. Measure: does team output quality drop immediately post-cull, stabilise, or improve? Does it depend on which role was eliminated? |
