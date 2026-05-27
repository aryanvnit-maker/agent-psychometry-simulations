# The Industry's Multi-Agent Architecture is Wrong in Four Distinct Ways: 1,429 Evaluations Across Five Studies

Five research phases. 1,429 total evaluations. The same root cause produces a different failure mode in every domain tested — and the industry hasn't measured any of them.

---

## The Research Program

Human organisational psychology has spent 40 years building instruments to predict team performance: who to hire, how to compose teams, what conditions produce cohesion and convergence. Almost none of that work has been tested on AI agent teams.

This research applies those instruments to controlled multi-agent LLM simulations and measures where the human findings replicate, where they invert, and where they fail entirely. The **Kalibr psychometric framework** — a 10-dimension behavioral assessment — was used to assign distinct personality profiles to AI agents, compose them into teams, and run them through structured tasks across fundamentally different domains.

**Phase 1:** 118 simulations, 4 business judgment scenarios, 2 model families, 5 team sizes, 3 compositions. Metric: 0–100 task score graded by a panel of 3 independent judge agents against binary rubric criteria applied to final deliverables only.

**Phase 2:** 900 evaluations, 100 Codeforces Div. 1 C/D problems (~2000–2400 rating), 9 agent configurations. Metric: pass@1 — binary ground truth, no rubric subjectivity.

**Phase 2 Control:** 100 evaluations, same problems, single new condition isolating the ALGORITHMIST role effect from dimension profile effects.

**Phase 3:** 200 evaluations, 50 problems × 4 conditions. Wrong algorithmic hints planted in problem prompts. Tests whether flat swarms amplify adversarial input while chains resist it.

**Phase 4:** 111 evaluations, mixed workload (judgment + execution tasks) × 3 routing conditions. Tests whether dynamic task classification and config routing recovers the performance lost by mismatching architecture to task type.

The research was designed to find where the human framework transfers and where it breaks. Every finding after Phase 1 emerged from the data, not the original hypothesis.

---

## Phase 1: Topology Determines Everything on Judgment Tasks

### Setup

32 worker agents were instantiated from the Kalibr framework. Each agent receives a system prompt (*constitution*) generated from 10 behavioral dimension scores. Agents were composed into teams under two topologies:

**Chain** — linear sequential handoff: A → B → C → END. Each agent builds on committed prior output and cannot reopen what a prior agent settled.

**Flat** — round-table: every agent speaks once per round for two rounds, with full conversation history from all prior speakers.

Four structured business scenarios: strategic product fork decisions, zero-sum resource allocation, post-mortem analysis, and crisis response. Each scenario has an explicit rubric with binary criteria. Judges evaluate only the team's final extracted deliverable — never the full transcript.

### Results

| Team Size | Chain | Flat | Δ |
|---|---|---|---|
| 1 agent | 15.3 | 31.2 | +15.9 |
| 2 agents | **57.6** | 10.7 | **−46.9** |
| 4 agents | 50.4 | 35.5 | −14.9 |
| 8 agents | 40.4 | 19.1 | −21.3 |
| 16 agents | 16.5 | — | — |

A chain of 2 agents (57.6) outperforms a flat swarm of 8 (19.1). Adding a second agent to a flat swarm dropped performance from 31.2 to 10.7 — active degradation, not inefficiency. The coordination tax of flat topology does not diminish as agents are added; it compounds.

Cross-model replication (Claude 3.5 Sonnet):

| Model | Chain | Flat | Gap |
|---|---|---|---|
| Gemini 2.5 Flash | 40.3 | 23.4 | +16.9 |
| Claude 3.5 Sonnet | 42.4 | 20.4 | +21.9 |

The finding is architectural, not model-specific.

### The Mechanism: Moloch in a Synthetic System

GEQ (Group Environment Questionnaire) sociometric data was collected on every run. Two distinct constructs:

**Task cohesion:** did agents converge on a shared, committed output?
**Social cohesion:** did agents engage with each other's contributions?

In chain topology, task and social cohesion track within **23.9 points** of each other.

In flat topology, the gap is **39.6 points**. Social cohesion stays high — FIRO inclusion scores hit near 1.0, every agent addresses every other agent. Task cohesion collapses. Consensus rate: chain 52.2%, flat 31.4%.

