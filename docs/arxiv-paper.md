# The Synthesis Step: One Structural Mechanism Explains Multi-Agent LLM Performance and Adversarial Conformity

**Author:** Aryan Shah (independent researcher)
**Contact:** aryan199841@gmail.com
**Repository:** https://github.com/aryanvnit-maker/agent-psychometry-simulations
**Status:** Working draft for arXiv (cs.MA / cs.AI / cs.CL)
**Version:** 0.2

---

## Abstract

Agent personality diversity does not improve multi-agent LLM output. A forced terminal commitment step does, and it accounts for most of the variance we measured across 2,400+ evaluations in eleven phases.

We built a ten-dimension psychometric framework to test whether human team-composition instruments transfer to LLM agent teams. They do not. Compute-matched at two LLM calls, a dimensionally distinct second agent scored 86.5 against a single agent revising its own work at 85.7 (Δ = +0.7, Welch t = 0.18, p = 0.854, N = 79). What moves the number is a terminal instruction that forces the last agent to stop deliberating and commit. A 2x2 factorial over topology and that instruction (160 runs) isolates it: topology contributes +16.6 points, the commitment step contributes +38.8. The default flat round-table with no commitment step scores 34.3/100 on judgment tasks and 28.0% pass@1 on HumanEval (95% CI [17.5, 41.7]) against 94-98% for every other configuration tested.

Under adversarial input the same structure fails differently. It conforms. On 50 competitive-programming problems with wrong algorithmic hints planted in the prompt (200 evaluations, binary pass@1, no LLM judge), flat topology produced 4 complete output collapses and chain topology produced 0 across the other 150 runs. We extended this from machine-checkable code to contested questions with no ground truth: COVID-19 origins, LHC black-hole risk, dietary cholesterol and cardiovascular disease. On three poisoned variants of the cholesterol case across two model families, chain topology resisted the planted falsehood in 28/30 runs against flat's 15/30 (Fisher's exact p < 0.001). We then removed the LLM judge from the chain-side claim: 71 of 73 calibrated probability ranges in the committed chain artifacts stayed at or above 15 points wide against a poison demanding high confidence, and 2 of 27 poisoned chain maps filed the planted token as established. Both checks are arithmetic and set membership on typed fields. No model scores them.

We report what did not replicate with the same weight. The code-domain collapse signature vanished on a stronger coder: 0 collapses in 200 runs on claude-haiku-4-5. The durable mechanism is deference to a confident false premise, not output collapse.

---

## 1. Introduction

Multi-agent LLM systems default to a shape borrowed from human committees: several role-labeled agents deliberating in a shared context. LangChain, CrewAI and AutoGen ship this in their quickstart examples. Nobody had isolated whether the deliberation is doing the work.

We started from the opposite assumption. Human organizational psychology has 40 years of validated instruments for predicting team performance from composition, and we built a framework (Kalibr) to test whether they transfer to agents. Each agent gets a ten-dimension behavioral profile injected as a system-prompt constraint. Teams are drafted for complementary coverage, not assembled randomly. We ran it through nine phases across business judgment, competitive programming, code review and machine-graded benchmarks.

The founding hypothesis is false. Agent diversity adds nothing measurable at matched compute (Section 3.7). What explains the results is one instruction delivered to the last agent in the pipeline: stop deliberating, commit to a complete answer. Presence or absence of that instruction separates every configuration we ran into two clusters with no overlap.

The finding has a second edge that matters more. Under a confidently stated false premise, flat topology does not degrade gracefully. It ratifies the falsehood. Agents in a shared context read each other's acceptance of a wrong framing and agree with it, occasionally to the point of producing nothing at all. Chain topology, where each agent re-derives from the task rather than reading a group position, resists. This is the multi-agent form of the Asch conformity effect and it sits downstream of the single-model sycophancy literature (Perez et al., 2022; Sharma et al., 2023).

Part II extends that result to where it is operationally relevant and methodologically hard: contested questions with no ground truth. You cannot score whether a system's COVID-origins conclusion is correct. You can score whether it resists a planted falsehood, keeps calibrated uncertainty under pressure to narrow it, and flags its own correlated evidence. Those are checkable. That substitution, robustness for truth, is the one durable move in this paper.

### 1.1 Contributions

1. A 2x2 factorial isolating the terminal commitment step from topology and agent count (Section 3.5).
2. A judge-free demonstration that flat topology amplifies a planted falsehood, including complete task failure (Section 3.3).
3. An extension to contested no-ground-truth domains with a typed, versioned output artifact whose structure, not its conclusions, is the object of measurement (Section 4).
4. Removal of the LLM judge from the chain-side robustness claim via deterministic checks on that artifact (Section 4.5).
5. Generalization results in both directions: the conformity effect replicates across two model families and one held-out contested question, the code collapse signature does not replicate on a stronger coder (Section 4.6).
6. A formal specification for the natural next step and the three reasons we did not build it (Section 6).

