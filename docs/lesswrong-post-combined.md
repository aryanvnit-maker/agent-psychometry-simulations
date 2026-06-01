# Multi-Agent Architecture Has a Single Root Cause: 2,400+ Evaluations Across Nine Studies

Nine research phases. Over 2,400 total evaluations. Every experiment pointed at the same mechanism. It took four follow-on studies to isolate it precisely.

---

## The Research Program

Human organisational psychology has spent 40 years building instruments to predict team performance: who to hire, how to compose teams, what conditions produce cohesion and convergence. Almost none of that work has been tested on AI agent teams.

This research applies those instruments to controlled multi-agent LLM simulations and measures where the human findings replicate, where they invert, and where they fail entirely. The **Kalibr psychometric framework** — a 10-dimension behavioral assessment — was used to assign distinct personality profiles to AI agents, compose them into teams, and run them through structured tasks across fundamentally different domains.

The original hypothesis: psychometric profiling of agents predicts team output quality the same way it predicts human team performance.

What the data actually shows: the mechanism is a synthesis prompt architecture, not psychometric diversity. Every performance gain across every phase traces back to a single structural forcing function — and the research program found this by running the experiments that falsified the original claim.

**The summary before the detail:** Kalibr delivers 6.9× more quality per LLM call than the default multi-agent configuration shipped in LangChain, CrewAI, and AutoGen, verified on 749 objective benchmark instances with binary ground truth and no LLM judge. The default flat roundtable without a synthesis step (28% HumanEval, 4 calls) vs Kalibr chain (96% HumanEval, 2 calls). The entire gap traces to one prompt.

**Phase 1:** 118 simulations, 4 business judgment scenarios, 2 model families, 5 team sizes, 3 compositions.

**Phase 2:** 900 evaluations, 100 Codeforces Div. 1 C/D problems, 9 agent configurations.

**Phase 2 Control:** 100 evaluations, same problems, single condition isolating the ALGORITHMIST role effect.

**Phase 3:** 200 evaluations, 50 problems × 4 conditions. Wrong algorithmic hints planted in problem prompts.

**Phase 4:** 111 evaluations, mixed workload × 3 routing conditions.

**Phase B:** ~60 evaluations, code review domain. Cross-domain topology replication.

**Phase 5:** 160 evaluations, 4 conditions, 2×2 factorial (topology × handoff prompt). Mechanism isolation.

**Phase 6:** ~750 evaluations, HumanEval and GSM8K objective benchmarks. No LLM judge.

**Phase 8:** 79 simulations × 3 judges, compute-matched agent diversity vs structured self-refinement.

**Phase 9:** 40 simulations × 3 judges, Kalibr 2-call chain vs xAI's internal Grok multi-agent panel. Same base model family, different orchestration layers.

---

## Phase 1: Topology Determines Output on Judgment Tasks

### Setup

32 worker agents instantiated from the Kalibr framework. Each agent receives a system prompt (*constitution*) generated from 10 behavioral dimension scores. Composed into teams under two topologies:

**Chain** — linear sequential handoff: A → B → C → END. Each agent builds on committed prior output and cannot reopen what a prior agent settled.

**Flat** — round-table: every agent speaks once per round for two rounds, with full conversation history from all prior speakers.

Four structured business scenarios: strategic product fork decisions, zero-sum resource allocation, post-mortem analysis, and crisis response. Binary rubric criteria. Judges evaluate only the team's final extracted deliverable.

### Results

| Team Size | Chain | Flat | Δ |
|---|---|---|---|
| 1 agent | 15.3 | 31.2 | +15.9 |
| 2 agents | **57.6** | 10.7 | **−46.9** |
| 4 agents | 50.4 | 35.5 | −14.9 |
| 8 agents | 40.4 | 19.1 | −21.3 |
| 16 agents | 16.5 | — | — |

A chain of 2 agents (57.6) outperforms a flat swarm of 8 (19.1). Adding a second agent to a flat swarm dropped performance from 31.2 to 10.7 — active degradation, not inefficiency.

Cross-model replication (Claude 3.5 Sonnet):