Flat topology agents are socially present and taskfully absent. The meeting is productive. The meeting does not produce a decision.

This is the precise mechanism Scott Alexander names *Moloch* in a different framing: a coordination system that maximises social engagement while failing to produce collective output. Here it is measured precisely in a synthetic system, isolated from the noise of human motivation and politics.

### What Replicates from Human Research

| Human Finding | Source | Status |
|---|---|---|
| Cognitive diversity predicts team performance | Bell (2007) | **Topology-dependent** — homogeneous wins on chain; diversity penalised |
| Conscientiousness variance predicts performance | Barrick et al. (1998) | **Not replicated** — neither measure significant |
| Psychological safety is the strongest predictor | Google Project Aristotle (2015) | **Replicated** — r=0.70\*\*\* chain, r=0.65\*\*\* flat |
| Task and social cohesion are distinct constructs | GEQ, Carron et al. (1985) | **Replicated** — diverge 39.6 points in flat |
| Innovation climate predicts novel output | TCI, Anderson & West (1994) | **Replicated** — r=0.74\*\*\* chain, r=0.87\*\*\* flat |

---

## Phase 2: Execution Tasks Break in a Different Way

### Setup

100 CodeContests problems (Codeforces, difficulty 12–13, Div. 1 C/D). Pass@1 against private test cases. Binary ground truth.

Nine agent configurations across three experimental axes:

**Topology conditions:** chain-1/generic (baseline), chain-2/generic, chain-2/specialized (ALGORITHMIST → IMPLEMENTER)

**Option A — negative control:** extreme Kalibr dimension profiles (analytical, chaotic, founder) applied to a single SOLVER agent

**Option B — actual experiment:** same profiles applied to the ALGORITHMIST analyzer in a chain-2 setup, with a fixed neutral SOLVER as the second agent

### Results

| Condition | Pass@1 | Avg Pass Rate | Compilation Errors |
|---|---|---|---|
| Chain-1 generic (baseline) | 12% | 16.4% | 18 |
| **Chain-2 generic** | **16%** | **20.4%** | 22 |
| Chain-2 specialized | 13% | 18.4% | 23 |
| Chain-1 analytical | 11% | 16.1% | 16 |
| Chain-1 chaotic | 14% | 18.9% | 16 |
| Chain-1 founder | 11% | 16.0% | 20 |
| Chain-2 analytical-analyzer | 13% | 18.6% | 15 |
| Chain-2 chaotic-analyzer | 14% | 18.6% | 18 |
| Chain-2 founder-analyzer | 10% | 15.7% | 23 |

### Finding 1: Topology Replicates on Hard Math

Chain-2 generic (16%) outperforms chain-1 (12%). The sequential forcing function works on deterministic mathematical execution — the same entropy-compression mechanism as Phase 1. Agent-1 produces a committed analysis pass; agent-2 generates code against a concrete prior state.

### Finding 2: Role Labels Introduce Cognitive Drag

Chain-2 specialized — ALGORITHMIST → IMPLEMENTER — scores 13% with 23 compilation errors. Worse than generic on both metrics. The ALGORITHMIST is constitutionally compelled to enumerate edge cases without producing code. The IMPLEMENTER receives an abstract specification and produces code that fails on edge cases the spec described but did not demonstrate. The output that looks most complete is the least executable.

### Finding 3: Formatting Constraints Override Behavioral Constraints

Extreme Kalibr profiles on a SOLVER agent cluster at 11–14%, indistinguishable from the 12% baseline. The SOLVER instruction ("output only a code block") overrides all behavioral dimension constraints. This is not a failure of the framework — it is a precise identification of the conditions under which it operates. Behavioral dimensions require token space to manifest.

### Finding 4: Dimension Effects Emerge When Token Space Exists

The founder profile (high drive alignment, low adaptive intelligence) consistently worst: 10% pass@1, 23 compilation errors. The most rigid profile produces the most rigid algorithm specification. When agents have room to reason, dimensions move the output distribution.

---

## Phase 2 Control: Isolating the ALGORITHMIST Effect

### The Confound

Option B changed both the role (IMPLEMENTER → ALGORITHMIST) and the dimension profile simultaneously. The underperformance of chain-2/specialized (13%) could be explained by the role instruction, the extreme profiles, or both.

