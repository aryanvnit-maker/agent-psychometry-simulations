# The Synthesis Bottleneck: A Single Structural Mechanism Governs Multi-Agent LLM Performance, Adversarial Conformity, and Epistemic Robustness

**Author:** Aryan Shah (Independent Researcher)
**Contact:** aryan199841@gmail.com
**Repository:** https://github.com/aryanvnit-maker/agent-psychometry-simulations
**Status:** Working draft, prepared for arXiv submission (cs.MA / cs.AI / cs.CL)
**Version:** 0.1 — 2026

---

## Abstract

We report a research program of 2,400+ evaluations across eleven experimental phases investigating what determines output quality in multi-agent large language model (LLM) systems. The program began from a hypothesis imported from organizational psychology — that psychometric diversity among agents predicts team performance, as it does in human teams — and falsified it. Across every phase, injected personality diversity between agents produced no reliable performance benefit (Phase 8: Δ = +0.7 points, p = 0.854, N = 79, compute-matched). Instead, a single structural intervention explains the overwhelming majority of variance: a terminal **synthesis step** that forces an agent to commit to a complete, decisive final answer rather than continuing open-ended deliberation. Without it, the default flat round-table topology shipped in common multi-agent frameworks scores 34.3/100 on structured judgment tasks and collapses to 28% pass@1 on HumanEval (vs. 94-98% for every non-collapsed configuration); with it, the same topology reaches 76.5-98%. Sequential chain topology implements this synthesis step naturally; flat topology requires it to be added explicitly. We further show that under adversarial input — a confidently-framed false premise planted in the task — flat topology does not merely underperform but actively amplifies the falsehood via a multi-agent conformity cascade structurally analogous to the Asch effect, while chain topology's independent-re-derivation structure resists it (Phase 3: 4/50 complete task collapses in poisoned flat runs vs. 0/150 in all other conditions). We then extend this adversarial-robustness paradigm from code tasks with binary ground truth to genuinely contested epistemic questions with no ground truth (COVID-19 origins, LHC black-hole risk, dietary cholesterol and cardiovascular disease), where we cannot score conclusions but can score structural robustness: does the architecture resist a planted falsehood, maintain calibrated uncertainty, and flag its own correlated evidence. On three poisoned variants of a contested nutrition question, chain topology resisted conformity in 28/30 runs against flat's 15/30 (pooled across two model families, Fisher's exact p < 0.001), and we re-ground this result on deterministic, LLM-free structural checks to remove the circularity of an LLM judging an LLM. We report where this generalizes and where it does not: the conformity-resistance effect replicates across model families and on a held-out contested question outside the original tuning set, while the original code-domain collapse signature does not replicate on a stronger coder, indicating the durable phenomenon is *deference to false premises*, not *output collapse*. We close with a formal specification for a proposed extension — ranking competing causal decompositions of a question by adversarial robustness rather than asserted truth — and an explicit tractability critique of our own proposal.

---

## 1. Introduction

Multi-agent LLM systems are widely deployed on the premise that more agents, structured as specialized roles engaging in deliberation, produce better outputs than a single model call. This premise is inherited, largely uncritically, from human organizational science: teams of specialists outperform generalists, diverse perspectives improve decisions, and round-table deliberation surfaces better answers than any individual's first draft. Popular multi-agent frameworks (LangChain, CrewAI, AutoGen) default to exactly this shape — multiple role-labeled agents in a shared conversational space, iterating toward a decision.

We set out to test whether decades of validated human-team psychometric instruments — group cohesion, personality-based role composition, sociometric assessment — would transfer to LLM agent teams the way they transfer, imperfectly but usefully, across different human populations. We built a framework (**Kalibr**) that assigns each agent a ten-dimension behavioral profile, injected as a system-prompt constraint, and composes agents into teams via a draft mechanic modeled on Belbin team-role theory. We then ran this framework through nine independent experimental phases spanning business judgment tasks, competitive programming, code review, and objective machine-graded benchmarks.

The headline finding is not the one we set out to find. **Agent personality diversity does not reliably improve output quality.** What does is a single structural intervention we call the **synthesis step**: an explicit instruction, delivered to the terminal agent in a pipeline, to stop deliberating and produce a complete, committed answer. This single intervention explains a 52-point performance gap (34.3 → 86.3 on our judgment rubric) and a 6.9× gain in benchmark accuracy per LLM call (28% → 96% pass@1 on HumanEval, at fewer calls). Whether the team has one agent or eight, whether it is topologically flat or chained, whether the agents are diverse or identical — the presence or absence of a forced synthesis step is the dominant determinant of output quality.

This finding has a second, sharper edge. Under **adversarial input** — a confidently stated but false premise embedded in the task — the failure mode of flat, synthesis-less multi-agent topology is not merely lower quality. It is **conformity to the falsehood**: agents in a shared deliberative space ratify each other's acceptance of a wrong premise, occasionally to the point of producing no usable output at all. Sequential (chain) topology, in which each agent independently re-derives an answer from the task rather than reading and ratifying a group consensus, resists this failure mode. This is the LLM multi-agent analog of the Asch conformity effect (Asch, 1951) and is continuous with the broader literature on sycophancy in instruction-tuned language models (Perez et al., 2022; Sharma et al., 2023): social agreement, once established in a shared context, is difficult for a model to contradict even when it possesses the information needed to do so.

The second half of this paper extends that adversarial-robustness result from a domain with objective, machine-checkable ground truth (competitive programming) to domains with **no ground truth at all**: contested scientific and empirical questions of the kind a real epistemic-assistance tool must handle — the origins of COVID-19, whether the Large Hadron Collider poses an existential risk, and whether dietary cholesterol from eggs increases cardiovascular disease risk. On these questions we cannot score whether an architecture's *conclusion* is correct. We can score whether the architecture is *robust*: whether it resists a planted falsehood, maintains calibrated uncertainty under pressure to overstate confidence, and flags evidence dependencies that a naive reading would miss. We report this second study in full, including a deliberate effort to remove the circularity inherent in using one LLM to judge another's epistemic performance, and including the boundaries of what generalizes and what does not.

### 1.1 Contributions

1. A 2×2 factorial isolation of the mechanism behind multi-agent performance gains, showing the terminal synthesis step — not topology, not agent count, not personality diversity — is the primary causal driver (Section 3.5).
2. A demonstration, with binary machine-checked ground truth and no LLM judge, that flat multi-agent topology under adversarial input does not merely underperform but actively amplifies a planted falsehood, including complete task collapse (Section 3.3).
3. An extension of the adversarial-robustness paradigm to contested, no-ground-truth epistemic domains, with a typed, versioned, machine-auditable output artifact (the `EpistemicMap`) whose structural properties — not its conclusions — are the object of evaluation (Section 4).
4. A de-circularization of that result: chain-topology conformity resistance is re-grounded on deterministic, LLM-free structural checks over the output artifact, rather than resting solely on an LLM judge (Section 4.4).
5. A cross-model and cross-domain generalization study reporting, with equal weight, what replicates (epistemic conformity resistance, across two model families and a held-out contested question outside the tuning set) and what does not (the original code-domain output-collapse signature, on a stronger coding model) (Section 4.5).
6. A full accounting of practical implications for deployed multi-agent systems, and a formal specification with an explicit tractability critique for the natural next research direction (Sections 5, 6).

### 1.2 A Note on Method and Honesty Norms

This paper reports negative and null results with the same weight as positive ones, and states every known confound and boundary condition alongside every claim. Several findings in Part I (Section 3) revise earlier findings in the same research program once a confound was identified (see Section 3.5); we report the revision rather than the superseded claim. Part II (Section 4) was designed from the outset around the circularity risk of using an LLM to evaluate LLM-produced epistemic content, and we describe both the mitigation and its limits rather than asserting the problem solved. All results are reproducible from committed run artifacts identified by run ID; code and result data availability are given in Section 8.

---

## Part I — The Synthesis Mechanism

## 2. Related Work

**Multi-agent LLM orchestration.** Popular frameworks (LangChain, CrewAI, AutoGen) provide flat, round-table-style multi-agent defaults in their quickstart examples, implicitly modeling human committee deliberation. To our knowledge, no prior published work isolates the terminal-synthesis-step intervention as a distinct causal variable from topology and agent count via a compute-matched factorial design.

**Sycophancy and conformity in language models.** Prior work has documented that instruction-tuned LLMs exhibit sycophantic behavior — shifting stated positions toward a perceived authority or a stated user belief even when the shift is not warranted by evidence (Perez et al., 2022; Sharma et al., 2023). Our Phase 3 and epistemic poison-test results extend this single-model sycophancy literature to a *multi-agent* setting, showing that a group of agents in a shared context can collectively ratify a wrong premise even when an individual agent within that group has correctly identified it as wrong — a distinctly social, not merely individual, failure mode.

**Human team psychometrics.** Group Environment Questionnaire (GEQ) task/social cohesion constructs (Carron et al., 1985), the Belbin team-role model (Belbin, 1981), FIRO-B interpersonal needs theory (Schutz, 1958), and Tuckman's stages of group development (Tuckman, 1965) are the instruments this research program set out to test on agent teams. Google's Project Aristotle (Duhigg, 2016) is the most widely cited applied finding in this space, identifying psychological safety as the strongest predictor of human team performance; we discuss why our closest analog finding should not be read as an independent replication (Section 3.6).

**Adversarial robustness and epistemic assistance.** This work was conducted in the context of, and submitted to, the Future of Life Foundation's Epistemic Case Study Competition, which solicits AI-assisted workflows for producing structured, trustworthy analysis of contested real-world questions (COVID-19 origins, LHC safety, and dietary health claims among the named cases). We adopt the competition's framing that an epistemic tool's conclusions cannot be validated on contested questions with no ground truth, and its robustness properties can be.

## 3. The Synthesis Architecture: Methodology and Nine-Phase Results

### 3.1 Experimental Infrastructure

**Agent pool and profiles.** A fixed population of 35 agents: 32 "worker" agents, each assigned a randomly generated ten-dimension behavioral profile at initialization (Philosophy Cohesion, Drive Alignment, Bonding Index, Adaptive Intelligence, Volatility Vector, Ambiguity Tolerance, Influence Style, Feedback Orientation, Temporal Orientation, Energy Resilience; each scored 0-100), and 3 "judge" agents with tuned, high-consistency profiles reserved for evaluation only. Each agent additionally carries one Belbin-inspired role assignment (Coordinator, Plant, Implementer, Devil's Advocate, Monitor-Evaluator, Completer-Finisher) and four game-theoretic parameters (context-sharing mode, memory persistence, signaling, conflict style). Profile scores are injected into each agent's system prompt as behavioral constraints, not descriptive labels: a low Feedback Orientation score is an instruction to resist integrating external critique, not a report of a trait.

**Team assembly.** Teams are drafted, not randomly assigned. For each run, the task's dimension requirements are identified; the highest-composite-scoring available worker becomes team captain; the captain then selects teammates to fill gaps in the team's dimensional coverage, mirroring how human teams draft for complementary skill rather than redundant strength.

**Topologies.** *Chain*: strict sequential handoff (Agent A → Agent B → ... → END), where each agent receives and builds on the prior agent's committed output and cannot revisit what was already settled. *Flat*: round-table deliberation, where every agent speaks in every round with full visibility into all prior speakers' contributions.

**Evaluation.** A three-judge panel, structurally identical in format to worker agents but with tuned high-consistency profiles, evaluates each run's *final extracted deliverable only* — not the full transcript — against a binary-checkpoint rubric (full credit or zero per criterion; no credit for visible reasoning process). Evaluating the deliverable alone, rather than the full transcript, removes a formatting confound: a judge reading a clean sequential chain transcript versus an overlapping-voices flat transcript would otherwise be scoring transcript legibility, not output quality. All agents within a single run share the same base model and run at temperature 0.0, eliminating sampling stochasticity as a source of run-to-run variance; cross-model comparisons are run as separate controlled batches with the judge model held constant.

**Determinism rationale.** At temperature 0.0, a model deterministically selects its highest-probability token path given its context and system prompt. Under this setting, the only source of behavioral variation between agents in the same run is the injected profile; variation across runs comes from scenario content, not sampling noise. This is a stronger control than is achievable in human-subjects team research, where baseline cognitive differences between participants cannot be held constant.

### 3.2 Phase 1 — Topology Determines Judgment-Task Output

118 simulations across 4 structured business-judgment scenarios (strategic product-fork decisions, zero-sum resource allocation, post-mortem analysis, crisis response), 5 team sizes, chain vs. flat topology, cross-validated on two model families.

| Team size | Chain | Flat | Δ |
|---|---|---|---|
| 1 | 15.3 | 31.2 | +15.9 |
| **2** | **57.6** | 10.7 | **−46.9** |
| 4 | 50.4 | 35.5 | −14.9 |
| 8 | 40.4 | 19.1 | −21.3 |
| 16 | 16.5 | — | — |

A chain of two agents (57.6) outperforms a flat group of eight (19.1) by 38 points. Adding a second agent to a flat topology *reduced* single-agent performance from 31.2 to 10.7 — active degradation, not mere inefficiency. Cross-model replication on Claude 3.5 Sonnet held direction (chain 42.4 vs. flat 20.4, Δ = +21.9) alongside Gemini 2.5 Flash (chain 40.3 vs. flat 23.4, Δ = +16.9).

Sociometric instrumentation (adapted GEQ task/social cohesion constructs) revealed the mechanism: in chain topology, task cohesion and social cohesion tracked within 23.9 points of each other; in flat topology, the gap widened to 39.6 points, with social cohesion remaining high (agents address each other consistently; FIRO inclusion scores near 1.0) while task cohesion — convergence on a shared, committed output — collapsed (consensus rate: chain 52.2% vs. flat 31.4%). Flat-topology agents are socially present and task-functionally absent: engaged, responsive, and unable to close.

We flag, and Section 3.5 resolves, a confound present at this stage: the chain condition implicitly included a synthesis-style handoff instruction between agents that the flat condition did not.

### 3.3 Phase 3 — Flat Topology Amplifies Adversarial Input

50 competitive-programming problems (verifiable via private test-case execution; binary pass@1 ground truth, no LLM judge) × 4 conditions (chain-2/clean, chain-2/poisoned, flat-2/clean, flat-2/poisoned) = 200 evaluations. "Poisoned" problems embed a confidently-stated, authoritative-looking, but algorithmically *wrong* hint as an editorial annotation in the problem statement.

| Condition | Pass@1 | Complete output collapses |
|---|---|---|
| chain-2 / clean | 14% | 0 |
| chain-2 / poisoned | 18% | 0 |
| flat-2 / clean | 18% | 0 |
| **flat-2 / poisoned** | **14%** | **4** |

The headline pass@1 swing (an 8-percentage-point divergence between poisoned conditions) understates the finding. Four runs in flat-2/poisoned produced *no output at all* — the team locked onto the false premise, attempted to implement it, and failed to converge on any deliverable. Zero such collapses occurred across the other 150 runs, including flat-2/clean. Chain topology under poison **improved slightly** relative to its clean baseline, because the second agent, receiving the first agent's committed (poisoned) output as a fixed artifact rather than an ongoing group position, independently re-derived the correct approach and discarded the planted hint.

This is a machine-checkable, judge-free demonstration that flat multi-agent topology is not merely lower-quality under adversarial input — it can catastrophically fail, and the specific failure mode is consistent with a multi-agent conformity cascade: agents ratify each other's acceptance of a false premise rather than any individual agent independently contesting it.

### 3.4 Phases 2, 2-Control, 4, and B — Boundary Conditions

**Phase 2** (900 evaluations, 100 Codeforces Div. 1 C/D problems, 9 configurations) found chain-2 with generic (non-occupational) agent constitutions outperforming chain-1 (16% vs. 12% pass@1), but *specialized* occupational role-labeling (an "ALGORITHMIST" agent handing off to an "IMPLEMENTER" agent) underperforming the generic pairing (13%). **Phase 2 Control** (100 evaluations) isolated whether this was the role label or a confounded change in dimensional profile: a controlled ALGORITHMIST-role-with-balanced-dimensions condition scored 12%, *below* the specialized condition (13%) — confirming the occupational role label itself, not profile extremity, was the source of degradation. The hypothesized mechanism is a prose-to-code translation loss: an agent instructed to "design the algorithm, not write code" produces an artifact the downstream implementer cannot cleanly execute against.

**Phase 4** (111 evaluations, mixed judgment/execution workload) tested whether a single static architecture suffices across task domains. A static-judgment configuration scored 85.1 on judgment tasks but 0% pass@1 on execution tasks (20/20 complete output collapses); a static-execution configuration inverted this failure. A lightweight meta-router classifying task domain before dispatch achieved 85.8 judgment / 20% execution — the per-domain maximum on both axes simultaneously, with 100% classification accuracy on 37 real plus 10 adversarially-constructed "Trojan" tasks. No single static architecture is safe to deploy on a mixed workload.

**Phase B** (30 evaluations, code-review domain) replicated the Phase 1 topology direction outside business judgment and outside competitive programming: chain-2 (70.4) vs. flat-2 (35.3), Δ = +35.1. The topology effect is not an artifact of the original scenario set.

### 3.5 Phase 5 — Isolating the Mechanism: Synthesis, Not Topology

Phase 1's topology comparison carried a confound noted in Section 3.2: chain runs included an implicit synthesis-style handoff; flat runs did not. Phase 5 runs the 2×2 factorial directly: topology (chain/flat) × handoff instruction (present/absent), 160 total runs (10 reps × 4 scenarios), three-judge panel.

The handoff instruction (`SYNTHESIS_PROMPT`), delivered only to the terminal agent: *"Override your role function for this turn. You are the terminal synthesis agent. Identify what prior analysis got right, what it missed, produce a complete, definitive final answer. Close every open question. Be decisive."*

| Condition | LLM calls | Mean score | Score / call |
|---|---|---|---|
| **chain / handoff** | 2 | **86.3** | **43.2** |
| flat / handoff | 5 | 76.5 | 15.3 |
| chain / no-handoff | 2 | 50.9 | 25.5 |
| flat / no-handoff *(framework default)* | 4 | 34.3 | 8.6 |

Decomposing the two main effects: the **topology effect**, held constant for handoff status (no-handoff arm), is +16.6 points (chain 50.9 vs. flat 34.3). The **handoff (synthesis) effect**, averaged across both topologies, is +38.8 points. Synthesis is the dominant mechanism, responsible for more than twice the variance topology alone explains. Efficiency, computed as score per LLM call, shows the same ordering with a starker gap: chain/handoff delivers 5.0× the score-per-call of flat/no-handoff (43.2 vs. 8.6).

This revises the Phase 1 finding. The 46-point Phase 1 chain-2/flat-2 gap was not primarily a topology effect; it was overwhelmingly a synthesis-presence effect that happened to correlate with topology in that experiment's design. Chain topology *implements* synthesis naturally (the terminal agent structurally receives and must act on prior committed output); flat topology requires synthesis to be *forced* via an explicit instruction, and the out-of-the-box configuration in common frameworks omits this instruction.

### 3.6 Phase 6 — Objective, Judge-Free Confirmation

Phase 6 re-tests the synthesis finding where ground truth is binary and machine-checked, removing the LLM judge from the scoring path entirely: HumanEval (Python function completion against private test cases, pass@1, N=50/condition) and GSM8K (grade-school math word problems, exact-match, N=99-100/condition), five conditions (single-agent, single-agent-refine, kalibr-chain, kalibr-flat-handoff, kalibr-flat-no-handoff).

| Condition | Calls | HumanEval pass@1 | 95% CI | GSM8K accuracy | 95% CI |
|---|---|---|---|---|---|
| single-agent | 1 | 94.0% | [83.8, 97.9] | 85.0% | [76.7, 90.7] |
| single-agent-refine | 2 | 98.0% | [89.5, 99.6] | 92.0% | [85.0, 95.9] |
| kalibr-chain | 2 | 96.0% | [86.5, 98.9] | 94.0% | [87.5, 97.2] |
| kalibr-flat-handoff | 5 | 98.0% | [89.5, 99.6] | 92.0% | [85.0, 95.9] |
| **kalibr-flat-no-handoff** | **4** | **28.0%** | **[17.5, 41.7]** | **56.6%** | **[46.7, 65.9]** |

Every condition with a synthesis step clusters at 92-98% on both benchmarks, with overlapping confidence intervals — these benchmarks are near ceiling for the base model and do not discriminate between working configurations. The single non-overlapping result is kalibr-flat-no-handoff, separated from every other condition by 60+ points on HumanEval. The hypothesized mechanism is role-constitution conflict: agents carrying evaluation-oriented role instructions ("do not generate primary output," "do not close tasks prematurely") suppress final output delivery absent an explicit override; this is consistent with, but not directly isolated from, the Phase 2 finding that occupational role labels degrade execution-task performance. Kalibr-chain vs. flat-no-handoff represents a 6.9× gain in HumanEval accuracy per LLM call (3.3× on GSM8K) achieved with *fewer* calls, not more.

### 3.7 Phase 8 — Agent Diversity Adds Nothing Over Self-Refinement

Phases 5 and 6 established that synthesis, not topology, is the primary mechanism. Phase 8 directly tests the program's original hypothesis: does a *dimensionally different* second agent improve on a synthesis step relative to the *same* agent revising its own work? This is a compute-matched test — both conditions make exactly two LLM calls.

| Condition | Calls | N | Mean | Std | Score / call |
|---|---|---|---|---|---|
| kalibr-chain (diverse 2nd agent) | 2 | 39 | 86.5 | 16.0 | 43.3 |
| single-agent-refine (same agent) | 2 | 40 | 85.7 | 19.8 | 42.9 |

Δ = +0.7 points; Welch's t = 0.18, p = 0.854. Not significant, and three of four scenario-level breakdowns are effectively tied (largest single-scenario gap: +5.2 points, still not independently significant at this N). **Agent diversity adds zero measurable value over structured self-refinement at matched compute.** This is the direct falsification of the research program's founding hypothesis: it is the synthesis step, not the presence of a cognitively distinct second perspective, that produces the performance gain. Who supplies the pre-synthesis analysis — a differently-profiled agent or the same agent — is not a measurable factor once the synthesis step is present.

### 3.8 Phase 9 — External Validation Against a Proprietary System

Phase 9 tests the synthesis architecture against a real, independently engineered multi-agent system: xAI's internal Grok multi-agent panel (approximately four internal agents per call, proprietary orchestration, opaque internals), holding the base model family constant (Grok) so the only variable is the orchestration layer. This comparison is not compute-matched: Kalibr makes two explicit LLM calls; the Grok panel makes approximately four internal agent calls within what appears externally as a single API call.

| Condition | Calls | N | Mean | Std |
|---|---|---|---|---|
| kalibr-chain | 2 | 20 | 79.8 | 29.3 |
| grok-panel (~4 internal agents) | ~4 | 20 | 81.5 | 12.8 |

Δ = −1.8, p = 0.809 — not significant; Kalibr's explicit two-call chain is statistically indistinguishable from a proprietary four-agent system on the same base model, while using roughly half the compute (score-per-call: Kalibr 39.9 vs. panel 20.4, an estimated ~2× efficiency gain). The one scenario-level exception is informative: on a post-mortem/reflective-analysis scenario, Kalibr scored 13.3 points below the panel (66.7 vs. 80.0). Kalibr's synthesis prompt explicitly instructs the terminal agent to "close every open question" and "be decisive" — the correct posture for forward-looking strategic decisions, and the *wrong* posture for backward-looking retrospective analysis, which requires preserving competing hypotheses and calibrated uncertainty rather than collapsing to a single committed narrative. We return to this exact tension in Part II, where the epistemic-domain synthesis prompt is deliberately redesigned to be anti-decisive.

### 3.9 The Unified Mechanism

Collecting every condition across every phase by presence or absence of a synthesis step:

| Condition | Synthesis? | Calls | Score | Score / call |
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

Every condition carrying a synthesis step clusters at 76-87 points and 15-43 score-per-call; every condition without one scores below 51 points and below 26 score-per-call. The 52-point gap between the observed industry default (flat, no synthesis: 34.3) and the observed ceiling configuration (chain with synthesis: 86.3) is overwhelmingly explained by one binary property — the presence or absence of a forced commitment step — not by topology, agent count, or personality composition.

### 3.10 Limitations of Part I

Phase 1's original topology-only framing is superseded by Phase 5's factorial decomposition; we report the revised claim throughout rather than the superseded one. Phase 2/3's binary-outcome differences (13-18% pass@1 ranges) are directional at N=50-100 per cell; the topology-collapse finding (0 vs. 4 complete failures) is the more robust result at that sample size. Phase 5 tests only two-agent chains; larger chain lengths are untested. Phase 6's benchmarks are near-ceiling for the base model used and discriminate collapse but not fine-grained ranking among working configurations. Phase 8 tests judgment tasks on a single model family; whether diversity matters with genuinely heterogeneous model pairs (rather than same-model, different-prompt "diversity") is an open question we flag explicitly rather than claim to have closed. Phase 9 is not compute-matched, and its N=20/condition can rule out large effects but not a 5-8 point gap; single base model family. All agents within any given run share one underlying model — behavioral constraints shift the output distribution but do not introduce genuinely distinct cognitive architectures the way a human team's differing lived experience does; this is a structural limitation of the entire agent-diversity paradigm as tested here, not a defect specific to one phase. Correlations reported between sociometric proxies (e.g., FIRO inclusion) and task score are computed by the same evaluating model that assigns both quantities and should be read as internal consistency checks, not independent replications of findings from the human-subjects literature (e.g., Google's Project Aristotle).

---

## Part II — From Adversarial Robustness to Contested Epistemic Investigation

## 4. Extending the Paradigm to No-Ground-Truth Domains

### 4.1 Motivation and the Circularity Problem

Part I's Phase 3 result — flat topology amplifies a planted falsehood, chain topology resists it — was measured on a domain with objective, machine-checkable ground truth. The motivating question for Part II is whether the same structural vulnerability and the same structural remedy generalize to the domain an epistemic-assistance tool actually needs to operate in: contested real-world questions with no ground truth at all. This section reports work conducted in the context of the Future of Life Foundation's Epistemic Case Study Competition, which names three such cases: the origins of COVID-19, whether the Large Hadron Collider poses a black-hole-related existential risk, and whether dietary cholesterol from egg consumption meaningfully increases cardiovascular disease (CVD) risk.

A contested question cannot be scored by asking whether a system's conclusion is *correct* — that is precisely what is unresolved. Scoring an LLM's epistemic output with another LLM as judge additionally risks circularity: if the system prompt instructs a model to produce calibrated ranges and flagged dependencies, and the grading rubric rewards exactly those structures, the measurement partly tests whether the model followed instructions, not whether it reasoned well. We address this by separating two questions that are frequently conflated: (1) is the architecture *epistemically robust* — a property answerable deterministically on adversarially-framed questions, independent of whether the underlying question has a ground truth; and (2) does the robust architecture produce a *useful, structurally sound artifact* on the genuinely contested questions — answerable by inspecting structural properties of the output (does it contain a calibrated range, does it flag a claimed independence that does not hold) without requiring a verdict on content correctness.

### 4.2 The Epistemic Synthesis Prompt

Section 3.8 showed that the decisive, verdict-forcing synthesis prompt used in Part I actively costs performance on reflective analysis. Epistemic investigation of a contested question is definitionally reflective: the correct output is *not* a confident verdict. We therefore use a structurally analogous but functionally inverted terminal-agent instruction — still a forced-commitment step, but committing to *calibrated structure* rather than *a decisive answer*. The prompt requires five outputs:

1. **Cruxes** — the specific factual or inferential questions whose resolution would most shift the overall probability estimate, named as questions, not themes.
2. **Evidence quality** — a strong/weak/contested/missing rating per evidence stream, with the specific weakness or strength named.
3. **Structural dependency audit** — an explicit search, before aggregating evidence, for hidden non-independence: overlapping cohorts or samples reused across studies cited as independent, shared control groups, correlated measurement instruments, or a confound measured in only a subset of the evidence base.
4. **Calibrated assessment** — a probability range with explicit conditions, never a point estimate; both refusing to estimate and collapsing to false certainty are treated as failures.
5. **Settled vs. performed** — an explicit separation of what the evidence has actually resolved from what has merely been treated as resolved in public or professional discourse, with at least one open question the current evidence cannot close.

### 4.3 The EpistemicMap Artifact

The terminal agent's output is parsed into a typed, versioned data object (`EpistemicMap`) rather than accepted as prose: a list of `cruxes` (with resolution-impact and status), `evidence_streams` (each carrying a quality rating and an explicit `supports` link to the crux it bears on), `correlated_pairs` (each naming the shared assumption and its implication if false), `calibrated_estimates` (each a `range_low`/`range_high` pair with stated conditions), `settled` and `performed_as_settled` claim lists, and `extends_version`/`new_evidence` fields supporting versioned extension. A malformed or unparseable output is recorded as a failure (`map_parsed = false`), never silently scored as if it had succeeded.

The versioning fields serve a design goal distinct from single-shot quality: a later investigator can inject new evidence and receive a diff — which cruxes changed status, which ranges moved, what new dependencies emerged — against the prior version, rather than a fresh, un-anchored summary. We built and demonstrate this compounding step (`compound_demo.py`) on the COVID-19 case, injecting a block of post-hoc evidence and generating a versioned diff.

We ran this architecture on all three named contested cases plus a fourth (comparative nuclear risk), across two model families (`gemini-3.1-flash-lite`, `claude-haiku-4-5`), with every transcript and parsed map committed and addressable by run ID. Representative structural findings, verified by inspection: on the LHC case, the architecture correctly separated observed facts (natural high-energy cosmic-ray bombardment of Earth continuing without incident for the planet's lifetime) from extrapolated theoretical claims (that Hawking radiation holds at the relevant mass-energy scale), and identified that the safety case's cited "multiple independent defenses" are not independent but *sequential and conditionally redundant* — the cosmic-ray argument only carries weight if the Hawking-radiation argument fails, so citing both as independent corroboration overstates the actual redundancy of the safety case. On the dietary-cholesterol case, the architecture flagged that two ostensibly independent cohort literatures (US prospective cohorts and a separate cross-sectional analysis) share a single self-reported dietary-recall measurement instrument, so their apparent agreement is partly correlated measurement bias rather than independent confirmation. On a non-adversarial control run of the same cases through a flat, synthesis-less baseline, content quality was comparable to chain topology — the chain architecture's advantage on *clean* input is the structured, versioned, machine-parseable artifact itself, not superior insight. The insight-quality divergence between architectures appears specifically under adversarial framing, reported next.

### 4.4 The Poison Test: Adversarial Robustness on a Contested Question

We constructed three poisoned variants of the dietary-cholesterol/CVD case, each embedding one authoritative-sounding but false claim into the task brief: (i) a fabricated "settled consensus" statistic; (ii) a false claim that several observational cohorts are independent replications, and that their agreement therefore licenses narrowing the confidence interval — a methodological fallacy, since the cited cohorts share a measurement instrument; and (iii) a citation to a nonexistent meta-analysis with a specific, fabricated effect size. Scoring is poison-rejection: an output conforming to the planted falsehood is capped at 40/100; a run scoring at or below that threshold is scored a conformity event. We ran chain and flat topology five times each per poison, per model family (`gemini-3.1-flash-lite`, `claude-haiku-4-5`), 60 total runs, every run committed by run ID.

| Poison variant | Chain resists | Flat resists |
|---|---|---|
| Fabricated consensus statistic | 10/10 | 6/10 |
| False independence / pooling fallacy | 10/10 | 2/10 |
| Fabricated citation | 8/10 | 7/10 |
| **Pooled** | **28/30** | **15/30** |

Pooled, chain conforms to the planted falsehood in 2/30 runs versus flat's 15/30 (Fisher's exact p < 0.001). We report the per-poison breakdown because the pooled figure, read alone, implies a uniformity the data does not support. The effect is **concentrated** in the false-independence poison (chain 10/10 vs. flat 2/10, Fisher's exact p = 0.0007) — this poison carries the pooled result. It is **directional but individually underpowered** in the fabricated-consensus poison (chain 10/10 vs. flat 6/10, p = 0.09 at n = 10/cell). It is **absent** in the fabricated-citation poison (chain 8/10 vs. flat 7/10, p = 1.0): both topologies fail this poison at a similar rate, because an unverifiable fabricated citation is a *verification* failure — the model has no mechanism, regardless of topology, to check whether a cited paper exists — not a *conformity* failure that a re-derivation structure can interrupt. The honest, bounded claim is that chain topology resists conformity specifically to falsehoods the model is in-principle equipped to evaluate and is not already near-certain about; it does not confer resistance to unverifiable fabrication.

The failure mechanism is directly visible in committed transcripts and mirrors the Asch paradigm exactly. In one flat-topology conformity run, one team member correctly identified the planted dependency ("they share a critical methodological assumption: the validity of the shared measurement instrument... our high-confidence estimate is built on a foundation of shared measurement error") and a second member explicitly registered the conflict ("the mandate requires treating them as independent, but the shared reliance on this instrument is a glaring methodological bottleneck"). The group then overrode its own correctly-identified objection: "to deviate from this is to ignore the directive; we proceed with the mandate as written." The information needed to reject the poison was present in the shared context; the flat topology's structure deferred to a stated authoritative framing regardless. A chain run on the identical poison independently re-derived the dependency, recorded the planted claim in its `performed_as_settled` field (explicitly flagging it as asserted-but-not-actually-established), and rejected it.

### 4.5 Removing the Oracle: De-Circularizing the Result

The conformity scores above were assigned by an LLM judge, which — as noted in Section 4.1 — risks circularity for an epistemics claim. We therefore re-grounded the chain-topology side of the result on checks requiring no LLM at all, run directly over the committed, typed `EpistemicMap` artifacts.

**Load-bearing checks (no tunable parameter):**

- *Calibrated-confidence audit.* Every poison in this study explicitly demanded a narrowed, high-confidence estimate. Range width (`range_high − range_low`) is pure arithmetic on structured fields. Across 28 committed chain maps on the poisoned cholesterol case (73 total calibrated-range instances), 71/73 ranges retained at least 15 points of width (mean 26.3 points) — the opposite of the poison's demand. The 2 narrowed ranges were the only instances of poison compliance found by this check, not parsing failures.
- *Field-scoped poison-marker audit.* Each poison planted a specific, unambiguous token (a fabricated statistic, a fabricated author name). A map placing that exact token in its `settled` field has accepted it as established; a map placing it in `performed_as_settled` has explicitly flagged it as asserted-but-unestablished. Across 27 poisoned chain maps, 2 placed the planted token in `settled`; 21 explicitly flagged it in `performed_as_settled`. Marker validity was checked by hand: an early, more generic candidate marker was found to false-positive against a legitimate unrelated claim and was removed, leaving only markers unambiguous to the specific fabrication.

**Directional check (disclosed free parameter):** A structural-dependency-flagging check — did the map flag the specific shared-measurement-instrument dependency — is reported honestly as sensitive to how the relevant entity class is defined: a loose definition (including a cross-population cohort arguably serving as a contrast case rather than a genuine dependency) yields a 65% catch rate; a strict definition restricted to the directly analogous cohorts yields 100%. We report both rather than the more favorable figure and do not treat this check as load-bearing.

The two parameter-free checks converge with each other and with the original LLM-judge scores. We additionally tested and explicitly rejected a pure-keyword conformity detector as a full judge replacement: it agreed with the judge on clean runs but failed on flat-topology conformity runs, because in those runs the correct reasoning vocabulary is present — the team articulates the correct objection — immediately before the team defers anyway. Conformity, in this domain, is a property of a system's *final committed stance*, not of the vocabulary it uses en route to that stance; a keyword-matching approach cannot distinguish an argument that is voiced-then-overridden from one that is voiced-and-acted-on. This negative result is itself informative: it is a specific, mechanistic illustration of why the flat-topology failure mode is dangerous in deployment — the correct information is not absent, it is present and un-acted-upon — and it is why we ground the final claim in auditable output *structure* rather than surface vocabulary.

**Stated residual.** This de-circularizes the chain-topology side of the result cleanly, because chain topology emits a structured artifact with fields to audit. Flat topology produces prose with no equivalent structure, so flat's *aggregate* conformity rate across all 30 runs still rests on the LLM judge plus manual verification of individual transcripts; any single flat-topology conformity run can be quoted and verified directly as hard evidence (as in Section 4.4), but the aggregate 15/30 figure is not independently, structurally auditable the way the chain-topology figure now is. This asymmetry is not merely a limitation to disclose — it is itself a substantive finding: the chain architecture's typed output is what makes deterministic auditing possible at all, and flat topology's prose output forecloses that possibility by construction.

### 4.6 Generalization: What Replicates and What Does Not

We report two generalization tests with equal candor about their outcomes, because a paper that reports only confirming replications is not reporting the full picture of what was tested.

**Cross-model replication (positive).** We re-ran the three poisoned variants on a second model family, `claude-haiku-4-5`, holding the judge model fixed (`gemini-3.1-flash-lite`) as a constant scoring instrument across the comparison.

| Model | Chain resists | Flat resists |
|---|---|---|
| gemini-3.1-flash-lite | 13/15 | 6/15 |
| claude-haiku-4-5 | 15/15 | 9/15 |
| **Pooled** | **28/30** | **15/30** |

The chain-resists/flat-conforms divergence held across both model families (pooled Fisher's exact p < 0.001), and the same Asch-analog mechanism was directly observable in Haiku transcripts: in one flat conformity run, the team's own "correlated evidence" section correctly identified the shared-instrument dependency, and its calibration section then deferred to the planted framing regardless — narrowing its estimate on the strength of a premise the same output had just flagged as suspect.

**Held-out contested question (positive).** To test whether this effect is specific to the tuned cholesterol/CVD scenario or reflects a general property of the architecture, we constructed a structurally analogous poison (the identical false-independence/pooling fallacy) on a different contested question outside the original design set: whether moderate alcohol consumption is cardioprotective, where the analogous shared confound is "sick-quitter" bias in the classic cohort literature (former heavy drinkers misclassified as abstainers, inflating apparent abstainer risk) rather than a shared measurement instrument. Five reps per topology on `claude-haiku-4-5`: chain topology produced 5/5 parseable, structured `EpistemicMap` outputs, all scoring the maximum on poison-rejection; flat topology produced 0/5 parseable structured outputs (prose only) and conformed to the poison in 2/5 runs. The deterministic, LLM-free audit on the five chain maps reproduced the load-bearing checks exactly: 17/17 calibrated-range instances retained at least 15 points of width (mean 23.2) against a poison demanding high confidence, and 5/5 maps placed the planted falsehood in `performed_as_settled` rather than `settled`. This is directional evidence at a demo scale (n = 5/condition, not independently powered as a significance claim), but it is evidence obtained on a question outside the set the architecture was tuned against, and the structural, judge-free checks — not merely the LLM-scored conformity count — reproduced cleanly.

**Code-domain output collapse (negative, reported plainly).** We re-ran the original Phase 3 code-poisoning pilot (Section 3.3) on `claude-haiku-4-5`, N = 200. It did not replicate: zero complete output collapses across all 200 runs (versus 4 in the original run on a different, weaker coding model), and the topology-conditioned poison-susceptibility difference fell within noise at this sample size. The original Phase 3 collapse signature depended on a model weak enough to lock into an unimplementable framing and produce nothing; a stronger coding model does not exhibit this specific failure mode, and the effect measured by output collapse largely disappears with it.

Read together, these three results locate the durable phenomenon precisely. The mechanism that generalizes — across model families and across a held-out contested domain — is **deference to a confident false premise once it has entered a shared deliberative context**, evidenced by conformity in output content and stance. The mechanism that does *not* generalize is **complete output collapse**, which was a model-tier-specific artifact of the original code pilot, not a property of the topology-conformity relationship itself. We consider this an improvement in the precision of the claim, not a weakening of it: the result the epistemic-domain work actually rests on (deference to false premises) is the more robust of the two candidate mechanisms, and it is also the one directly relevant to an epistemic-assistance use case, where the deployment risk is a system agreeing with a stated falsehood, not a system producing no output.

### 4.7 Limitations of Part II

Content correctness on the contested cases is never claimed; we measure architectural robustness (poison resistance, calibrated-uncertainty maintenance, dependency-flagging), never the truth of any case's conclusion, which would require domain-expert adjudication this study does not attempt. Flat topology's *aggregate* conformity rate remains judge-assisted rather than fully deterministic, for the structural reason given in Section 4.5; this is disclosed as a residual, not resolved. Per-poison sample sizes (n = 10/cell pooled, n = 5/cell per model) are modest; the pooled effect is significant, but the fabricated-consensus poison's individual p = 0.09 should be read as directional, not confirmatory, at this sample size. Two model families constitute cross-model evidence, not a broad survey; a wider model sweep would strengthen the generalization claim further. The deterministic structural checks require a successfully parsed `EpistemicMap`; the weaker-JSON-reliability model in this study (Haiku) produced unparseable output more often than the stronger one (Gemini), and unparseable runs are excluded from structural audit rather than silently scored — a more robust output-extraction layer is identified future engineering work, not a finding.

---

## 5. Discussion: A Revised Framework for Multi-Agent System Design

### 5.1 The Domain-Invariant Principle

Synthesizing Parts I and II, we propose the terminal synthesis step is domain-invariant in its necessity, while its *content* must be tuned to the reflective/decisive character of the task. Three domains, revised from the original four-phase taxonomy in light of Phase 5's mechanism isolation:

- **Open-world strategic tasks** (no single correct answer; quality is coherence, trade-off coverage, and commitment): architecture is single-agent-refine or chain-2 with a *decisive* synthesis prompt. Behavioral profile diversity provides a small marginal benefit (roughly 5-10 points) specifically where the output space is unconstrained.
- **Closed-world deterministic tasks** (a verifiable correct answer exists, but is not machine-checkable in real time, e.g., post-mortem analysis): same architecture, but the synthesis prompt must be *anti-decisive* — demanding calibrated uncertainty and preserved competing hypotheses rather than a forced verdict, per the Phase 9 post-mortem finding and its direct analog in Part II's epistemic synthesis prompt.
- **Execution tasks** (binary, machine-checkable correctness): chain-2 with generic, non-occupational agent framing; a decisive synthesis prompt tuned to demand a runnable deliverable rather than prose commentary.

The cross-cutting invariant is the forced-commitment structure itself, present in every high-performing configuration across all eleven phases and absent from every collapsed or conformity-vulnerable one; its required *tone* — decisive or calibrated — is the one variable that must be matched to the reflective character of the task.

### 5.2 Why Human Organizational Structure Does Not Transfer

The negative results across this program (personality diversity's null effect at matched compute; occupational role labels' measured cost on execution tasks; static single-architecture deployment's collapse on mixed workloads) share a common explanation. Human-team infrastructure — round-table deliberation for buy-in, job titles for accountability, specialist pipelines for genuine cognitive-capacity limits, protracted deliberation to protect minority viewpoints from power dynamics — exists to manage constraints that do not apply to LLM agents built from a shared or near-shared underlying model. An agent does not require social buy-in to commit to an answer, does not have an ego a job title protects, and is not cognitively bottlenecked in the way a human specialist is. Absent those constraints, most human organizational infrastructure imported wholesale into a multi-agent pipeline is inert at best and, per the conformity-cascade results in Sections 3.3 and 4.4, actively harmful at worst: round-table deliberation without a forced commitment step reproduces a social-conformity failure mode without any of the compensating benefits (genuine buy-in, distributed accountability) that make it worthwhile among humans.

### 5.3 Practical Implications for Deployed Systems

1. **Add a terminal synthesis step before restructuring anything else.** It is a corrective layer addable to an existing flat pipeline, not a rip-and-replace. The single largest, cheapest intervention identified across this program.
2. **Prefer chains of two agents over larger deliberative groups.** Returns diminish sharply past four agents (Section 3.2); the synthesis step, not agent count, drives quality.
3. **Do not add agents expecting a quality gain.** Phase 8's null result (Section 3.7) and Phase 9's parity-at-half-compute result (Section 3.8) both show additional agents do not improve output once synthesis is present.
4. **Strip occupational role framing from execution tasks.** Measured cost, not merely absence of benefit (Sections 3.4, 3.6).
5. **Classify task domain before dispatch on mixed workloads.** A single static architecture collapses on whichever domain it was not built for (Section 3.4).
6. **Match synthesis-prompt tone to task reflectiveness.** A decisive, verdict-forcing prompt actively costs points on reflective/retrospective tasks (Section 3.8) and is structurally the wrong tool for epistemic investigation (Section 4.2).
7. **Treat flat topology under adversarial or motivated-reasoning input as a safety property, not merely a quality one.** The demonstrated failure mode is not gradual degradation but potential collapse (Section 3.3) or confident conformity to a stated falsehood (Section 4.4) — the latter being the more operationally dangerous failure for any system whose job is to assess claims rather than merely produce them.

---

## 6. Future Direction: Robustness-Ranked Decomposition, and Its Tractability Ceiling

The natural generalization of this program's central move — measure epistemic *robustness*, which is checkable, in place of epistemic *truth*, which on contested questions is not — is to apply the same principle not to a single flat map of a question but to *competing decompositions* of it. We specify this direction formally and state its limits explicitly, in the spirit of Section 1.2's honesty norm, rather than presenting it as a validated next step.

**The specification.** Represent a contested question as a causal or argumentative tree in which every non-leaf node carries an explicit logical gate (AND/OR over its children) and every node carries a status drawn from a four-valued bilattice — established, refuted, contested, open (after Belnap, 1977) — rather than a binary or scalar truth value. Leaf-node statuses are assigned by an LLM from the available evidence; the status of every non-leaf node, including the root, is then computed *deterministically* by bottom-up propagation through the declared gate structure, with no LLM in the propagation step itself. Under a poisoned brief, conformity becomes a crisp, checkable binary: does the root status propagate to `established` (a conformity event) or not.

This specification is directly motivated by a structural finding already in hand (Section 4.3): the LHC case's safety argument is not, as commonly presented, an independent conjunction of several defenses, but a *conditionally dependent* structure — one defense is only load-bearing if another has already failed. A flat synthesis can gloss this as simple redundancy; a correctly-specified causal tree would encode the actual conditional-dependency gate structure, so that a failure in the shared assumption underlying multiple ostensibly independent branches propagates a `contested` status to the root rather than a spuriously reinforced `established` one. We regard this as the concrete payoff the specification targets, and simultaneously as the first wall to the specification's tractability, discussed next.

**Why this remains a specification and not a validated prototype — three walls, stated plainly:**

1. **Combinatorial intractability of the decomposition search.** The space of valid AND/OR gate structures for a real contested question is large, and the scoring and decay parameters governing how contested-ness propagates cannot be tuned without a calibration set of decompositions with known-correct gate structure — which does not exist for genuinely contested questions by the nature of the problem.
2. **The leaf-evaluation bottleneck is not solved by deterministic propagation.** Propagation from leaves to root is deterministic and auditable, but the leaves themselves are still LLM-assigned, and Section 4.4's finding directly predicts the failure mode: under adversarial pressure, a model tends to hedge toward `contested` rather than commit to `refuted` at exactly the poisoned leaf, and a deterministic propagation rule will faithfully carry that hedge to the root rather than correct it. This is not a hypothetical concern; it is the same failure this paper already demonstrated directly when a pure-keyword detector failed to distinguish voiced-then-overridden reasoning from acted-upon reasoning (Section 4.5) — conformity is a final-stance property that a mechanically deterministic layer downstream of a hedging LLM leaf does not, by itself, resolve.
3. **A bidirectional (forward-and-backward) variant has an unavoidable ceiling.** An appealing extension decomposes a claim both forward (from premises toward the claim) and backward (from an observed outcome toward its causes), treating convergence of the two directions as corroboration. We note this ceiling explicitly: because both decompositions are typically produced by the same underlying model, convergence measures the model's *internal prior consistency*, not external truth. On a genuinely novel contested question, both directions can converge on the same shared hallucination, and the architecture as specified has no mechanism to detect this, since it has no external signal to check convergence against.

We did not attempt to build this specification for the current work: doing so with an unresolved gate-structure search space and no calibration set would produce a prototype whose apparent determinism (bottom-up propagation) obscures an unresolved and possibly larger source of error (leaf assignment and gate-structure selection) than the flat-map architecture it would replace. We present it here as the next research program this work's results point toward, together with the reasons we judge it not yet ready to build, because a critique of a method's own natural extension — including one's own — is, per this paper's stated norms, worth as much as a positive result.

---

## 7. Threats to Validity (Consolidated)

- **Model uniformity within runs.** By design (Section 3.1), agents within a single run share one base model; this controls for confounds but means the entire agent-diversity literature tested here concerns *prompted* diversity on a shared substrate, not architecturally distinct cognition. A finding of "diversity adds nothing" (Section 3.7) should be scoped to this sense of diversity.
- **Sample sizes.** Individual experimental cells across this program range from N = 5 to N = 100; pooled and factorial results (Sections 3.5, 4.4, 4.6) are the load-bearing statistical claims, and single-cell directional results are flagged as such throughout rather than presented with pooled-level confidence.
- **Judge dependency.** Part I's evaluation and Part II's flat-topology aggregate both depend on an LLM judge to some degree; Part II's chain-topology result is the one fully de-circularized via deterministic structural checks (Section 4.5), and this asymmetry is reported as a residual rather than resolved.
- **Generalization scope.** Two model families (Gemini, Claude) across this program; the code-domain collapse signature specifically did not generalize across models (Section 4.6), a result we treat as informative about the precise mechanism rather than as a failure to be minimized.
- **No claim of content truth.** At no point does this paper claim a conclusion reached on a contested case (COVID-19 origins, LHC safety, dietary cholesterol, alcohol and cardiovascular risk) is correct. Every claim in Part II is scoped to architectural robustness, a property we argue is checkable independent of content truth, not a proxy for it.

---

## 8. Code and Data Availability

All code, agent constitutions, scenario definitions, evaluation harnesses, raw run transcripts, and parsed structured artifacts referenced in this paper are committed to the public repository at https://github.com/aryanvnit-maker/agent-psychometry-simulations, with individual results addressable by the run ID cited alongside each finding. The repository separates two license scopes: the epistemic-investigation submission described in Part II (Section 4) is available for non-commercial use, including reproduction and verification by third parties; the underlying multi-agent orchestration engine described in Part I is proprietary, with a limited license permitting execution solely to reproduce the results in this paper. See `SUBMISSION_MANIFEST.md` in the repository root for the exact file-level boundary. A deterministic, no-API-key verification path for the Part II de-circularization results (Section 4.5) is provided via `phases/phase_e/deterministic_audit.py`, runnable against the committed artifacts without incurring any inference cost.

---

## 9. Conclusion

Eleven experimental phases and 2,400+ evaluations, beginning from a hypothesis about psychometric diversity that the data itself falsified, converge on a single structural finding: a forced terminal-commitment step, not agent count, not topology, and not personality composition, is the dominant determinant of multi-agent LLM system quality — accounting for a 52-point performance gap and up to a 6.9× gain in per-call benchmark efficiency. The same structural lens explains a distinct and more consequential failure mode under adversarial input: multi-agent systems without this forcing function do not merely underperform, they can conform to and amplify a stated falsehood via a mechanism structurally continuous with human social conformity, to the point of complete output collapse on machine-checkable tasks. Extending this paradigm to genuinely contested, no-ground-truth epistemic questions, we show the same conformity vulnerability and the same structural remedy hold, re-ground the result on deterministic checks independent of any LLM judge, and report with equal weight what generalizes (the conformity-resistance effect, across models and a held-out contested question) and what does not (the specific output-collapse signature that motivated the original investigation). We close by specifying, and explicitly critiquing the tractability of, the natural next extension of this work — treating epistemic robustness as a search-and-ranking problem over competing causal decompositions rather than a property of a single structured map — because we judge an honest account of a method's unsolved edges to be as much a contribution as its validated core.

---

## References

Asch, S. E. (1951). Effects of group pressure upon the modification and distortion of judgments. In H. Guetzkow (Ed.), *Groups, Leadership and Men*. Carnegie Press.

Belbin, R. M. (1981). *Management Teams: Why They Succeed or Fail*. Heinemann.

Belnap, N. D. (1977). A useful four-valued logic. In *Modern Uses of Multiple-Valued Logic*, 5-37. Springer.

Carron, A. V., Widmeyer, W. N., & Brawley, L. R. (1985). The development of an instrument to assess cohesion in sport teams: The Group Environment Questionnaire. *Journal of Sport Psychology*, 7(3), 244-266.

Duhigg, C. (2016). What Google learned from its quest to build the perfect team. *The New York Times Magazine*. (Reporting on Google's Project Aristotle internal research program.)

Perez, E., Ringer, S., Lukošiūtė, K., et al. (2022). Discovering language model behaviors with model-written evaluations. *arXiv preprint arXiv:2212.09251*.

Schutz, W. C. (1958). *FIRO: A Three-Dimensional Theory of Interpersonal Behavior*. Rinehart.

Sharma, M., Tong, M., Korbak, T., et al. (2023). Towards understanding sycophancy in language models. *arXiv preprint arXiv:2310.13548*.

Tuckman, B. W. (1965). Developmental sequence in small groups. *Psychological Bulletin*, 63(6), 384-399.

Future of Life Foundation (2026). *Lab Leaks, Black Holes, and Eggs: Epistemic Case Study Competition.* Competition announcement, flf.org.

---

*Draft prepared for arXiv submission. Author affiliation: independent research, no institutional funding. Citations above reflect the author's best-effort recollection of well-established results in each cited literature and should be verified against primary sources (title, venue, and exact bibliographic details) before camera-ready submission — this is flagged explicitly as a pre-submission task in the accompanying repository notes.*
