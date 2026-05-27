# Hacker News Submission — All Phases Combined

## Title (87 characters)

```
Show HN: 1,429 evals — flat agent swarms underperform chains by 46 points. Here's why.
```

---

## Body

Five experiments, 1,429 evaluations, temperature=0.0 throughout.

The core finding: a chain of 2 agents outperforms a flat swarm of 8 by 38 points on judgment tasks. Adding agents to a flat swarm makes it worse, not better. Cross-model replicated on Gemini 2.5 Flash and Claude 3.5 Sonnet.

The mechanism is measurable. GEQ sociometric data shows flat topology produces a 39.6-point divergence between social cohesion (high — agents engage constantly) and task cohesion (collapsed — nobody commits). Consensus rate: chain 52.2%, flat 31.4%. The meeting is productive. The meeting does not produce a decision.

Three follow-on experiments:

**Coding tasks (900 evals, Codeforces Div. 1 C/D):** Chain-2 generic (16% pass@1) beats specialized ALGORITHMIST → IMPLEMENTER (13%). A control condition isolated the cause: the role instruction ("design the algorithm, do not write code") enforces a prose→code translation step the downstream agent can't complete cleanly. The role is the culprit, not the profiles.

**Adversarial input (200 evals):** Wrong hints planted in problem prompts. Chain-2: +4pp under poison. Flat-2: −4pp. More importantly, flat-2/poisoned produced 4 complete task collapses — agents committed to an unimplementable framing and produced nothing. Chain-2: zero collapses across 100 poisoned runs.

**Mixed workloads (111 evals):** A 5-line classifier routing between two configs achieves per-domain maximum on both judgment and execution simultaneously. Any single static config collapses on one axis — static-judgment produces 0% pass@1 on coding (20 NoCode); static-execution drops 26 points on judgment.

Full write-up with all results, mechanisms, and limitations: [LessWrong URL]
GitHub (code, constitutions, raw results): [GitHub URL]

---

## First Comment

Anticipated objections:

**"Judge agents are just models — circular evaluation."** Judges scored only the final extracted deliverable against binary rubric criteria, not the full transcript. Three independent judges per run. The topology gap (46 points) is large enough that moderate judge variance doesn't move the conclusion. The coding results (Phase 2/3) use objective pass@1 against private test cases — no judge involved.

**"13% vs 16% on coding isn't conclusive."** Correct. The topology finding (chain-2 > chain-1) and the NoCode collapse under adversarial input are the robust Phase 2/3 results. The 3pp persona degradation is directional. The control condition isolating the role instruction adds confidence but N=100 binary outcomes warrant caution.

**"Real systems use heterogeneous models."** Tested only within-model teams. Topology × model-heterogeneity interaction is untested and listed as an open question. The topology finding may change under heterogeneous teams — that's worth running.

**"I've seen personas help in production."** The claim is specific: the ALGORITHMIST role instruction ("design, do not write code") creates a prose→code translation step. Generic constitutions with behavioral dimensions but no occupational identity don't show this degradation. If your persona doesn't enforce a design/implement boundary, you may not see the effect.

**"118 Phase 1 runs is thin."** Agreed. Effect size confidence intervals are wide. The 46-point topology gap is robust; the per-composition differences are directional. Pre-registered replication is the right next step.

Temperature=0.0, seed-controlled where applicable, fully deterministic. All code, constitutions, datasets, and raw result files in the repo.