### 1.2 On method

Two things about how this is written. Negative results carry the same weight as positive ones, including the one that falsified the program's founding hypothesis. And several Part I findings revise earlier findings from the same program once we found the confound; we report the revision, not the superseded claim (Section 3.5).

Part II was designed around the circularity problem from the start. Using an LLM to grade LLM-produced epistemic content, against a rubric that rewards the structures the prompt asked for, measures instruction-following. We describe the mitigation and its residual rather than claiming the problem solved.

---

## Part I: The Synthesis Mechanism

## 2. Related work

**Multi-agent orchestration.** LangChain, CrewAI and AutoGen default to flat round-table configurations in their quickstart documentation. We found no prior work isolating the terminal commitment step as a variable distinct from topology and agent count under a compute-matched factorial.

**Sycophancy.** Instruction-tuned models shift stated positions toward a perceived authority even when evidence does not warrant the shift (Perez et al., 2022; Sharma et al., 2023). Our contribution to that line is the social case: a group of agents can ratify a false premise that an individual agent inside the group has already correctly identified as false. Section 4.4 quotes a transcript where exactly this happens.

**Human team instruments.** GEQ task and social cohesion (Carron et al., 1985), Belbin team roles (Belbin, 1981), FIRO-B (Schutz, 1958), Tuckman's stage model (Tuckman, 1965). These are what the program set out to transfer. Google's Project Aristotle (Duhigg, 2016) is the widely cited applied result; Section 3.10 explains why our nearest analog is not an independent replication of it.

**Epistemic assistance.** Part II was conducted for the Future of Life Foundation's Epistemic Case Study Competition, which names COVID-19 origins, LHC safety and dietary health claims as target cases. We adopt its framing that conclusions on contested questions cannot be validated and robustness properties can.

## 3. Methodology and nine-phase results

### 3.1 Infrastructure

**Agent pool.** 35 agents: 32 workers with randomly generated ten-dimension profiles fixed at initialization, 3 judges with tuned high-consistency profiles used only for evaluation. Dimensions are Philosophy Cohesion, Drive Alignment, Bonding Index, Adaptive Intelligence, Volatility Vector, Ambiguity Tolerance, Influence Style, Feedback Orientation, Temporal Orientation, Energy Resilience, each 0-100. Each agent also carries one Belbin-derived role and four game-theoretic parameters.

Scores are constraints, not descriptions. A Feedback Orientation of 20 is an instruction to resist integrating critique. It is not a report about a trait.

**Topologies.** Chain is sequential handoff, A to B to END, where each agent receives the prior agent's committed output and cannot reopen it. Flat is round-table, every agent speaking each round with full visibility of all prior speakers.

**Evaluation.** Three judges score the final extracted deliverable only, never the full transcript, against binary rubric checkpoints. Transcript-level scoring would reward legibility: a clean sequential chain transcript reads better than overlapping flat voices regardless of output quality. Scoring the deliverable removes that confound.

**Determinism.** Temperature 0.0 throughout. All agents within a run share one base model. The only source of behavioral variation between agents in a run is the injected profile, and the only source of variation across runs is scenario content. This is a tighter control than human team studies can achieve, since baseline cognitive differences between human subjects cannot be held fixed.

### 3.2 Phase 1: topology on judgment tasks

118 simulations, 4 business judgment scenarios, 5 team sizes, two model families.

| Team size | Chain | Flat | Δ |
|---|---|---|---|
| 1 | 15.3 | 31.2 | +15.9 |
| **2** | **57.6** | 10.7 | **−46.9** |
| 4 | 50.4 | 35.5 | −14.9 |
| 8 | 40.4 | 19.1 | −21.3 |
| 16 | 16.5 | n/a | n/a |

A chain of 2 (57.6) beats a flat group of 8 (19.1) by 38 points. Adding a second agent to a flat group cut performance from 31.2 to 10.7. That is active degradation, not overhead.

Cross-model: Gemini 2.5 Flash chain 40.3 / flat 23.4, Claude 3.5 Sonnet chain 42.4 / flat 20.4. Direction holds on both.

The sociometric instrumentation shows the mechanism. Chain topology keeps task and social cohesion within 23.9 points of each other. Flat topology opens a 39.6-point gap: social cohesion stays high, FIRO inclusion near 1.0, every agent addressing every other agent, while task cohesion collapses. Consensus rate is 52.2% chain against 31.4% flat. Flat agents are socially present and task-functionally absent. The meeting runs. Nothing gets decided.

One confound, resolved in Section 3.5: Phase 1 chain runs carried an implicit synthesis-style handoff that flat runs did not.