| Model | Chain | Flat | Gap |
|---|---|---|---|
| Gemini 2.5 Flash | 40.3 | 23.4 | +16.9 |
| Claude 3.5 Sonnet | 42.4 | 20.4 | +21.9 |

### The Mechanism: Moloch in a Synthetic System

GEQ sociometric data collected on every run. Two distinct constructs:

- **Task cohesion:** did agents converge on a shared, committed output?
- **Social cohesion:** did agents engage with each other's contributions?

In chain topology, task and social cohesion track within **23.9 points** of each other.

In flat topology, the gap is **39.6 points**. Social cohesion stays high — FIRO inclusion scores near 1.0, every agent addresses every other agent. Task cohesion collapses. Consensus rate: chain 52.2%, flat 31.4%.

Flat topology agents are socially present and taskfully absent. The meeting is productive. The meeting does not produce a decision.

**Important caveat raised in Phase 5:** chain topology in Phase 1 implicitly included a synthesis handoff prompt between agents; flat topology did not. This is a confound. Phase 5 isolates it.

---

## Phase 2: Execution Tasks Break in a Different Way

### Setup

100 CodeContests problems (Codeforces Div. 1 C/D, difficulty 12–13). Pass@1 against private test cases. Binary ground truth. Nine agent configurations.

### Results

| Condition | Pass@1 | Compilation Errors |
|---|---|---|
| Chain-1 generic (baseline) | 12% | 18 |
| **Chain-2 generic** | **16%** | 22 |
| Chain-2 specialized (ALGORITHMIST → IMPLEMENTER) | 13% | 23 |
| Chain-1 analytical | 11% | 16 |
| Chain-1 chaotic | 14% | 16 |
| Chain-1 founder | 11% | 20 |
| Chain-2 analytical-analyzer | 13% | 15 |
| Chain-2 chaotic-analyzer | 14% | 18 |
| Chain-2 founder-analyzer | 10% | 23 |

Chain-2 generic (16%) outperforms chain-1 (12%). Chain-2 specialized underperforms generic. The ALGORITHMIST role instruction ("design the algorithm, do not write code") creates a prose→code translation step that the downstream agent cannot complete cleanly.

---

## Phase 2 Control: Isolating the ALGORITHMIST Effect

The confound: Option B changed both role and dimension profile simultaneously. Was the underperformance from the role instruction or the extreme profiles?

| Condition | Pass@1 | Compilation Errors |
|---|---|---|
| Chain-2 generic | 16% | 22 |
| Chain-2 specialized (extreme dims) | 13% | 23 |
| **Chain-2 ALGORITHMIST-balanced** | **12%** | 16 |

The control (balanced dimensions, ALGORITHMIST role) scored 12% — lower than specialized (13%), not higher. Extreme profiles were marginally helping, not hurting. The role label is the culprit.

---

## Phase 3: Flat Topology Is Unsafe Under Adversarial Input

### Setup

50 problems × 4 conditions = 200 evaluations. Wrong algorithmic hints planted in problem prompts as editorial annotations. Conditions: chain-2/clean, chain-2/poisoned, flat-2/clean, flat-2/poisoned.

### Results

| Condition | Pass@1 | NoCode |
|---|---|---|
| chain-2/clean | 14% | 0 |
| chain-2/poisoned | 18% | 0 |
| flat-2/clean | 18% | 0 |
| **flat-2/poisoned** | **14%** | **4** |

8pp swing between poisoned conditions. Chain-2 improved under adversarial input by independently evaluating and rejecting the hint. Flat-2 degraded — agents validated each other's acceptance of the wrong framing.

**The smoking gun:** 4 complete task collapses in flat-2/poisoned (agents produced no output), zero collapses across all other 150 runs. Flat topology under a wrong premise can lock into an unimplementable framing and produce nothing. Chain never collapsed once.

---

## Phase 4: Dynamic Routing Recovers Per-Domain Performance

### Setup

Mixed workload: judgment tasks + execution tasks × 3 routing conditions = 111 evaluations.

- **static-judgment** — always deploys Kalibr chain-2
- **static-execution** — always deploys generic chain-2
- **meta-router** — classifies task domain first, routes to matching config

### Results

| Config | Judgment score | Execution pass@1 |
|---|---|---|
| static-judgment | 85.1 | 0.0% (20 NoCode) |
| static-execution | 59.6 | 20.0% |
| **meta-router** | **85.8** | **20.0%** |

