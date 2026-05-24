# Hacker News Submission

## Title (85 characters)

```
Show HN: I ran 118 AI simulations. Sequential chains beat flat swarms by 18 points.
```

---

## Body

The industry default for multi-agent AI is flat topology: all agents share a context window, deliberate simultaneously, and output in a round-table.

118 deterministic simulations tested this against sequential chain topology across four scenario types and two model families (Gemini 2.5 Flash and Claude 3.5 Sonnet).

Chain topology wins by 17–22 points on task scores (graded 0–100 against final deliverables only, not transcripts, to eliminate formatting bias). Adding agents past N=2 on a chain hurts performance monotonically. On bounded convergence tasks, a sequential chain of 2 agents mathematically outperforms a flat swarm of 8.

The mechanism is isolated in the sociometric data: flat topology produces massive social cohesion (agents acknowledge each other, build context) while task cohesion craters. Convergence requires entropy reduction at each step. Flat topology defers it indefinitely.

Strongest predictor across both topologies: whether agents acknowledge prior output before adding new content (r=0.70).

Code is public, fully reproducible at seed=42, temperature=0.0. Simulations use LangGraph, Supabase, and a 32-agent Kalibr psychometric pool to generate system constraints.

Full write-up: [LessWrong URL]
GitHub repo: [GitHub URL]

---

## First Comment (post within 60 seconds of submission)

Terminology upfront since it'll come up:

**Chain:** A→B→C→END. Each agent receives only the prior agent's output as input. No agent sees the full deliberation history — only the committed forward state.

**Flat:** All agents share a full context window. All agents respond each round. Two rounds per run.

**Judge methodology:** Three independent judge instances scored each run. Judges evaluated only the team's final extracted deliverable against hard binary rubric criteria — not the full transcript. For chain, the final deliverable is the last agent's synthesized output. For flat, it is the complete final round. This eliminates the structural formatting bias: a judge reading a chain transcript sees clean sequential reasoning; reading a flat transcript sees overlapping voices.

**On chain-1 vs chain-N:** A single agent with no handoff (chain-1) scores 15.3 — the lowest result in the dataset. The performance gain is in the handoff structure, not the final agent. Removing the chain collapses performance back to baseline.

All simulations run at temperature=0.0, seed=42. The full harness, agent pool, scenarios, and evaluation code are in the repo.

TL;DR for skeptics: flat topology agents collaborate well and produce weak deliverables. Chain topology agents barely interact and produce strong deliverables. That gap is the finding.