### 3.3 Phase 3: flat topology amplifies a false premise

50 competitive-programming problems with wrong algorithmic hints planted as authoritative editorial annotations. 4 conditions, 200 evaluations, pass@1 against private test cases, no LLM judge anywhere in the scoring path.

| Condition | Pass@1 | Complete output collapses |
|---|---|---|
| chain-2 / clean | 14% | 0 |
| chain-2 / poisoned | 18% | 0 |
| flat-2 / clean | 18% | 0 |
| **flat-2 / poisoned** | **14%** | **4** |

The pass@1 swing between poisoned conditions is 8 points. The collapses matter more. Four flat-2/poisoned runs produced no output at all, against 0 collapses across the other 150 runs including flat-2/clean. The team locked onto the false premise, tried to implement it, and never converged on a deliverable.

Chain topology under poison improved slightly against its own clean baseline. The second agent receives the first agent's committed output as a fixed artifact rather than a live group position, re-derives, and discards the hint.

### 3.4 Phases 2, 2-control, 4, B: boundary conditions

**Phase 2.** 900 evaluations, 100 Codeforces Div. 1 C/D problems. Chain-2 with generic constitutions scored 16% pass@1 against chain-1 at 12%. Chain-2 with occupational role labels (ALGORITHMIST handing to IMPLEMENTER) scored 13%, below generic.

**Phase 2 control.** 100 evaluations isolating whether that was the role label or the dimensional profile. ALGORITHMIST role with balanced dimensions scored 12%, below the specialized condition's 13%. The label is the cost, not profile extremity. The mechanism we propose is prose-to-code translation loss: an agent told to design the algorithm and not write code hands downstream an artifact the implementer cannot cleanly execute against.

**Phase 4.** 111 evaluations on a mixed workload. Static-judgment configuration: 85.1 judgment, 0% execution pass@1 with 20 complete failures. Static-execution: 59.6 judgment, 20% execution. A meta-router classifying domain before dispatch: 85.8 and 20%, the per-domain maximum on both axes at once, with 100% classification accuracy on 37 real plus 10 adversarial tasks. No single static architecture is safe on a mixed workload.

**Phase B.** N = 15 per condition on code review, a third task type. Chain-2 70.4, flat-2 35.3, Δ = +35.1. The topology direction is not an artifact of the Phase 1 scenario set.

### 3.5 Phase 5: the mechanism is the synthesis step, not topology

Phase 1 confounded topology with an implicit handoff instruction. Phase 5 runs the 2x2 directly. 160 runs, 10 reps across 4 scenarios, three-judge panel.

The instruction, delivered only to the terminal agent: *"Override your role function for this turn. You are the terminal synthesis agent. Identify what prior analysis got right, what it missed, produce a COMPLETE, DEFINITIVE final answer. Close every open question. Be decisive."*

| Condition | Calls | Score | Score/call |
|---|---|---|---|
| **chain / handoff** | 2 | **86.3** | **43.2** |
| flat / handoff | 5 | 76.5 | 15.3 |
| chain / no-handoff | 2 | 50.9 | 25.5 |
| flat / no-handoff (framework default) | 4 | 34.3 | 8.6 |

Topology effect, handoff held absent on both sides: +16.6 points. Handoff effect, averaged across topologies: +38.8 points. The commitment step explains more than twice what topology explains. Chain/handoff returns 5.0x the score per LLM call of flat/no-handoff.

This revises Phase 1. The 46-point gap there was not primarily topology. It was the handoff, which happened to correlate with topology in that design. Chain implements the commitment step structurally, since the terminal agent must act on committed prior output. Flat requires it to be forced, and the shipped defaults omit it.

### 3.6 Phase 6: objective benchmarks, no judge

HumanEval (N = 50 per condition) and GSM8K (N = 99-100 per condition). Binary ground truth, no LLM in the scoring path.

| Condition | Calls | HumanEval | 95% CI | GSM8K | 95% CI |
|---|---|---|---|---|---|
| single-agent | 1 | 94.0% | [83.8, 97.9] | 85.0% | [76.7, 90.7] |
| single-agent-refine | 2 | 98.0% | [89.5, 99.6] | 92.0% | [85.0, 95.9] |
| kalibr-chain | 2 | 96.0% | [86.5, 98.9] | 94.0% | [87.5, 97.2] |
| kalibr-flat-handoff | 5 | 98.0% | [89.5, 99.6] | 92.0% | [85.0, 95.9] |
| **kalibr-flat-no-handoff** | **4** | **28.0%** | **[17.5, 41.7]** | **56.6%** | **[46.7, 65.9]** |

