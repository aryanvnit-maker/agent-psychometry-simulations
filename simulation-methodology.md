# Simulation Methodology

Framework for replicating validated human team research in an AI agent environment to generate novel cohesion and composition correlations.

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

**Cognitive dimensions** (to be mapped against Kalibr's 10 dimensions):
- Risk tolerance (conservative → aggressive)
- Autonomy (defers frequently → acts unilaterally)
- Contrarianism (validates → challenges by default)
- Verbosity (minimal output → exhaustive output)
- Closure drive (comfortable with ambiguity → pushes for resolution)

**Role taxonomy** (to be mapped against Belbin's 9 roles):
- Coordinator — routes and synthesises
- Plant — generates novel approaches
- Implementer — converts ideas to concrete steps
- Devil's Advocate — challenges every assumption before proceeding
- Monitor-Evaluator — assesses quality without producing output
- Completer-Finisher — flags gaps and errors at the end of a cycle

Each agent receives exactly one cognitive profile + one role assignment. The profile is injected via system prompt. The role determines what the agent is explicitly instructed to do and not do.

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

Vary cognitive composition systematically across runs. Every other variable must be held constant.

**Composition variants to run:**
- All-homogeneous (every agent shares the same profile)
- All-diverse (maximum spread across all cognitive dimensions)
- Single-role missing (remove Devil's Advocate, then Coordinator, then Plant — one at a time)
- Single-dimension extremes (all high autonomy, all high closure drive, etc.)
- Founder-brained configuration (mirrors a typical founding team: high autonomy, high closure, low contrarianism)
- Kalibr-recommended configuration (fills gaps rather than mirrors)

Each variant must run a minimum number of times per scenario phase to generate statistically usable data. The target comparison is Bell (2007)'s curvilinear diversity-performance curve.

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
- Receives only the transcript of a completed simulation phase
- Returns a hard-structured JSON output — no prose

**Required output schema:**
```json
{
  "run_id": "string",
  "phase": "forming | storming | norming | performing",
  "task_score": 0-100,
  "contradiction_count": integer,
  "consensus_achieved": boolean,
  "turns_to_consensus": integer,
  "novel_approaches_count": integer,
  "role_coverage": ["coordinator", "plant", ...],
  "dominant_agent": "agent_id or null",
  "excluded_agents": ["agent_id", ...],
  "evaluator_notes": "string (optional, one line max)"
}
```

The evaluator's schema must be fixed before any simulations run. Changing the schema mid-study invalidates cross-run comparisons.

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

**The rule:** Every agent in every simulation runs on the same underlying model at the same temperature setting.

**Rationale:** If Agent A uses one model provider and Agent B uses another, you have introduced architectural differences as an uncontrolled confound. You cannot know whether coordination failure came from cognitive composition mismatch or from tokenization and attention mechanism differences between providers. The only variable that changes between agents must be the injected cognitive profile in the system prompt.

Suggested baseline: a single model, temperature 0.2 (low enough to reduce stochastic noise, high enough to avoid fully deterministic outputs).

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