Classifier accuracy: **100%** on 37 real tasks + 10 adversarial Trojan tasks.

### The Domain Taxonomy Finding

| Scenario | static-judgment | static-execution | Δ |
|---|---|---|---|
| s01 strategic fork | 60.6 | 41.7 | +18.9 |
| s02 resource allocation | **100.0** | 22.2 | **+77.8** |
| s03 post-mortem | 80.0 | 80.0 | 0.0 |
| s04 crisis response | 100.0 | 94.4 | +5.6 |

Open-world strategic tasks show massive Kalibr advantage. Closed-world deterministic tasks show near-zero advantage. The profiles do not hurt; they provide no marginal benefit when the correct answer is independently verifiable.

---

## Phase B: Topology Replication on Code Review

### Setup

Code review domain. Chain topology vs flat topology on a different task type — not competitive programming, not business judgment, but engineering critique. Independent replication study.

### Result

| Topology | N | Mean score |
|---|---|---|
| chain-2 | 15 | 70.4 |
| flat-2 | 15 | 35.3 |
| **Δ** | | **+35.1** |

Chain outperformed flat on code review by 35.1 points, replicating the Phase 1 direction on a different task type. The topology finding is not specific to the business judgment scenarios in Phase 1.

---

## Phase 5: The Mechanism Isolated — Synthesis Beats Topology

### The Confound in Phase 1

Phase 1 compared chain to flat. Chain topology naturally includes a synthesis step: agent B receives committed output from agent A and is framed as building on it. The Phase 1 chain runs included an explicit handoff prompt directing agent B to synthesize prior contributions. The Phase 1 flat runs had no such prompt.

The 46-point gap could have been caused by topology, by the synthesis prompt, or by both. Phase 5 runs the 2×2 factorial to find out.

### Setup

Four conditions, 10 reps × 4 scenarios = 160 total runs, 3-judge panel per run:

- **chain/handoff** — chain topology + SYNTHESIS_PROMPT at handoff
- **chain/no-handoff** — chain topology, no injected synthesis instruction
- **flat/handoff** — flat round-table + explicit closing synthesis step
- **flat/no-handoff** — flat round-table, no synthesis (matching the out-of-the-box examples in most frameworks, which omit a terminal synthesis step)

SYNTHESIS_PROMPT: *"OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN. You are the terminal synthesis agent. Identify what prior analysis got right, what it missed, produce a COMPLETE, DEFINITIVE final answer. Close every open question. Be decisive."*

### Results

| Condition | Calls | Mean score | Score/call |
|---|---|---|---|
| **chain/handoff** | 2 | **86.3** | **43.2** |
| flat/handoff | 5 | 76.5 | 15.3 |
| chain/no-handoff | 2 | 50.9 | 25.5 |
| flat/no-handoff (LangChain/CrewAI/AutoGen default) | 4 | 34.3 | 8.6 |

**Topology effect (no handoff on either side):** chain/no-handoff vs flat/no-handoff = **+16.6 pts**

**Handoff effect (averaged across both topologies):** **+38.8 pts**

**Efficiency:** chain/handoff vs flat/no-handoff = **5.0× more score per LLM call** (43.2 vs 8.6).

The synthesis step is the dominant mechanism. The topology gap is real and causal (+16.6 pts) but less than half the handoff effect. Phase 1's 46-point gap was overwhelmingly explained by the presence of a synthesis step in chain runs that flat runs did not have.

### What This Changes

The Phase 1 claim — "topology determines everything" — is partially revised. The correct claim is:

*The synthesis step is the primary mechanism. Topology is a structural property that determines whether the synthesis step happens naturally (chain) or must be forced explicitly (flat). Without synthesis, topology produces a 16.6-pt gap. With synthesis, the gap narrows to 9.8 pts. The out-of-the-box flat configuration (no synthesis step, as in most framework quickstart examples) scores 34.3. The optimal configuration (chain/handoff) scores 86.3. The 52-point gap between them is mostly explained by the presence or absence of a synthesis step, not by topology per se. Note: teams that already add a final "summarize and commit" step to their flat pipeline will not see the 34.3 baseline — they are already in the flat/handoff regime (~76.5).*