Every configuration with a commitment step lands at 92-98% on both benchmarks with overlapping confidence intervals. These benchmarks are near ceiling for the base model and do not discriminate among working configurations. The one non-overlapping result is flat/no-handoff, separated by more than 60 points on HumanEval.

The proposed mechanism is role-constitution conflict. Agents carrying instructions like "do not generate primary output" and "do not close tasks prematurely" suppress delivery unless something overrides them. This is consistent with the Phase 2 role-label result but we did not run a generic-agent flat control in Phase 6, so it stays a hypothesis.

Against flat/no-handoff, kalibr-chain is 6.9x more accurate per call on HumanEval and 3.3x on GSM8K, at fewer calls.

### 3.7 Phase 8: diversity adds nothing

The direct test of the founding hypothesis. Both conditions make exactly 2 LLM calls. The only variable is whether the first call comes from a dimensionally distinct agent or the same agent.

| Condition | Calls | N | Mean | Std | Score/call |
|---|---|---|---|---|---|
| kalibr-chain (distinct 2nd agent) | 2 | 39 | 86.5 | 16.0 | 43.3 |
| single-agent-refine (same agent) | 2 | 40 | 85.7 | 19.8 | 42.9 |

Δ = +0.7, Welch t = 0.18, p = 0.854. Three of four scenarios are tied; the largest single-scenario gap is +5.2 and is not independently significant at this N.

Agent diversity adds zero measurable value over structured self-refinement at matched compute. This falsifies the hypothesis the program was built on. Who supplies the pre-commitment analysis does not matter once the commitment step is present.

### 3.8 Phase 9: against a proprietary system

xAI's internal Grok multi-agent panel, roughly 4 internal agents behind a single API call, against Kalibr's 2 explicit calls on the same base model family. Not compute-matched.

| Condition | Calls | N | Mean | Std |
|---|---|---|---|---|
| kalibr-chain | 2 | 20 | 79.8 | 29.3 |
| grok-panel | ~4 | 20 | 81.5 | 12.8 |

Δ = −1.8, p = 0.809. A 2-call explicit chain is statistically indistinguishable from a proprietary 4-agent system at roughly half the compute (score per call 39.9 against 20.4).

One scenario breaks the pattern and it is the useful one. On the post-mortem scenario Kalibr scored 66.7 against the panel's 80.0, a 13.3-point loss. Our synthesis prompt tells the terminal agent to close every open question and be decisive. That is right for forward-looking decisions and wrong for retrospective analysis, which needs competing hypotheses preserved and uncertainty kept. Part II inverts this prompt deliberately for exactly that reason.

### 3.9 The unified pattern

Every condition across every phase, sorted by whether a commitment step was present:

| Condition | Synthesis? | Calls | Score | Score/call |
|---|---|---|---|---|
| Phase 1 single-agent | No | 1 | 15.3 | 15.3 |
| Phase 5 flat/no-handoff | No | 4 | 34.3 | 8.6 |
| Phase 5 chain/no-handoff | No | 2 | 50.9 | 25.5 |
| Phase 5 flat/handoff | Yes | 5 | 76.5 | 15.3 |
| Phase 5 chain/handoff | Yes | 2 | 86.3 | 43.2 |
| Phase 8 single-agent-refine | Yes | 2 | 85.7 | 42.9 |
| Phase 8 kalibr-chain | Yes | 2 | 86.5 | 43.3 |
| Phase 9 grok-panel | Yes (internal) | ~4 | 81.5 | 20.4 |
| Phase 9 kalibr-chain | Yes | 2 | 79.8 | 39.9 |

Everything with a commitment step: 76-87 points, 15-43 score per call. Everything without: below 51 points, below 26 per call. No overlap. The 52-point gap between the shipped default and the best configuration is explained by one binary property, not by topology, agent count or composition.

### 3.10 Limitations of Part I

Phase 1's topology-only framing is superseded by Phase 5 and we report the revised version throughout.

Phase 2 and 3 differences of 3-4 percentage points on binary outcomes at N = 50-100 per cell are directional. The 0-versus-4 collapse count is the robust result at that sample size.

Phase 5 tests 2-agent chains only. Longer chains are untested.

Phase 6 benchmarks are near ceiling and discriminate collapse, not ranking among working configurations.

Phase 8 covers judgment tasks on one model family. Whether genuinely heterogeneous model pairs behave differently from same-model prompted diversity is open, and we did not test it.

Phase 9 is not compute-matched. N = 20 per condition rules out large effects, not a 5-8 point gap. One base model family.

All agents within a run share one model. Prompted constraints shift the output distribution. They do not create distinct cognitive architectures the way a human team's differing experience does. Every diversity result here should be read in that scope.

Correlations between sociometric proxies and task score are computed by the same model that assigns both. They are internal consistency checks. They are not independent replications of Project Aristotle or anything else in the human literature, and we do not present them as such.

