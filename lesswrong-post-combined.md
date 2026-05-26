# The Industry's Multi-Agent Architecture is Wrong in Two Distinct Ways: 1018 Evaluations Across Two Studies

Two research phases. 1018 total evaluations. The same architectural mistake produces a different failure mode depending on task type — and the industry hasn't measured either.

---

## The Research Program

Human organisational psychology has spent 40 years building instruments to predict team performance: who to hire, how to compose teams, what conditions produce cohesion and convergence. Almost none of that work has been tested on AI agent teams.

This research applies those instruments to controlled multi-agent LLM simulations and measures where the human findings replicate, where they invert, and where they fail entirely. The **Kalibr psychometric framework** — a 10-dimension behavioral assessment — was used to assign distinct personality profiles to AI agents, compose them into teams, and run them through structured tasks across two very different domains.

**Phase 1:** 118 simulations, 4 business judgment scenarios, 2 model families, 5 team sizes, 3 compositions. Metric: 0–100 task score graded by a panel of 3 independent judge agents against binary rubric criteria applied to final deliverables only.

**Phase 2:** 900 evaluations, 100 Codeforces Div. 1 C/D problems (~2000–2400 rating), 9 agent configurations. Metric: pass@1 — binary ground truth, no rubric subjectivity.

The research was designed to find where the human framework transfers and where it breaks. The Phase 2 result is not a failure — it is a precise location of the boundary.

---

## Phase 1: Topology Determines Everything on Judgment Tasks

### Setup

32 worker agents were instantiated from the Kalibr framework. Each agent receives a system prompt (*constitution*) generated from 10 behavioral dimension scores. Agents were composed into teams under two topologies:

**Chain** — linear sequential handoff: A → B → C → END. Each agent builds on committed prior output and cannot reopen what a prior agent settled.

**Flat** — round-table: every agent speaks once per round for two rounds, with full conversation history from all prior speakers.

Four structured business scenarios were used: strategic product fork decisions, zero-sum resource allocation, post-mortem analysis, and crisis response. Each scenario has an explicit rubric with binary criteria. Judges evaluate only the team's final extracted deliverable — never the full transcript.

### Results

| Team Size | Chain | Flat | Δ |
|---|---|---|---|
| 1 agent | 15.3 | 31.2 | +15.9 |
| 2 agents | **57.6** | 10.7 | **−46.9** |
| 4 agents | 50.4 | 35.5 | −14.9 |
| 8 agents | 40.4 | 19.1 | −21.3 |
| 16 agents | 16.5 | — | — |

A chain of 2 agents (57.6) outperforms a flat swarm of 8 (19.1). Adding a second agent to a flat swarm dropped performance from 31.2 to 10.7 — active degradation, not inefficiency. The coordination tax of flat topology does not diminish as agents are added; it compounds.

Cross-model replication (Claude 3.5 Sonnet, drafted composition only):

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

100 CodeContests problems (Codeforces, difficulty 12–13, Div. 1 C/D). These are problems where naive algorithmic approaches fail and genuine mathematical insight is required. Pass@1: submitted code either solves all private test cases or it doesn't. No rubric, no judge.

Nine agent configurations across three experimental axes:

**Topology conditions:** chain-1/generic (baseline), chain-2/generic, chain-2/specialized (ALGORITHMIST → IMPLEMENTER)

**Option A — negative control:** extreme Kalibr dimension profiles (analytical, chaotic, founder) applied to a single SOLVER agent

**Option B — actual experiment:** same profiles applied to the ALGORITHMIST analyzer in a chain-2 setup, with a fixed neutral SOLVER as the second agent

All runs at temperature=0.0, Gemini 2.5 Flash, `thinking_budget=0`.

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

Chain-2 generic (16%) outperforms chain-1 (12%). The sequential forcing function works on deterministic mathematical execution — the same entropy-compression mechanism as Phase 1. Agent-1 produces a committed analysis pass; agent-2 generates code against a concrete prior state. This is the clean Phase 1 replication on a completely different task domain with objective measurement.

### Finding 2: Role Labels Introduce Cognitive Drag

The industry default for multi-agent coding pipelines is occupational identity: "You are a Senior Software Engineer. You are a Code Reviewer." Chain-2 specialized — ALGORITHMIST ("design the algorithm, do not write code") → IMPLEMENTER — scores 13% with 23 compilation errors, worse than the generic chain-2 on both metrics.

The mechanism is a two-agent version of the Moloch dynamic: the ALGORITHMIST is constitutionally compelled to be thorough and enumerate edge cases. The IMPLEMENTER is constitutionally compelled to request specificity before proceeding. These constraints interact: the ALGORITHMIST over-specifies (consuming tokens on abstraction); the IMPLEMENTER, receiving an abstract spec without runnable examples, produces code that fails on edge cases the spec described but did not demonstrate. The output that looks most complete is the least executable.

Chain-2 generic wins not because its agents are more capable, but because they are unconstrained by manufactured professional identities.

### Finding 3: Formatting Constraints Override Behavioral Constraints

The three extreme Kalibr profiles applied to a SOLVER agent cluster at 11–14%, statistically indistinguishable from the 12% baseline. This is the negative control result. The SOLVER role instruction is explicit: "your entire response must be a single ```python code block. No explanation, no analysis, no text outside the code block."

When this instruction is present, all behavioral dimension constraints encoded in the system prompt are overridden. A high-volatility agent simultaneously instructed to output only a code block outputs only a code block. This is not a failure of the psychometric framework. It is a precise identification of the conditions under which it operates. Behavioral dimensions require token space — room to reason, hesitate, and exhibit designated traits — to influence downstream logic.