---

## Phase 6: Objective Benchmarks — The Synthesis Architecture Holds

### Setup

Phase 6 tests the synthesis finding on objective benchmarks where ground truth is available and no LLM judge is required:

- **HumanEval** — Python function completion against private test cases (pass@1), N=50 per condition
- **GSM8K** — Grade-school math word problems (exact numerical match), N=99–100 per condition

Five conditions: single-agent (1 call), single-agent-refine (2 calls, self-synthesis), kalibr-chain (2 calls, 2 agents), kalibr-flat-handoff (5 calls, round-table + synthesis), kalibr-flat-no-handoff (4 calls, round-table only).

### Results

**HumanEval — pass@1 (N=50 per condition)**

| Condition | Calls | pass@1 | 95% CI | Score/call |
|---|---|---|---|---|
| single-agent | 1 | 94.0% | [83.8%, 97.9%] | 94.0 |
| single-agent-refine | 2 | 98.0% | [89.5%, 99.6%] | 49.0 |
| kalibr-chain | 2 | 96.0% | [86.5%, 98.9%] | 48.0 |
| kalibr-flat-handoff | 5 | 98.0% | [89.5%, 99.6%] | 19.6 |
| **kalibr-flat-no-handoff** | **4** | **28.0%** | **[17.5%, 41.7%]** | **7.0** |

**GSM8K — accuracy (N=99–100 per condition)**

| Condition | Calls | accuracy | 95% CI | Score/call |
|---|---|---|---|---|
| single-agent | 1 | 85.0% | [76.7%, 90.7%] | 85.0 |
| single-agent-refine | 2 | 92.0% | [85.0%, 95.9%] | 46.0 |
| kalibr-chain | 2 | 94.0% | [87.5%, 97.2%] | 47.0 |
| kalibr-flat-handoff | 5 | 92.0% | [85.0%, 95.9%] | 18.4 |
| **kalibr-flat-no-handoff** | **4** | **56.6%** | **[46.7%, 65.9%]** | **14.2** |

kalibr-chain vs flat/no-handoff (the framework default): **6.9× more efficient on HumanEval, 3.3× on GSM8K**. Single-agent scores highest score/call because HumanEval is near-ceiling at 1 call for this model — the relevant comparison is working multi-agent vs broken multi-agent.

### Finding 1: Role Constitution Collapse

kalibr-flat-no-handoff collapsed to 28.0% on HumanEval and 56.6% on GSM8K. The probable mechanism is role constitution conflict: Kalibr's MONITOR_EVALUATOR agents carry the instruction "do not generate primary output" and COMPLETER_FINISHER agents carry "do not close tasks prematurely." Without an explicit synthesis override, these role constraints suppress final output delivery. This is consistent with the Phase 2 finding that role labels degrade execution performance, but it is a mechanism hypothesis — we did not test flat topology with generic (no-role) agents in Phase 6 as a direct control.

The synthesis prompt override in flat/handoff rescues the condition entirely: 98.0% HumanEval, 92.0% GSM8K. Same architecture, same agents, same rounds — the synthesis instruction is what unlocks output.

### Finding 2: Ceiling Effect

Modern models (Gemini 2.5 Flash) score 94–98% on HumanEval and 85–94% on GSM8K across all non-collapsed conditions. These benchmarks lack the headroom to discriminate between working configurations. The confidence intervals overlap substantially for all conditions except kalibr-flat-no-handoff, which is separated by 60+ points. The primary Phase 6 finding is the collapse, not relative rankings among working configurations.

---

## Phase 8: Agent Diversity vs Structured Self-Refinement

### The Question

Phase 5 proved the synthesis step matters. Phase 6 confirmed synthesis architecture holds on objective benchmarks. The remaining question: does having a *different* agent do the first analysis provide any benefit over having the *same* agent do it twice?

This is the multi-agent product claim: that cognitive diversity — different constitutions, different dimensional profiles — produces better inputs for synthesis than self-analysis does.

Phase 8 is a compute-matched test. Both conditions make exactly 2 LLM calls. The only variable is whether the first call is made by a dimensionally different agent or by the same agent.