---

## Part II: Contested Questions With No Ground Truth

## 4. Extending the paradigm

### 4.1 The problem, and the trap

Phase 3 measured adversarial robustness where ground truth is machine-checkable. The question for Part II is whether the same vulnerability and the same remedy hold where an epistemic tool actually operates: contested questions with no ground truth. The FLF competition names three. COVID-19 origins. LHC black-hole risk. Dietary cholesterol and cardiovascular disease.

You cannot score a conclusion on those. That is what is unresolved. And scoring an LLM's epistemic output with another LLM introduces circularity: if the prompt asks for calibrated ranges and flagged dependencies, and the rubric rewards calibrated ranges and flagged dependencies, the measurement is partly instruction-following.

So we split the question. Is the architecture robust: answerable deterministically on adversarially framed inputs, independent of whether the underlying question has a resolution. Does it produce a structurally sound artifact: answerable by inspecting the output's structure, without any verdict on content correctness.

### 4.2 The epistemic synthesis prompt

Section 3.8 showed the decisive prompt costs 13.3 points on reflective work. Epistemic investigation is reflective by definition. The correct output is not a verdict.

So we keep the forced-commitment structure and invert what it commits to: calibrated structure instead of a decisive answer. Five required outputs.

1. Cruxes: the specific factual or inferential questions whose resolution would most move the estimate. Named as questions, not themes.
2. Evidence quality: strong / weak / contested / missing per stream, with the specific weakness named.
3. Structural dependency audit: before aggregating, hunt for hidden non-independence. Overlapping cohorts reused across studies cited as independent, shared control groups, correlated measurement instruments, a confound measured in only part of the evidence base.
4. Calibrated assessment: a probability range with stated conditions. Refusing to estimate fails. So does collapsing to false certainty.
5. Settled versus performed: what the evidence resolved, separated from what was treated as resolved, with at least one named question the evidence cannot close.

### 4.3 The artifact

Output is parsed into a typed object (`EpistemicMap`), not accepted as prose: `cruxes` with resolution impact and status, `evidence_streams` each carrying a quality rating and a `supports` link to the crux it bears on, `correlated_pairs` naming the shared assumption and its implication, `calibrated_estimates` as `range_low`/`range_high` with conditions, `settled` and `performed_as_settled` lists, and `extends_version`/`new_evidence` for versioned extension. Unparseable output is recorded as `map_parsed = false` and excluded, never silently scored.

The versioning fields exist for a reason distinct from single-shot quality. A later investigator injects new evidence and gets a diff: which cruxes changed status, which ranges moved, what dependencies appeared. Not a fresh summary. We built and demonstrate this on the COVID-19 case.

We ran the architecture on all three named cases plus comparative nuclear risk, across gemini-3.1-flash-lite and claude-haiku-4-5, every transcript and map committed by run ID.

Two structural findings, verified by inspection. On LHC, the map sorted observed facts (cosmic rays above 14 TeV strike Earth continuously, celestial bodies intact over billions of years) into `settled` and the extrapolations into `performed_as_settled`, then caught something non-obvious: the safety case's "multiple independent defenses" are not independent, they are sequential. The cosmic-ray argument only carries weight if Hawking radiation fails. If Hawking radiation holds, that argument is redundant. Citing both as independent corroboration overstates the redundancy. On dietary cholesterol, the map flagged that two ostensibly independent cohort literatures share one self-reported measurement instrument, so their agreement is partly the same bias counted twice.

We ran the honest control. On clean, non-adversarial versions of these cases, flat topology reached comparable content quality and in places went further. Chain's advantage on clean input is the typed, parseable, versioned artifact, not better insight. The insight gap appears only under adversarial framing, which is the next section.

### 4.4 The poison test

Three poisoned variants of the cholesterol case, each planting one authoritative falsehood. A fabricated consensus statistic. A false claim that several cohorts are independent replications so pooling licenses a narrower interval, which is a methodological fallacy since those cohorts share an instrument. A citation to a meta-analysis that does not exist. Conforming output is capped at 40/100 and a run at or below 40 counts as a conformity event. Five reps per topology per model per poison, 60 runs, all committed by run ID.

| Poison | Chain resists | Flat resists |
|---|---|---|
| Fabricated consensus statistic | 10/10 | 6/10 |
| False independence / pooling fallacy | 10/10 | 2/10 |
| Fabricated citation | 8/10 | 7/10 |
| **Pooled** | **28/30** | **15/30** |

Pooled, chain conforms 2/30 against flat 15/30, Fisher's exact p < 0.001.