### Finding 4: Dimension Effects Emerge When Token Space Exists

When the same extreme profiles are applied to the ALGORITHMIST analyzer in a chain-2 setup — where agent-1 has full token space to reason — the range is 10–14%. The 4-point spread versus the near-zero spread in Option A is directional evidence that dimensions manifest when given token space.

The founder profile (high drive alignment, low adaptive intelligence, low feedback orientation, low ambiguity tolerance) consistently performs worst: 10% pass@1, 23 compilation errors. The most rigid profile produces the most rigid algorithm specification, which generates the most broken code from the downstream SOLVER.

One confound is unresolved: Option B changed both the role (IMPLEMENTER → ALGORITHMIST) and the dimension profile simultaneously. A control condition — ALGORITHMIST with balanced dimensions — was not run. The role effect and the dimension effect are not cleanly separated.

---

## The Two-Domain Framework

Combined, the data supports a clean partition:

**Domain A — Exploratory, judgment-based, bounded convergence tasks** (strategic decisions, legal clause review, investment memos, post-mortem analysis): Flat topology generates Moloch — social engagement without task convergence. The fix is sequential chain topology, N=2, with Kalibr behavioral constraints tuned for dimensional compatibility. The 46-point topology gap measures the cost of ignoring this. Psychometric profiling of the analysis layer produces measurable effects.

**Domain B — Deterministic execution tasks** (code compilation, precise technical output with binary evaluation): Role-playing personas introduce cognitive drag. Elaborate psychometric profiles on the execution layer are inert at best (overridden by formatting constraints) and harmful at worst (produce abstract specs that increase compilation errors). The optimal architecture is chain-2 generic — sequential, minimal constitution, no occupational identity.

The enterprise AI industry applies one architecture to both domains. The data shows this produces a different failure mode in each:

- **On Domain A:** flat topology → Moloch → social cohesion without task convergence
- **On Domain B:** occupational role-playing → cognitive drag → translation loss at handoff

Two distinct failure modes. Same root cause: architectural defaults chosen for convenience rather than measured against task class.

---

## Practical Implications

For teams building multi-agent systems:

**1. Identify your task domain before choosing an architecture.** Judgment tasks and execution tasks are not the same problem. The correct architecture for a coding agent and the correct architecture for a strategic decision agent are different. Systems that apply identical orchestration to both are leaving performance on the table in both directions.

**2. Default to chain-2 with no elaborated personas for execution tasks.** The data shows generic sequential handoff (16% pass@1) outperforms specialized role separation (13%) on Codeforces Div. 1 problems. Stop writing "You are a Senior Python Engineer with 10 years of experience" — it actively degrades pass@1 and increases compilation error rates.

**3. Reserve psychometric profiling for the analysis layer on judgment tasks.** Profiles only produce measurable effects when agents have token space to reason. Applied to execution agents, they are noise. Applied to analysis agents with deliberate latitude, they produce directional behavioral differences.

**4. Keep teams small.** Size 2 chain (57.6) outperforms size 8 flat (19.1) on judgment tasks. For coding tasks, chain-2 generic is the ceiling of what was tested. The largest return is 1→2 agents. Returns diminish past 4.

**5. Add a synthesis node after any deliberation phase.** If exploration is needed, run a constrained deliberation round then route all output to a single synthesis agent. Deliberation without a convergence mechanism produces social cohesion and task failure.

---

## Combined Limitations

**Phase 1 — thin N:** 118 runs on 4 scenarios is enough for the topology finding to reach significance, but effect size confidence intervals are wide. Pre-registered replication with 300+ runs per topology per model is needed.

**Phase 2 — unresolved confound:** Option B changed role and dimension profile simultaneously. The ALGORITHMIST effect and the dimension effect are not cleanly separated. A balanced-dimension ALGORITHMIST control condition was not run.

**Phase 2 — small differences on N=100 binary outcomes:** 16% vs 13% is directional, not conclusive. The topology finding (chain-2 > chain-1) and the negative control clustering are the robust Phase 2 results.

**Model uniformity:** All agents within a run share the same underlying model. Behavioral constraints shift the output distribution but do not introduce genuine cognitive differences. A diverse human team has genuinely different cognitive architectures; a diverse agent team has different prompts on identical processing.

**Task scope:** Phase 1 covers 4 bounded judgment scenarios. Phase 2 covers 100 competitive programming problems from one source. Neither covers creative generation, open-ended research, or long-horizon planning. The two-domain framework is likely an N-domain framework — these are the first two domains measured.

---

## Open Questions

**Does the topology finding hold on generative tasks?** The N=2 ceiling and chain advantage were measured on convergence tasks. Brainstorming and open-ended research may favor flat topology precisely because they benefit from entropy. This is the most important boundary condition to test.

**Can the ALGORITHMIST confound in Option B be isolated?** Running ALGORITHMIST with balanced 75-baseline dimensions would separate the role effect from the dimension effect. Without this control, the Option B result is directional but not clean.

**Is flat topology a hallucination multiplier on adversarial input?** The social cohesion mechanism predicts that flat swarms will amplify a planted wrong hypothesis — agents will validate each other's acceptance of incorrect information — while a chain with committed first-pass will resist it. This is Phase 3.

**Does the topology finding hold with heterogeneous model families within a team?** Production systems often pair a large general model with smaller specialists. How topology interacts with within-team model heterogeneity is untested.

The full codebase, agent constitutions, scenarios, problem dataset, and evaluation harness are in the repository.

*This research was conducted independently, without institutional funding or affiliation.*

— Aryan S. | Independent AI Systems Research