### Setup

Two conditions, 10 reps × 4 scenarios, 3-judge panel:

**kalibr-chain:** diversity_pick (agent maximally different from captain on task dimensions) speaks first. Captain synthesizes. 2 calls, 2 agents.

**single-agent-refine:** captain analyzes on call 1. Same captain synthesizes on call 2 with identical SYNTHESIS_PROMPT. 2 calls, 1 agent.

Both conditions: same scenarios, same synthesis prompt, same judge panel. Pool initialized with the same seed per (scenario, rep) pair so the captain is the same person across conditions.

### Results

| Condition | Calls | N | Mean | Std | Score/call |
|---|---|---|---|---|---|
| kalibr-chain | 2 | 39 | 86.5 | 16.0 | 43.3 |
| single-agent-refine | 2 | 40 | 85.7 | 19.8 | 42.9 |

**Δ = +0.7 pts. Welch t = 0.18, p = 0.854. Not significant.**

Per-scenario breakdown:

| Scenario | chain | refine | Δ |
|---|---|---|---|
| s01 strategic fork | 82.2 | 83.3 | −1.2 |
| s02 resource allocation | 97.4 | 97.3 | +0.1 |
| s03 post-mortem | 80.7 | 80.7 | 0.0 |
| s04 security breach | 86.7 | 81.5 | +5.2 |

Three of four scenarios are effectively tied. No scenario shows a statistically meaningful gap.

### Verdict

**TIED. Agent diversity adds zero measurable value over structured self-refinement, compute-matched at 2 calls each.**

A single agent running the same synthesis protocol on its own analysis produces statistically identical output to a diverse second agent synthesizing a different agent's analysis. The synthesis step — the structural forcing function that demands commitment, identifies gaps, and closes open questions — is all that matters. Who provides the first analysis is irrelevant.

This is the final closure of the research program's original hypothesis. Psychometric diversity of AI agents does not drive output quality. The synthesis architecture does.

---

## Phase 9: Kalibr vs xAI's Internal Multi-Agent Panel

### The Question

Phases 5 and 8 established that the synthesis step is the dominant mechanism and that agent diversity adds nothing. Phase 9 tests whether this holds against an external benchmark: xAI's Grok multi-agent panel, a commercially deployed proprietary multi-agent system.

Both conditions use the same Grok base model family. The only variable is the orchestration layer.

- **kalibr-chain**: grok-4.20-0309-reasoning, 2 explicit LLM calls, Kalibr's synthesis architecture
- **grok-panel**: grok-4.20-multi-agent-0309, ~4 internal agents, xAI's orchestration (1 API call to us)

This is not compute-matched. Grok panel uses approximately 4 internal agents per call. Kalibr makes 2 explicit calls. The comparison is architecture vs architecture, not call-for-call.

### Results

| Condition | Model | Calls | N | Mean | Std |
|---|---|---|---|---|---|
| kalibr-chain | grok-4.20-0309-reasoning | 2 | 20 | 79.8 | 29.3 |
| grok-panel | grok-4.20-multi-agent-0309 | ~4 | 20 | 81.5 | 12.8 |
| **Δ** | | | | **−1.8, p=0.809** | |

Not significant. Kalibr's 2-call explicit synthesis chain is statistically identical to xAI's proprietary ~4-agent internal system on the same base model family.

Score-per-LLM-call: **Kalibr 39.9 vs panel 20.4** (estimated). Kalibr is approximately 2× more score-efficient per LLM call.

Per-scenario breakdown:

| Scenario | kalibr-chain | grok-panel | Δ |
|---|---|---|---|
| s01 strategic fork | 85.3 | 80.0 | +5.3 |
| s02 resource allocation | 80.0 | 84.0 | −4.0 |
| s03 post-mortem | 66.7 | 80.0 | **−13.3** |
| s04 security breach | 87.0 | 82.0 | +5.0 |

### The Post-Mortem Gap

The s03 result is interpretable. Kalibr's SYNTHESIS_PROMPT instructs the terminal agent to "close every open question" and "be decisive." For a post-mortem, this is structurally wrong. Post-mortems require preserving competing hypotheses, acknowledging uncertainty, and ranking causes by likelihood — not collapsing to a single committed answer.