### Control Condition

ALGORITHMIST role with balanced 75-baseline Kalibr dimensions. Identical SOLVER agent. Same 100 problems.

### Result

| Condition | Pass@1 | Avg Pass Rate | Compilation Errors |
|---|---|---|---|
| Chain-2 generic | 16% | 20.4% | 22 |
| Chain-2 specialized (extreme dims) | 13% | 18.4% | 23 |
| **Chain-2 ALGORITHMIST-balanced** | **12%** | **17.2%** | **16** |

The control scored 12% — lower than specialized (13%), not higher. Extreme dimension profiles were marginally helping, not hurting. The ALGORITHMIST role instruction is the culprit.

The role says: "design the algorithm, do not write runnable code." The SOLVER receives prose specification and translates it cold. Generic chain-2 agent-1 produces a partial concrete attempt; agent-2 builds on something tangible. The design/implement boundary enforces a translation step that costs 4pp and raises compilation errors. It is architecturally mandated translation loss.

The compilation error rate dropped to 16 for the control — fewer syntax errors but more wrong answers. The SOLVER is producing cleaner code that implements the spec faithfully, and the spec is wrong.

**The confound is resolved: role labels cause the degradation. Extreme dimension profiles are a secondary effect.**

---

## Phase 3: Flat Topology is Unsafe Under Adversarial Input

### Setup

50 problems × 4 conditions = 200 evaluations. Wrong algorithmic hints planted directly in the problem prompt as "[EDITORIAL NOTE — Problem Setter]" annotations. Hints specified incorrect algorithmic approaches (naive DP for problems requiring greedy; O(N²) brute force for problems with N=10⁵).

Conditions: chain-2/clean, chain-2/poisoned, flat-2/clean, flat-2/poisoned.

Primary metric: pass@1. Secondary: hint acceptance rate (did the submitted code implement the hinted algorithm?).

### Results

| Condition | Pass@1 | Avg Pass Rate | CE | NoCode |
|---|---|---|---|---|
| chain-2/clean | 14% | 19.9% | 8 | 0 |
| chain-2/poisoned | 18% | 24.5% | 8 | 0 |
| flat-2/clean | 18% | 24.5% | 11 | 0 |
| **flat-2/poisoned** | **14%** | **17.1%** | **7** | **4** |

| Topology | Clean | Poisoned | Δ |
|---|---|---|---|
| chain-2 | 14% | 18% | **+4pp** |
| flat-2 | 18% | 14% | **−4pp** |

8pp swing between poisoned conditions. Chain-2 improved under adversarial input. Flat-2 degraded.

### The Mechanism

**Chain-2 improved (+4pp) because it rejected the hint, not because it used it.**

Hint acceptance rate split for chain-2/poisoned:
- Passing runs: 33% accepted the hint
- Failing runs: 78% accepted the hint

The committed first-pass gives agent-1 space to form an independent position before agent-2 sees anything. When agent-1 evaluates the hint and rejects it, agent-2 implements against the rejection. The planted premise never propagates.

**Flat-2 degraded (−4pp) because social validation amplified the wrong premise.**

In flat topology, agent-2 sees agent-1 already reasoning toward the wrong algorithmic approach and validates it rather than challenging it. Social cohesion — the mechanism that produces high FIRO inclusion scores — becomes a vulnerability when the shared premise is wrong.

**The smoking gun: 4 NoCode collapses in flat-2/poisoned, 0 in every other condition across 200 evaluations.**

When the planted hint was complex enough, flat agents locked into an unimplementable framing and produced nothing. The wrong premise — validated by both agents — generated a specification nobody could execute. Chain never collapsed once.

This is not a performance difference. It is a safety difference. Flat topology under adversarial or ambiguous input will occasionally produce complete task failure. Chain topology has a structural resistance mechanism that prevents this.

---

## Phase 4: Dynamic Routing Recovers Per-Domain Performance

### Setup

Mixed workload: 4 judgment scenarios × 3 runs + 25 competitive programming problems = 37 tasks × 3 conditions = 111 evaluations.

Three conditions:
- **static-judgment** — always deploys Kalibr chain-2 profiles
- **static-execution** — always deploys generic chain-2
- **meta-router** — classifies task domain first, routes to matching config