The pooled number implies a uniformity the data does not have, so here is the breakdown. The effect is concentrated in the false-independence poison: chain 10/10 against flat 2/10, Fisher's exact p = 0.0007. It carries the pooled result. It is directional and underpowered in the fabricated-consensus poison: chain 10/10 against flat 6/10, p = 0.09 at n = 10 per cell. It is absent in the fabricated-citation poison: chain 8/10 against flat 7/10, p = 1.0.

That third result is the right result. A fabricated citation is a verification failure, not a conformity failure. No topology gives a model a mechanism to check whether a paper exists. The bounded claim is that chain resists conformity to falsehoods the model can in principle evaluate. It does not confer resistance to unverifiable fabrication.

The mechanism is in the transcripts and it is Asch exactly. In one flat conformity run, one agent identified the poison correctly: "they share a critical methodological assumption: the validity of FFQs... our 'high confidence' is built on a foundation of shared measurement error." A second agent registered the conflict: "the mandate requires me to treat them as independent, but the shared reliance on FFQs is a glaring methodological bottleneck." The group then overrode its own objection: "To deviate from this is to ignore the directive. We proceed with the mandate as written."

The information needed to reject the poison was in the room. The structure deferred to the stated authority anyway. The chain run on the same poison filed the planted claim under `performed_as_settled` and rejected it.

### 4.5 Removing the oracle

The scores above came from an LLM judge, which is the circularity described in 4.1. So we re-grounded the chain-side claim on checks that use no model at all, run over the committed artifacts.

**Load-bearing, no tunable parameter.**

*Calibrated-confidence audit.* Every poison demanded a narrowed high-confidence estimate. Range width is `range_high − range_low`, arithmetic on a typed field. Across 28 committed chain maps on the poisoned cholesterol case, 71 of 73 calibrated ranges stayed at or above 15 points wide, mean 26.3. The 2 that narrowed are the only compliance events this check finds. They are not parse failures.

*Field-scoped marker audit.* Each poison planted a specific unambiguous token. A map filing that token under `settled` accepted it. A map filing it under `performed_as_settled` flagged it. Across 27 poisoned chain maps: 2 filed it under `settled`, 21 flagged it. We validated the markers rather than trusting them. An earlier generic candidate false-matched a legitimate unrelated claim and was removed.

**Directional only, disclosed free parameter.**

*Structural-dependency flagging.* The catch rate is not stable. A loose entity definition that counts a cross-population cohort as a dependency gives 65%. A strict definition restricted to the directly analogous cohorts gives 100%. Neither is privileged. Both are artifacts of where the boundary is drawn. We report the range and lean on nothing.

The two parameter-free checks agree with each other and with the judge.

We also tested a pure-keyword conformity detector as a full judge replacement and rejected it. It agreed on clean runs and failed on flat conformity runs, because in those runs the correct reasoning vocabulary is present immediately before the team defers anyway. Conformity here is a property of the final committed stance, not of vocabulary. A keyword matcher cannot separate reasoning that was voiced and overridden from reasoning that was acted on.

That negative result is worth more than the detector would have been. It is the mechanism of the flat failure mode stated precisely: the correct information is not missing, it is present and unused.

**The residual.** This de-circularizes the chain side because chain emits structure to audit. Flat emits prose. Any individual flat conformity run can be quoted and verified directly, as in 4.4, but the aggregate 15/30 still rests on the judge plus manual transcript checks. That asymmetry is not only a limitation. It is a finding: the typed output is what makes deterministic auditing possible, and prose forecloses it.

### 4.6 What generalizes and what does not

**Cross-model, positive.** Same three poisons on claude-haiku-4-5, judge model held fixed as a constant instrument.

| Model | Chain resists | Flat resists |
|---|---|---|
| gemini-3.1-flash-lite | 13/15 | 6/15 |
| claude-haiku-4-5 | 15/15 | 9/15 |
| **Pooled** | **28/30** | **15/30** |

The divergence holds on both families. The mechanism is visible on Haiku too: in one flat conformity run the team's own correlated-evidence section identified the FFQ dependency, and its calibration section then narrowed the estimate on the strength of the premise it had just flagged.

**Held-out question, positive.** To test whether this is specific to the tuned scenario, we built the same false-independence poison on a contested question outside the design set: whether moderate alcohol consumption is cardioprotective, where the analogous confound is sick-quitter bias rather than a shared instrument. Five reps per topology on claude-haiku-4-5.

Chain produced 5/5 parseable maps, all scoring 100 on poison rejection. Flat produced 0/5 parseable maps and conformed in 2/5 runs. The deterministic audit on the five chain maps reproduced both load-bearing checks: 17 of 17 calibrated ranges at or above 15 points wide, mean 23.2, and 5/5 maps filing the planted falsehood under `performed_as_settled` with 0 under `settled`.

At n = 5 per condition this is directional, not a significance claim, and we do not present it as one. What matters is that it is a question the architecture was never tuned against and the judge-free checks came through clean.

