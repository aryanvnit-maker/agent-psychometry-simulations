# Hacker News Submission — All Phases Combined

## Title (97 characters)

```
Show HN: 1,429 AI agent evals, 5 studies. Flat swarms fail. Personas fail. Same root cause.
```

---

## Body

Five research phases. 1,429 total evaluations. Temperature=0.0 throughout, fully deterministic.

**Phase 1** — 118 simulations, 4 business scenarios, 2 model families, 5 team sizes. Metric: 0–100 rubric score against final deliverables only.

**Phase 2** — 900 evaluations, 100 Codeforces Div. 1 C/D problems, 9 agent configurations. Metric: pass@1, binary ground truth.

**Phase 2 Control** — 100 evaluations isolating the ALGORITHMIST role effect from dimension profile effects.

**Phase 3** — 200 evaluations, wrong algorithmic hints planted in problem prompts, chain vs flat under adversarial input.

**Phase 4** — 111 evaluations, mixed workload, dynamic task classification and routing vs static configs.

Six findings:

**1. Chain-2 beats flat-8 by 38 points on judgment tasks.** Adding agents to a flat swarm makes it worse. The mechanism: flat topology produces high social cohesion and collapsed task cohesion simultaneously. GEQ data shows a 39.6-point divergence. Agents engage with everything and commit to nothing. Cross-model replicated.

**2. Topology replicates on hard coding problems.** Chain-2 generic (16% pass@1) outperforms chain-1 (12%) on Div. 1 competitive programming. The sequential forcing function compresses entropy at the handoff even on deterministic math.

**3. Occupational personas actively degrade coding performance — the role instruction is the culprit.** ALGORITHMIST → IMPLEMENTER scores 13% with more compilation errors than generic chain-2. The Phase 2 control (ALGORITHMIST role + balanced dimensions) scored 12% — lower than extreme profiles (13%), not higher. Extreme dimensions were marginally helping. The role instruction "design the algorithm, do not write code" enforces a prose→code translation step that costs 4pp and raises compilation errors. The SOLVER implements the spec faithfully and the spec is wrong.

**4. Flat topology is unsafe, not just slow, under adversarial input.** Chain-2 under wrong algorithmic hints: +4pp. Flat-2 under same hints: −4pp. 8pp swing. Four complete task collapses (NoCode) in flat-2/poisoned, zero in chain-2 across 200 evaluations. Chain-2's committed first-pass gives agent-1 space to reject the planted premise before agent-2 sees it. In flat topology, agent-2 validates whatever agent-1 accepted. Social cohesion becomes a vulnerability when the shared premise is wrong.

**5. No single static architecture handles mixed workloads.** Static-judgment config deployed globally: 85.1 on judgment tasks, 0% pass@1 on coding (20 NoCode — constitution blocks code output). Static-execution deployed globally: 59.6 on judgment, 20% on coding. A lightweight classifier routing between the two configs achieves 85.8 and 20% simultaneously. 100% routing accuracy on real tasks and adversarial Trojan tasks.

**6. Psychometric profiling only matters on open-world strategic tasks.** Kalibr profiles produce a 78-point gap on resource allocation (100 vs 22.2). Near-zero gap on closed-world deterministic tasks (post-mortem, crisis response). Profiles are neutral when tasks have verifiable answers. They are overridden entirely when formatting constraints are present (SOLVER). They only operate when the output space is unconstrained and token space allows reasoning.

The root cause of every failure: the industry imports human team management into agent systems. Humans need roundtables for buy-in, job titles for accountability, deliberation frameworks for power dynamics. Agents have none of those constraints. Every piece of that scaffolding is dead weight or worse.

Three rules derived from 1,429 evaluations: use chains of two, not rooms of many. Write no occupational personas for execution tasks. Classify the task before deploying the pipeline.

LessWrong write-up: [URL]
GitHub: [URL]

---

## First Comment

Clarifications that will come up:

**On the Phase 1 judge methodology:** Three independent judge agents scored each run against binary rubric criteria applied to final deliverables only — not the full transcript. This eliminates formatting bias between chain and flat transcript structures.

**On the 12% coding baseline:** Codeforces Div. 1 C/D problems require genuine algorithmic insight — roughly top 10–15% of competitive programmers. 12% pass@1 on this difficulty is consistent with published results on the CodeContests benchmark.

**On "personas hurt":** The claim is specific. The harm comes from role instructions that enforce a division of labour (design vs implement). The ALGORITHMIST role that says "do not write runnable code" creates a mandatory translation step at the handoff. A system prompt with behavioral dimensions but no occupational identity does not produce this effect.

**On the Phase 3 NoCode collapses:** These are not compilation failures — the agents produced no code at all. The wrong hint committed both flat agents to an algorithmic approach neither could implement. Chain-2 never exhibited this failure across 100 poisoned evaluations.

**On the meta-router 100% accuracy:** The classifier prompt is five lines. Gemini Flash, temperature=0, max_tokens=10. Validated on 10 adversarial Trojan tasks specifically designed to fool it — execution problems encoded as narrative scenarios and judgment problems formatted as technical specs. 10/10.

**On "the industry is wrong":** The claim is bounded. We have measured three task domains. The finding is that the two most common architectural defaults (flat roundtable, specialist pipeline) produce distinct failure modes in each domain tested. The correct architecture — small chain, minimal identity, classified routing — is simpler than what the industry is building and measurably better on every metric.

Temperature=0.0, deterministic evaluation throughout. Full codebase, constitutions, problems, and raw results in the repo.