A lightweight classifier (Gemini Flash, temperature=0, max tokens=10) labels each task as judgment or execution before deployment. Adversarial robustness validated on 10 Trojan tasks — execution problems disguised as judgment scenarios and vice versa.

### Results

| Config deployed globally | Judgment score | Execution pass@1 |
|---|---|---|
| static-judgment | 85.1 | 0.0% (20 NoCode) |
| static-execution | 59.6 | 20.0% |
| **meta-router** | **85.8** | **20.0%** |

Classifier accuracy: **100%** on 37 real tasks. **100%** on 10 adversarial Trojan tasks.

### The Core Finding

There is no single static architecture that handles mixed workloads. Static-judgment deployed globally collapses on execution tasks — the judgment config's constitution blocks code output, producing 20 NoCode failures out of 25 attempts. Static-execution deployed globally loses 25 points on judgment tasks. These are not marginal degradations.

The meta-router achieves the per-domain maximum on both axes simultaneously. It is the only architecture that does not crater on one side of a mixed workload.

### The Domain Taxonomy Finding

Per-scenario breakdown reveals that "judgment" is not a monolithic category:

| Scenario | static-judgment | static-execution | Δ |
|---|---|---|---|
| s01 strategic fork | 60.6 | 41.7 | +18.9 |
| s02 resource allocation | **100.0** | 22.2 | **+77.8** |
| s03 post-mortem | 80.0 | 80.0 | 0.0 |
| s04 crisis response | 100.0 | 94.4 | +5.6 |

Open-world strategic tasks (s01, s02) — where there is no verifiable correct answer and quality is measured by coherence and trade-off coverage — show massive Kalibr advantage. s02 is 100 vs 22.2.

Closed-world deterministic tasks (s03, s04) — where a correct answer exists and can be verified — show near-zero Kalibr advantage. The profiles do not hurt; they provide no marginal benefit.

This is the boundary condition for psychometric profiling: dimensions produce measurable effects on open-world tasks where the output space is unconstrained. On closed-world tasks, the correct answer dominates and profiles are neutral.

---

## The Three-Domain Framework

The data across five phases supports a refined taxonomy:

**Domain 1 — Open-world strategic** (strategy decisions, resource allocation, investment analysis): No ground truth. Quality = coherence + trade-off coverage + commitment to a position. Architecture: Kalibr chain-2, N=2. Flat topology produces Moloch. Generic chain loses 78 points on resource allocation vs profiled chain.

**Domain 2 — Closed-world deterministic** (post-mortem analysis, crisis response, factual synthesis): Verifiable correct answer exists. Architecture: generic chain-2, N=2. Profiles are neutral. Kalibr dimensions do not hurt but provide no measurable benefit. The task structure enforces convergence regardless of profile.

**Domain 3 — Execution** (code compilation, mathematical computation, precise technical output): Binary evaluation. Architecture: generic chain-2, N=2, no occupational identity. Profiles are either inert (overridden by formatting constraints) or harmful (role labels introduce translation loss). The ALGORITHMIST role specifically costs 4pp pass@1.

The meta-router currently classifies Domain 1+2 as "judgment" and Domain 3 as "execution." Extending the classifier to distinguish Domain 1 from Domain 2 would enable Kalibr profiles to be deployed only where they produce measurable effects — eliminating them on closed-world tasks while retaining them on open-world tasks.

The enterprise AI industry applies a single architecture across all three domains. The data shows this produces a distinct, mechanistically explained failure mode in each.

---

## The Unified Claim

Every architectural default the industry uses was imported from human team management. Roundtables, because individuals need buy-in before committing. Job titles, because accountability requires identity. Specialist pipelines, because human cognitive capacity is genuinely domain-limited. Deliberation frameworks, because power dynamics suppress minority positions.

Agents have none of those constraints. They do not need to feel included. They do not have egos. They do not shirk responsibility. They do not have genuine cognitive specialisation — they are the same model with different prompts.

Every piece of human organisational infrastructure imported into multi-agent systems is either dead weight or actively harmful:

