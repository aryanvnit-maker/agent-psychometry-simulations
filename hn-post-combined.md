# Hacker News Submission — Combined Phase 1 + Phase 2

## Title (89 characters)

```
Show HN: 1018 AI agent evals, 2 studies. Flat swarms fail. Role-playing fails. Same mistake.
```

---

## Body

Two research phases. 1018 total evaluations. Temperature=0.0 throughout, fully deterministic.

**Phase 1** — 118 simulations across 4 business scenarios, 2 model families (Gemini 2.5 Flash + Claude 3.5 Sonnet), 5 team sizes, 3 compositions. Metric: 0–100 task score, rubric-graded against final deliverables only.

**Phase 2** — 900 evaluations on 100 Codeforces Div. 1 C/D problems (~2000–2400 rating), 9 agent configurations. Metric: pass@1 against private test cases. Binary ground truth.

Four findings across both phases:

**1. Sequential chains beat flat swarms on judgment tasks.** Chain-2 scores 57.6 vs flat-2's 10.7 — a 46.9-point gap. Cross-model replicated. The mechanism: flat topology produces social cohesion (agents engage, acknowledge, validate) while task cohesion collapses. Convergence requires entropy reduction at each step. Flat defers it indefinitely.

**2. The topology finding replicates on hard coding problems.** Chain-2 generic (16% pass@1) outperforms chain-1 (12%) on Div. 1 competitive programming. Sequential structure compresses entropy at the handoff even on deterministic math. The advantage is architectural, not task-specific.

**3. Occupational role-playing actively degrades coding performance.** ALGORITHMIST → IMPLEMENTER specialization drops pass@1 to 13% and raises compilation errors vs a generic chain-2 (16%). The role separation introduces translation loss: the ALGORITHMIST produces abstract specs the IMPLEMENTER renders as broken Python.

**4. Psychometric profiles are inert on the execution layer — the reason matters.** Extreme behavioral profiles on a SOLVER agent cluster at 11–14%, indistinguishable from the 12% baseline. The formatting constraint ("output only a code block") completely overrides behavioral constraints. Profiles only produce measurable effects when agents have token space to reason — the analysis layer, not the execution layer.

The combined result: the industry applies one architecture to everything. The data shows flat topology causes coordination failure on judgment tasks, and occupational role-playing causes cognitive drag on execution tasks. Two distinct failure modes from the same architectural mistake.

Phase 1 write-up: [LessWrong URL]
Phase 2 write-up: [LessWrong URL]
GitHub: [GitHub URL]

---

## First Comment

Clarifications that will come up:

**On the Phase 1 judge methodology:** Three independent judge agents scored each run. Judges evaluated only the team's final extracted deliverable against binary rubric criteria — not the full transcript. For chain topology the deliverable is the last agent's synthesized output; for flat it is the complete final round. This eliminates the formatting bias of evaluating chain vs flat transcripts directly.

**On the 12% coding baseline:** Codeforces Div. 1 C/D problems are where naive approaches fail and genuine algorithmic insight is required — roughly the top 10–15% of competitive programmers. 12% pass@1 for a single LLM agent on this difficulty is in line with published results on the CodeContests benchmark.

**On "role-playing hurts":** The claim is specific. Chain-2 generic uses a balanced behavioral constitution — it has a system prompt. What hurts is occupational identity framing ("You are a Senior Algorithmist") that creates role-specific constraints which conflict with execution requirements. The agent told to "design algorithms, not write code" produces specs the SOLVER cannot translate cleanly.

**On the psychometric null result:** This is the correct finding, not a failure of the framework. Behavioral dimensions require token space — room to reason, hesitate, and exhibit designated traits — to influence downstream logic. A SOLVER with a strict formatting constraint has no distribution to weight. The dimensions operate at the analysis layer, not the execution layer. That's the Phase 1 result. Phase 2 shows the boundary condition.

**On statistical significance:** The 46-point topology gap in Phase 1 is robust. The Phase 2 within-condition differences (16% vs 13% on N=100 binary outcomes) are directional, not conclusive. The topology finding and the negative control (psychometric profiles clustering at baseline) are the Phase 2 results to weight heavily.

Temperature=0.0, seed=42 (Phase 1), deterministic evaluation. Code and problems in the repo.