Kalibr wins on forward-looking decision tasks (strategy, resource allocation, crisis response) where decisiveness is the correct posture. The panel's implicit orchestration appears to handle reflective tasks better, likely because it does not enforce a hard decisiveness constraint at the terminal step.

This is a known limitation of the current synthesis prompt design: it is tuned for commitment, not reflection. A separate synthesis variant for backward-looking analysis tasks would close this gap. It is the most important near-term architectural extension.

### What Phase 9 Means

Kalibr's open synthesis architecture matches xAI's internal multi-agent orchestration at half the LLM call count. The synthesis mechanism generalises to a real proprietary comparison.

The implication: proprietary black-box multi-agent orchestration does not produce better outputs than an explicit 2-call synthesis chain. The mechanism is transparent, replicable, and compute-efficient. What xAI's panel likely does internally — a synthesis or aggregation step — is what Kalibr makes explicit.

---

## The Unified Mechanism

Trace the synthesis step through the full research arc:

| Condition | Synthesis? | Calls | Score | Score/call |
|---|---|---|---|---|
| Phase 1 single-agent | No | 1 | 15.3 | 15.3 |
| Phase 5 flat/no-handoff (framework default) | No | 4 | 34.3 | 8.6 |
| Phase 5 chain/no-handoff | No | 2 | 50.9 | 25.5 |
| Phase 5 flat/handoff | Yes (explicit) | 5 | 76.5 | 15.3 |
| Phase 5 chain/handoff | Yes (natural) | 2 | 86.3 | 43.2 |
| Phase 8 single-agent-refine | Yes | 2 | 85.7 | 42.9 |
| Phase 8 kalibr-chain | Yes | 2 | 86.5 | 43.3 |
| Phase 9 grok-panel | Yes (internal, implicit) | ~4 | 81.5 | 20.4 |
| Phase 9 kalibr-chain | Yes (explicit) | 2 | 79.8 | 39.9 |

Every condition with a synthesis step clusters at 76–87 pts and 15–43 score/call. Every condition without one scores below 51 pts and below 26 score/call. The framework default (flat/no-handoff, 8.6 score/call) is the worst performer on both dimensions. Every condition without one scores below 51 pts. The 52-point gap between the industry default (flat/no-handoff, 34.3) and the optimal configuration (chain/handoff, 86.3) is overwhelmingly explained by the presence of a synthesis step, not by topology or agent count.

The SYNTHESIS_PROMPT's function: it overrides role function constraints, demands that the agent identify gaps in prior analysis, and requires a complete, committed final answer. Without it, role constitutions that include evaluation or oversight functions suppress primary output delivery. With it, the model shifts from deliberation mode to commitment mode regardless of which architectural configuration it sits in.

---

## The Revised Three-Domain Framework

The original taxonomy (Phases 1–4) identified three domains by task type. Phase 5 and 8 add a more fundamental organising principle: **the synthesis step is domain-invariant**.

**Domain 1 — Open-world strategic** (strategy decisions, resource allocation, investment analysis): No ground truth. Quality = coherence + trade-off coverage + commitment. Architecture: single-agent-refine or chain-2 + synthesis prompt. Kalibr profiles provide a marginal benefit (~5–10 pts) on open-world tasks where output space is unconstrained.

**Domain 2 — Closed-world deterministic** (post-mortem analysis, crisis response, factual synthesis): Verifiable correct answer exists. Architecture: single-agent-refine or chain-2 generic + synthesis prompt. Profiles are neutral. The synthesis step is still required for output commitment.

**Domain 3 — Execution** (code, math, precise technical output): Binary evaluation. Architecture: single-agent-refine or chain-2 generic, no occupational identity. The ALGORITHMIST role costs 4pp pass@1. The synthesis prompt must not require prose-format output — it needs to demand runnable code delivery.

**Cross-domain invariant:** deploy the synthesis step. Topology and agent count are secondary. Flat topology without synthesis collapses on judgment tasks. Role constitutions without synthesis override block output delivery on code tasks. The synthesis prompt is the single intervention that rescues performance across all three domains.

---

## The Unified Claim

