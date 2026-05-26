# KalibrBench: Your Multi-Agent Architecture Is Losing You Performance

1,018 evaluations across two research phases. The industry default — flat topology, occupational role personas, parallel deliberation — produces measurable, reproducible performance collapse. The data is below.

---

## The Numbers

### Phase 1 — Business Judgment Tasks (118 simulations, 0–100 rubric score)

| Team Size | Chain (sequential) | Flat (round-table) | Δ |
|---|---|---|---|
| 1 agent | 15.3 | 31.2 | +15.9 |
| **2 agents** | **57.6** | 10.7 | **−46.9** |
| 4 agents | 50.4 | 35.5 | −14.9 |
| 8 agents | 40.4 | 19.1 | −21.3 |
| 16 agents | 16.5 | — | — |

A chain of 2 agents (57.6) outperforms a flat swarm of 8 (19.1). Cross-model replicated on Gemini 2.5 Flash and Anthropic Claude 3.5 Sonnet.

| Model | Chain | Flat | Gap |
|---|---|---|---|
| Gemini 2.5 Flash | 40.3 | 23.4 | −16.9 |
| Claude 3.5 Sonnet | 42.4 | 20.4 | −21.9 |

### Phase 2 — Hard Coding Tasks (900 evaluations, pass@1 on Codeforces Div. 1 C/D)

| Condition | Pass@1 | Compilation Errors |
|---|---|---|
| Chain-2 generic | **16%** | 22 |
| Chain-2 specialized (ALGORITHMIST → IMPLEMENTER) | 13% | 23 |
| Chain-1 generic (baseline) | 12% | 18 |
| Psychometric profiles on execution layer | 11–14% | — |

Occupational role personas ("You are a Senior Algorithmist") drop pass@1 by 3 points and raise compilation errors. Generic sequential handoff beats every specialized configuration tested.

---

## The Coordination Tax

When you add a second agent to a flat swarm, performance drops from 31.2 to 10.7 — a **46.9-point collapse**. That is not inefficiency. That is the Coordination Tax: the compute you pay for deliberation that never converges.

The mechanism is visible in the GEQ sociometric data. In flat topology, social cohesion and task cohesion diverge by **39.6 points**. Agents acknowledge each other, build rapport, address each other by turn — and produce no committed output. FIRO inclusion hits 1.0. Consensus rate drops to 31.4%. The meeting is productive. The meeting does not produce a decision.

In chain topology, the same agents with the same constitutions diverge by only **23.9 points**. Sequential commitment forces entropy reduction at each handoff. Each agent builds on a settled prior state. The chain decides.

This is Moloch in a synthetic system. It is substrate-independent. It is architectural.

**The industry applies one pattern to everything.** The data shows this produces two distinct failure modes:

- **Judgment tasks** (strategy, analysis, decisions): flat topology → social cohesion without task convergence → 46-point performance collapse
- **Execution tasks** (code, precise output): role-playing personas → translation loss at handoff → 3pp pass@1 drop, rising compilation errors

---

## Enterprise Coordination Tax Audit

KalibrBench is an open-source evaluation framework.

For enterprise teams running LangChain, CrewAI, AutoGen, or custom multi-agent pipelines: we conduct **Coordination Tax Audits** — localized benchmarks that measure topological token bloat in your specific pipeline, identify where flat deliberation is consuming compute without producing convergence, and restructure agent configurations toward the N=2 sequential optimum.

Engagements produce a written report with before/after pass@1 or task score measurements on your workloads.

**Contact:** aryan199841@gmail.com

---

## Reproduce the Findings

```bash
git clone https://github.com/aryanvnit-maker/agent-psychometry-simulations
cd agent-psychometry-simulations
pip install -r requirements.txt
cp .env.example .env  # add GEMINI_API_KEY

# Phase 1: business judgment benchmark (requires DATABASE_URL for Supabase)
python reproduce.py

# Phase 2: competitive programming benchmark (no database required)
python run_cp_baseline.py --n 100
python run_cp_experiment.py --n 100
python analyze_cp.py
```

Temperature=0.0, seed=42. Fully deterministic. Same inputs, same outputs.

---

## Methodology

### Agent Architecture

**32 worker agents** instantiated from the Kalibr psychometric framework. Each agent receives a *constitution* — a system prompt generated from 10 behavioral dimension scores.

| Dimension | What It Encodes |
|---|---|
| Philosophy Cohesion | Alignment between stated values and behaviour |
| Drive Alignment | Goal-directedness and task persistence |
| Bonding Index | Relational investment and trust-building |
| Adaptive Intelligence | Response quality under ambiguity |
| Volatility Vector | Emotional stability under pressure |
| Ambiguity Tolerance | Comfort with incomplete information |
| Influence Style | How the agent shapes group direction |
| Feedback Orientation | Openness to challenge and correction |
| Temporal Orientation | Short-term execution vs long-term thinking |
| Energy Resilience | Sustained output under sustained pressure |