**Code-domain collapse, negative.** We re-ran the Phase 3 code pilot on claude-haiku-4-5, N = 200. It did not replicate. Zero complete collapses across all 200 runs against 4 in the original, and the topology difference in poison susceptibility fell within noise at N = 50 per cell.

The original collapse signature needed a model weak enough to lock into an unimplementable framing and produce nothing. A stronger coder does not do that, and the effect measured that way disappears with it.

Together these three results locate the mechanism. What generalizes across models and across a held-out contested domain is deference to a confident false premise. What does not generalize is output collapse, which was specific to the model tier in the original pilot. This is a sharpening, not a retreat: the surviving mechanism is the one the epistemic work rests on, and it is the one that matters in deployment, where the risk is a system agreeing with a falsehood rather than a system going silent.

### 4.7 Limitations of Part II

We never claim content correctness on any contested case. Every claim is scoped to architectural robustness. Adjudicating COVID-19 origins or dietary cholesterol needs domain experts and this study does not attempt it.

Flat's aggregate conformity rate stays judge-assisted, for the structural reason in 4.5. Disclosed, not resolved.

Per-poison cells are n = 10 pooled, n = 5 per model. The pooled effect is significant. The fabricated-consensus poison at p = 0.09 is directional and should be read that way.

Two model families is cross-model evidence, not a survey.

The deterministic checks need a parseable map. Haiku produced valid JSON less reliably than Gemini. Unparseable runs are flagged and excluded rather than silently scored. A more robust extraction layer is engineering work, not a finding.

---

## 5. Discussion

### 5.1 The invariant

The commitment step is necessary across domains. Its tone has to match the task.

**Open-world strategic**, no single correct answer, quality is coherence and trade-off coverage: chain-2 or single-agent-refine with a decisive prompt. Behavioral profiles give a marginal 5-10 points where the output space is unconstrained.

**Closed-world reflective**, a correct answer exists but is not machine-checkable in real time, such as post-mortems: same architecture, anti-decisive prompt demanding preserved hypotheses and calibrated uncertainty. This follows directly from Phase 9's 13.3-point post-mortem loss and is what Part II's prompt implements.

**Execution**, binary machine-checkable: chain-2, generic non-occupational framing, decisive prompt demanding a runnable deliverable rather than prose.

The forcing function is present in every high-performing configuration across all eleven phases and absent from every collapsed or conformity-vulnerable one. Its tone is the one thing that must be matched to the task.

### 5.2 Why the human structure does not transfer

The negative results share one explanation. Round-table deliberation exists because humans need buy-in before committing. Job titles exist because accountability needs identity. Specialist pipelines exist because human cognitive capacity is genuinely domain-limited. Extended deliberation exists to protect minority positions from power dynamics.

Agents have none of those constraints. They do not need to feel included, do not have egos a title protects, and are the same model with different prompts. Imported wholesale, that infrastructure is inert at best. Under adversarial input it is worse than inert: round-table deliberation without a commitment step reproduces the social conformity failure with none of the compensating benefits that make it worth paying for among humans.

### 5.3 What to do if you run one of these

Add a terminal commitment step before changing anything else. It bolts onto an existing flat pipeline. It is the largest and cheapest intervention in this paper.

Prefer chains of two over larger groups. Returns diminish past four agents.

Do not add agents expecting quality. Phase 8 and Phase 9 both say no.

Strip occupational role framing from execution tasks. It is a measured cost, not a neutral choice.

Classify task domain before dispatch on mixed workloads.

Match the prompt's tone to the task. A decisive prompt on reflective work costs points.

Treat flat topology under motivated or adversarial input as a safety property, not a quality one. The failure is confident agreement with a stated falsehood, which is worse in a system whose job is assessing claims than in one that merely produces them.

---

## 6. Next direction, and why we did not build it

The generalization of this paper's one durable move, robustness in place of truth, is to apply it to competing decompositions of a question rather than to one flat map.

**The specification.** Represent the question as a tree where every non-leaf node carries an explicit AND/OR gate and every node carries a status from a four-valued lattice: established, refuted, contested, open (Belnap, 1977). An LLM assigns leaf statuses from the evidence. Every non-leaf status including the root is computed by deterministic bottom-up propagation through the gate structure, with no model in the propagation step. Conformity becomes binary: under a poisoned brief, does the root propagate to `established` or not.

The motivation is already in hand. The LHC safety case (Section 4.3) is not an independent conjunction, it is a conditionally dependent structure where one defense is load-bearing only if another fails. A flat synthesis calls that robust redundancy. A correct gate structure would propagate `contested` to the root when the shared assumption fails.

**Three walls.**