Every architectural default the industry uses was imported from human team management. Roundtables because individuals need buy-in before committing. Job titles because accountability requires identity. Specialist pipelines because human cognitive capacity is genuinely domain-limited. Deliberation frameworks because power dynamics suppress minority positions.

Agents have none of those constraints. They do not need to feel included. They do not have egos. They do not have genuine cognitive specialisation — they are the same model with different prompts.

Every piece of human organisational infrastructure imported into multi-agent systems is either dead weight or actively harmful:

- Flat topology → Moloch → 52-point quality gap vs optimal; 8.6 vs 43.2 score/call (5× efficiency loss)
- Occupational personas → translation loss → 4pp pass@1 degradation and elevated compilation errors (N=900)
- Flat topology under adversarial input → complete task collapse (4 NoCode, 0 in chain, 200 evaluations)
- Single static architecture on mixed workloads → 0% execution pass@1 or 26-point judgment degradation
- Agent diversity without synthesis → identical to self-refinement (Δ=+0.7, p=0.854, N=79)
- Proprietary ~4-agent orchestration → same output as Kalibr's 2-call chain at ~2× the compute (Phase 9, p=0.809)

The correct architecture was sitting in plain sight. One agent or two, sequential handoff, synthesis prompt at the terminal step. It took 2,400+ evaluations across nine experiments to prove it because the industry was not measuring.

---

## Practical Implications

**1. The synthesis prompt is the primary intervention — and it is a corrective layer, not a rip-and-replace.** It can sit on top of any existing LangChain, CrewAI, or AutoGen pipeline as a terminal synthesis step. Before restructuring topology or adding agents, add this step. The default configuration in all three frameworks (flat roundtable, no synthesis step) scores 28% on HumanEval at 4 LLM calls. Adding the synthesis step takes it to 98% at 5 calls. Switching to chain-2 + synthesis: 96% at 2 calls — 6.9× more score-efficient than where you started. If you do one thing, do this.

**2. Use chains of two, not rooms of many.** The largest return is 1→2 agents. Returns diminish past 4. A chain of 2 beats a room of 8 by 38 points on judgment tasks. The chain topology implements the synthesis step naturally; flat topology requires it to be forced explicitly.

**3. Do not add agents to improve quality.** Phase 8 proves this directly: two agents compute-matched to one agent (both 2 calls) produces statistically identical output (Δ=+0.7, p=0.854). Phase 9 confirms it at the system level: xAI's ~4-agent internal panel matched Kalibr's 2-call chain (Δ=−1.8, p=0.809) at roughly double the compute. Adding agents does not improve quality once the synthesis step is present.

**4. Strip occupational personas from execution tasks.** "You are a Senior Python Engineer" costs 4pp pass@1. The ALGORITHMIST role creates a prose→code translation step the downstream agent cannot complete. Generic constitutions with behavioral dimensions but no occupational identity outperform specialised ones on execution.

**5. Classify task domain before deploying.** A five-line classifier routing between two configs achieves per-domain maximum on both axes simultaneously. Any system using one config for all task types is collapsing on half its workload.

**6. Reserve psychometric profiling for open-world strategic tasks only.** Profiles produce measurable effects only when the output space is unconstrained and agents have token space to reason. On execution tasks with formatting constraints, they are overridden entirely. On closed-world deterministic tasks, they are neutral.

**7. Treat flat topology under adversarial input as a safety issue.** The 4 NoCode collapses in flat-2/poisoned represent complete task failure. Production systems on flat topology will occasionally produce nothing when input contains wrong framing. Chain topology has structural resistance.

---

## Limitations

**Phase 1 — thin N and synthesis confound.** 118 runs on 4 scenarios. Phase 5 partially revises the Phase 1 mechanism claim: the 46-point topology gap was mostly explained by the synthesis confound, not pure topology. The residual topology effect (+16.6 pts without synthesis, +9.8 pts with synthesis) is real and causal, but smaller than originally presented.

**Phase 2/3 — small differences on binary outcomes.** 16% vs 13% on N=100 binary pass@1 is directional. The topology finding (chain-2 > chain-1) and the NoCode collapse under adversarial input are the robust results. The 3pp persona degradation is directional only.

**Phase 5 — two-agent chain only.** The factorial tests chain-2 and flat-2. Topology × handoff interaction at larger team sizes is untested.