Scores ≥70 produce high-expression behaviours. Scores ≤30 produce low-expression behaviours.

### Topologies

**Chain** — A → B → C → END. Each agent receives full history but produces output once, in order. No agent can reopen what a prior agent settled. Entropy is reduced at each handoff.

**Flat** — Every agent speaks once per round for two rounds, with full conversation history. Perfect information. No routing cost. No convergence mechanism.

### Phase 1 Evaluation

Three independent judge agents score each run's **final extracted deliverable** against binary rubric criteria. Not the transcript — the deliverable. For chain, the deliverable is the last agent's synthesized output. For flat, the complete final round. This eliminates the formatting bias of evaluating sequential vs parallel transcripts directly.

### Phase 2 Evaluation

Pass@1 against private test cases. Code executed via local subprocess. Binary ground truth — no rubric, no judge.

---

## Key Findings

**Finding 1 — Topology is architectural, not model-specific.** Chain outperforms flat by 17–22 points across Gemini 2.5 Flash and Claude 3.5 Sonnet. Same gap, different model families.

**Finding 2 — The Coordination Tax compounds with scale.** Adding agents to flat topology past N=1 actively degrades performance. Each additional agent increases social engagement and decreases task convergence. The N=2 chain is the empirical optimum for bounded tasks.

**Finding 3 — Occupational role personas introduce cognitive drag on execution tasks.** ALGORITHMIST → IMPLEMENTER role separation scores 13% pass@1 vs 16% for generic chain-2. The role constraints interact: the ALGORITHMIST over-specifies, the IMPLEMENTER under-executes.

**Finding 4 — Psychometric profiles require token space to operate.** Extreme behavioral profiles on a SOLVER agent (strict code-only output) cluster at 11–14%, identical to baseline. Formatting constraints override behavioral constraints. Profiles operate at the analysis layer, not the execution layer.

**Finding 5 — Psychological safety is the strongest cross-topology predictor.** r=0.70\*\*\* (chain) and r=0.65\*\*\* (flat). Diversity does not predict performance in either topology (r=−0.06, n.s.).

---

## Human Psychology Replication Status

| Human Finding | Source | AI Status |
|---|---|---|
| Cognitive diversity predicts performance | Bell (2007) | **Topology-dependent** — homogeneous wins on chain |
| Conscientiousness variance predicts performance | Barrick et al. (1998) | **Not replicated** |
| Psychological safety is the strongest predictor | Google Project Aristotle (2015) | **Replicated** — r=0.70\*\*\* |
| Task and social cohesion are distinct constructs | GEQ, Carron et al. (1985) | **Replicated** — 39.6-point gap in flat |
| Innovation climate predicts novel output | TCI, Anderson & West (1994) | **Replicated** — r=0.87\*\*\* |

---

## Project Structure

```
agent-psychometry-simulations/
├── src/
│   ├── agents/
│   │   ├── profile.py          # KalibrDimensions, AgentProfile, Role taxonomy
│   │   ├── constitution.py     # Dimension scores → behavioral system prompt
│   │   └── pool.py             # 32 workers + 3 judges, captain draft logic
│   ├── orchestration/
│   │   └── engine.py           # LangGraph graphs: chain, flat; handoff injection
│   ├── datasets/
│   │   └── codecontests.py     # CodeContests loader (Phase 2)
│   ├── execution/
│   │   ├── judge0.py           # Subprocess executor (Phase 2)
│   │   └── extractor.py        # Code block extraction from agent transcripts
│   ├── evaluation/
│   │   ├── judge.py            # 3-judge panel, final-answer-only evaluation
│   │   └── schema.py           # EvaluatorOutput Pydantic model
│   ├── scenarios/
│   │   └── library.py          # 4 business scenarios with rubrics
│   └── telemetry/
│       ├── database.py         # Supabase connection, insert_run
│       └── schema.sql          # runs + evaluations table definitions
├── run_all.py                  # Phase 1 batch runner
├── run_cp_baseline.py          # Phase 2 chain-1 baseline
├── run_cp_experiment.py        # Phase 2 all 9 conditions
├── run_phase3.py               # Phase 3 hallucination multiplier
├── analyze.py                  # Phase 1 analysis
├── analyze_cp.py               # Phase 2 analysis
├── analyze_phase3.py           # Phase 3 analysis
└── reproduce.py                # Single-command Phase 1 demo
```

---

## License

AGPLv3. Open for academic use, replication, and non-commercial research.

Commercial use — including incorporating this framework, methodology, or evaluation infrastructure into a product or service — requires a separate license. Contact aryan199841@gmail.com.