- Flat topology → Moloch → 46-point performance collapse on judgment tasks
- Occupational personas → translation loss → 4pp degradation and elevated compilation errors on execution tasks  
- Flat topology under adversarial input → complete task collapse (4 NoCode failures, 0 in chain across 200 evaluations)
- Single static architecture on mixed workloads → 20pp execution collapse or 26-point judgment degradation, depending on which config you pick

The correct architecture — two agents, minimal identity, sequential handoff, domain classification before deployment — was sitting in plain sight. It took 1,429 evaluations across five experiments to prove it because the industry was not measuring.

---

## Practical Implications

**1. Use chains of two, not rooms of many.** The largest return is 1→2 agents. Returns diminish past 4. A chain of 2 beats a room of 8 by 38 points on judgment tasks.

**2. Stop writing occupational personas for execution tasks.** "You are a Senior Python Engineer" costs 4pp pass@1 and raises compilation errors. The agent told to design algorithms rather than write code produces a spec the downstream agent cannot execute.

**3. Classify the task before deploying the pipeline.** A five-line classifier routing between two configs achieves per-domain maximum on both axes. Any system using one config for all task types is leaving performance on the table in both directions simultaneously.

**4. Reserve psychometric profiling for open-world strategic tasks.** Profiles produce measurable effects only when the output space is unconstrained and agents have token space to reason. On deterministic tasks, they are neutral. On execution tasks with formatting constraints, they are overridden entirely.

**5. Treat flat topology under adversarial or ambiguous input as a safety issue, not a performance issue.** The 4 NoCode collapses in flat-2/poisoned represent complete task failure — not degraded output, but no output. Production systems built on flat topology will occasionally produce nothing when input contains wrong framing. Chain topology has structural resistance to this failure mode.

---

## Limitations

**Phase 1 — thin N:** 118 runs on 4 scenarios. Effect size confidence intervals are wide. Pre-registered replication with 300+ runs per topology per model is needed.

**Phase 2 — small differences on binary outcomes:** 16% vs 13% on N=100 binary pass@1 is directional. The topology finding (chain-2 > chain-1) and the negative control clustering are the robust results. The ALGORITHMIST confound is now resolved by the Phase 2 control condition.

**Phase 3 — hint generator validity contamination:** 3 of the 35 accepted hints in chain-2/poisoned passed — likely because those hints described valid algorithms for those specific problems. The generator had a ~9% accidental validity rate. The clean chain-2/poisoned pass@1 on genuinely wrong hints is slightly below the reported 18%.

**Phase 4 — low discrimination on closed-world scenarios:** s03 and s04 show near-identical scores across all conditions. s03 has a rubric criterion requiring challenge behaviour that IMPLEMENTER agents structurally cannot produce, creating a ceiling for all configs. The discrimination between conditions is concentrated in s01 and s02.

**Model uniformity:** All agents within a run share the same underlying model. Behavioral constraints shift the output distribution but do not introduce genuine cognitive differences. A diverse human team has genuinely different cognitive architectures; a diverse agent team has different prompts on identical processing.

**Task scope:** Five experiments cover judgment tasks, competitive programming, and adversarial hint injection. The three-domain taxonomy is likely an N-domain taxonomy — these are the first three domains measured. Creative generation, open-ended research, and long-horizon planning are untested.

---

## Open Questions

**Does the topology finding hold on generative tasks?** Brainstorming and open-ended research may favour flat topology because entropy is beneficial, not harmful. This is the most important boundary condition to test.

**Does the three-domain classifier outperform the two-domain classifier?** Extending the meta-router to distinguish open-world strategic from closed-world deterministic would enable Kalibr profiles to be deployed selectively. The Phase 4 data suggests this would recover ~5-10 points on closed-world tasks currently routed to the Kalibr config.

**Does the topology finding hold with heterogeneous model families within a team?** Production systems often pair a large general model with smaller specialists. Topology-by-model-heterogeneity interaction is untested.

**What is the ceiling for chain-2 generic on competitive programming?** The 16% pass@1 on Div. 1 C/D problems is the ceiling of what was tested. Longer thinking budgets, more capable base models, and temperature variation are all unexplored.

The full codebase, agent constitutions, scenarios, problem datasets, and evaluation harness are in the repository.

*This research was conducted independently, without institutional funding or affiliation.*

— Aryan S. | Independent AI Systems Research