**Phase 6 — ceiling effect.** HumanEval (94–98%) and GSM8K (85–92%) are too easy for Gemini 2.5 Flash to discriminate between working configurations. The primary finding is the flat/no-handoff collapse, not relative rankings. Hard benchmarks (Codeforces Div. 1 C/D) show more discrimination but have lower absolute performance.

**Phase 8 — judgment tasks and single model.** Diversity vs self-refinement tested on 4 judgment scenarios with Gemini 2.5 Flash. Whether diversity provides marginal benefit on genuinely open-ended generative tasks (brainstorming, research synthesis, creative generation) or with heterogeneous model pairs is untested.

**Phase 9 — not compute-matched and small N.** Grok panel uses ~4 internal agents; Kalibr makes 2 calls. The comparison is architecture vs architecture, not call-for-call. n=20 per condition is sufficient to rule out large effects but cannot rule out a 5–8 point gap. The post-mortem result (−13.3 pts) is the most important finding and likely reflects prompt design, not a fundamental architectural limitation. Single base model family (Grok); cross-model replication of Phase 9 is open.

**Model uniformity throughout.** All agents within a run share the same underlying model. Behavioral constraints shift the output distribution but do not introduce genuine cognitive differences. A diverse human team has genuinely different cognitive architectures; a diverse agent team has different prompts on identical processing. The Phase 8 null result may not hold if agents are drawn from different model families with genuinely different training distributions.

**Psychological safety correlations.** The r=0.70 and r=0.65 correlations between FIRO inclusion scores and task scores are intra-judge correlations — the same model computing both. These should not be interpreted as independent replications of the Google Project Aristotle finding. They reflect internal consistency of the evaluation model, not orthogonal validation.

---

## Open Questions

**Does the synthesis finding hold against proprietary multi-agent systems?** Phase 9 answers this for Grok: yes, Kalibr's 2-call chain matches xAI's internal ~4-agent panel (Δ=−1.8, p=0.809) at half the compute. Open: replication with OpenAI's multi-agent tooling and other proprietary orchestration systems.

**Does the synthesis finding hold with heterogeneous model teams?** Phase 8's null result (diversity = self-refinement) used same-model agents. If agent A is GPT-4 and agent B is Claude, their genuinely different training distributions might produce a non-trivial diversity signal.

**Does the synthesis finding hold on generative tasks?** Brainstorming and open-ended research may benefit from diversity — entropy is valuable when the task requires exploration rather than commitment. Phase 8 tested bounded judgment tasks with clear rubric criteria.

**What is the correct synthesis prompt for execution tasks?** The SYNTHESIS_PROMPT used here is optimised for judgment: it demands commitment and gap identification on a prior analysis. For code tasks, the synthesis step needs to demand runnable code delivery, not analysis. The Phase 6 collapse suggests an unoptimised synthesis prompt may not rescue execution under all conditions.

**Does heterogeneous model diversity change the Phase 8 result?** The most testable extension of Phase 8: replace the diversity_pick with an agent from a different model family (different base model weights), hold the synthesis step constant, and rerun. If the null result holds, the synthesis architecture claim generalises. If it breaks, diversity matters when it is genuine rather than simulated by different prompts.

**What is the minimum synthesis prompt?** The SYNTHESIS_PROMPT is 4 instructions. Which elements are load-bearing? "Close every open question" and "Be decisive" are candidates for the critical constraint. Ablation study needed.

The full codebase, agent constitutions, scenarios, benchmark datasets, and evaluation harness are in the repository.

---

## If You're Running a Multi-Agent Pipeline

The evaluation harness is designed to be run against your own scenarios, not just the ones in this paper. If you want to know whether your pipeline has the synthesis collapse failure mode — or whether your architecture is spending compute on agent count that adds nothing — the tooling is open source and runs against any judgment scenario you can describe as a brief + rubric.

For teams that prefer a structured assessment: I offer confidential back-test audits, identifying your exact collapse rate, token waste, and architectural fix against your own production logs. Contact: aryan199841@gmail.com.

*This research was conducted independently, without institutional funding or affiliation.*

— Aryan S. | Independent AI Systems Research