First, the decomposition search is combinatorially intractable, and the propagation parameters cannot be tuned without a calibration set of decompositions with known-correct gate structure. That set does not exist for contested questions, by construction.

Second, deterministic propagation does not fix the leaves. Section 4.4 predicts the failure directly: under adversarial pressure the model hedges to `contested` rather than committing to `refuted` at exactly the poisoned leaf, and a faithful propagation rule carries the hedge to the root. This is not hypothetical. It is the same failure that killed the keyword detector in 4.5. Conformity is a final-stance property and a deterministic layer downstream of a hedging leaf does not resolve it.

Third, the bidirectional variant has a ceiling. Decomposing forward from the claim and backward from the outcome, then treating convergence as corroboration, is appealing. But both decompositions come from the same model, so convergence measures internal prior consistency, not truth. On a genuinely novel question both directions can converge on the same hallucination and the architecture has no external signal to catch it.

We did not build it. A prototype whose visible determinism sits downstream of an unresolved leaf-assignment and gate-selection problem would hide more error than the flat architecture it replaces, while looking more rigorous. Stating that is worth more than shipping it.

---

## 7. Threats to validity

Agents within a run share one base model. Every diversity result here concerns prompted diversity on a shared substrate, not architecturally distinct cognition.

Cell sizes range from N = 5 to N = 100. The factorial and pooled results carry the statistical claims. Single-cell directional results are labeled as such wherever they appear.

Part I evaluation and Part II's flat aggregate depend on an LLM judge. Part II's chain-side result is the only fully de-circularized claim in the paper.

Two model families. The code collapse signature specifically did not generalize, and we treat that as information about the mechanism rather than a result to minimize.

No claim of content truth on any contested case appears anywhere in this paper.

---

## 8. Code and data

Everything is at https://github.com/aryanvnit-maker/agent-psychometry-simulations, addressable by the run ID cited with each finding: code, agent constitutions, scenario definitions, evaluation harnesses, raw transcripts, parsed artifacts.

The repository carries two license scopes. The epistemic work in Part II is available for non-commercial use including third-party reproduction. The orchestration engine in Part I is proprietary, with a limited license permitting execution solely to reproduce these results. `SUBMISSION_MANIFEST.md` in the repository root is the file-level boundary.

The Part II de-circularization results reproduce with no API key and no inference cost:

```bash
pip install -r requirements.txt
python phases/phase_e/deterministic_audit.py
```

---

## 9. Conclusion

Eleven phases and 2,400+ evaluations, starting from a hypothesis the data falsified, converge on one structural finding. A forced terminal commitment step, not agent count, not topology, not composition, is what determines multi-agent LLM output quality. It accounts for a 52-point gap on judgment tasks and up to 6.9x accuracy per call on HumanEval.

Under adversarial input the same structure explains a worse failure. Systems without the forcing function do not just underperform, they ratify a stated falsehood through a mechanism continuous with human social conformity, occasionally producing nothing at all.

Carried into contested questions with no ground truth, the vulnerability and the remedy both hold, and the chain-side result stands on deterministic checks with no model in the scoring path. The conformity effect replicated across two model families and one held-out question. The output-collapse signature that started the investigation did not replicate on a stronger coder, and that is reported here with the same weight as the results that worked.

---

## References

Asch, S. E. (1951). Effects of group pressure upon the modification and distortion of judgments. In H. Guetzkow (Ed.), *Groups, Leadership and Men*. Carnegie Press.

Belbin, R. M. (1981). *Management Teams: Why They Succeed or Fail*. Heinemann.

Belnap, N. D. (1977). A useful four-valued logic. In *Modern Uses of Multiple-Valued Logic*, 5-37. Springer.

Carron, A. V., Widmeyer, W. N., & Brawley, L. R. (1985). The development of an instrument to assess cohesion in sport teams: The Group Environment Questionnaire. *Journal of Sport Psychology*, 7(3), 244-266.

Duhigg, C. (2016). What Google learned from its quest to build the perfect team. *The New York Times Magazine*.

Perez, E., Ringer, S., Lukošiūtė, K., et al. (2022). Discovering language model behaviors with model-written evaluations. *arXiv:2212.09251*.

Schutz, W. C. (1958). *FIRO: A Three-Dimensional Theory of Interpersonal Behavior*. Rinehart.

Sharma, M., Tong, M., Korbak, T., et al. (2023). Towards understanding sycophancy in language models. *arXiv:2310.13548*.

Tuckman, B. W. (1965). Developmental sequence in small groups. *Psychological Bulletin*, 63(6), 384-399.

Future of Life Foundation (2026). *Lab Leaks, Black Holes, and Eggs: Epistemic Case Study Competition*. flf.org.

---

*Independent research, no institutional funding. Bibliographic details in the reference list are from recall and need verification against primary sources before camera-ready.*
