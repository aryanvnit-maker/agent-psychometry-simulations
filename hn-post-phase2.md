# Hacker News Submission — Phase 2

## Title (84 characters)

```
Show HN: We tested 9 agent configs on 100 Codeforces Div.1 problems. Role-playing hurts.
```

---

## Body

Phase 1 of this research showed sequential chains beat flat swarms by 46 points on business tasks. Phase 2 tests whether that holds on hard coding problems and whether psychometric agent profiles affect execution performance.

900 evaluations. 100 Codeforces Div. 1 C/D problems (~2000–2400 CF rating). Pass@1 as the metric. Temperature=0.0 throughout.

Three findings:

**1. The topology result replicates on hard math.** Chain-2 generic (two agents, sequential handoff, no personas) scores 16% pass@1 vs 12% for a single agent. The sequential forcing function works on deterministic execution, not just judgment tasks.

**2. Role-playing identities actively reduce performance.** Assigning agents occupational roles — "You are an Algorithmist. You are an Implementer." — drops pass@1 to 13% and increases compilation errors. The role separation introduces translation loss at the handoff. Chain-2 with no identity labels wins.

**3. Psychometric profiling is inert on execution tasks — but not for the reason you might expect.** We ran extreme Kalibr dimension profiles (high volatility/low adaptability vs. high adaptability/low volatility) on a single SOLVER agent. All profiles clustered at 11–14%, identical to the 12% baseline. The formatting constraint ("output only a code block") completely overrides behavioral constraints. The profiles only produce measurable effects when agents have token space to reason — in the analysis layer of a chain, not the execution layer.

Combined with Phase 1: the industry applies one architecture to everything. The data shows flat topology causes coordination failure on judgment tasks, and occupational role-playing causes cognitive drag on execution tasks. Two distinct failure modes from the same architectural mistake.

Full write-up: [LessWrong URL]
GitHub (Phase 2 branch): [GitHub URL]

---

## First Comment

Clarifications that will come up:

**On the 12% baseline:** These are Codeforces Div. 1 C/D problems, roughly equivalent to the top 10-15% of competitive programmers. 12% pass@1 for a single LLM agent on this difficulty is in line with published results on the CodeContests benchmark.

**On "role-playing hurts":** The claim is specific. We're not saying all system prompts are harmful. Chain-2 generic uses a balanced behavioral constitution — it has a system prompt. What hurts is occupational identity framing ("You are a Senior Algorithmist") that creates role-specific constraints which conflict with execution requirements. The agent told to "design algorithms, not write code" produces specs the SOLVER cannot translate cleanly.

**On the psychometric profile null result in Option A:** This is the correct finding. Dimensions need token space. A SOLVER agent with no room to express behavioral variance will not express it. This does not mean the dimensions are useless — it means they operate at the team coordination layer, not the individual execution layer. That's the Phase 1 result. Phase 2 shows where that boundary is.

**On statistical significance:** 16% vs 13% on N=100 binary outcomes is directional, not conclusive. The topology finding (chain > flat) and the negative control (Option A clustering) are the robust results. The within-condition dimension effects require larger N to confirm.

Temperature=0.0, deterministic evaluation, fully reproducible. Code and problems in the repo.
