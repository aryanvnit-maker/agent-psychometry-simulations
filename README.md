# Kalibr-v2: Agent Psychometry Simulations

Empirical research infrastructure for testing whether validated human team psychology instruments predict AI agent team performance — and where they break down.

---

## The Finding

118 controlled simulations. Two topology types. Two model families. Four scenarios. The result:

| Model Family | Chain (sequential) | Flat (round-table) | Gap |
|---|---|---|---|
| **Gemini 2.5 Flash** | **40.3** | 23.4 | −16.9 |
| **Anthropic Claude 3.5 Sonnet** | **42.4** | 20.4 | −21.9 |
| **Combined** | **40.7** | 22.7 | **−18.0** |

Chain outperforms flat across both model families. The topology finding is architectural, not model-specific.

| Team Size | Chain | Flat | Δ |
|---|---|---|---|
| 1 agent | 15.3 | 31.2 | +15.9 |
| 2 agents | 57.6 | 10.7 | −46.9 |
| 4 agents | 50.4 | 35.5 | −14.9 |
| 8 agents | 40.4 | 19.1 | −21.3 |
| 16 agents | 16.5 | — | — |

**Sweet spot: 2–4 agents in chain topology.** A chain of 2 agents (57.6) outperforms a flat swarm of 8 (19.1). Adding agents to flat topology past size 1 actively degrades performance — coordination overhead exceeds the value of the second agent.

**Reproduce it in one command** (requires `GEMINI_API_KEY` in `.env`):
```bash
python reproduce.py
```

Read the agent system prompts that produced these results:
```bash
python export_constitutions.py
```

---

## What This Is

Human organisational psychology has spent 40 years building instruments to predict team performance: who to hire, how to compose teams, what conditions produce cohesion. Almost none of that work has been tested on AI agent teams.

This project runs those instruments on multi-agent LLM simulations and measures where the human findings replicate, where they invert, and where they produce novel patterns with no human analogue.

We used the **Kalibr psychometric framework** — a 10-dimension behavioral assessment — to assign distinct personality profiles to AI agents, composed them into teams under controlled conditions, and ran them through structured business scenarios. Three independent AI judge agents scored each team's final deliverable against explicit binary rubrics on a 0–100 scale. 118 simulations across two topology types and two model families produced the results documented here.

---

## Research Questions

1. Does cognitive diversity predict AI agent team performance the way it predicts human team performance (Bell, 2007)?
2. Does team-level conscientiousness predict performance (Barrick et al., 1998)?
3. Does psychological safety predict performance more than composition (Google Project Aristotle, 2015)?
4. Do GEQ task cohesion and social cohesion remain distinct constructs in AI teams (Carron et al., 1985)?
5. Does topology (how agents are connected) interact with composition to produce performance differences?
6. Is the topology finding model-specific or architectural?

---

## Methodology

### Agent Architecture

**32 worker agents** were instantiated from the Kalibr psychometric framework. Each agent receives a system prompt (called a *constitution*) generated from their dimensional profile. The constitution specifies behavioral constraints — what the agent will and will not do, how it communicates, how it handles conflict — derived directly from their scores.

**10 Kalibr dimensions** (all scored 0–100):

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

Scores ≥70 produce high-expression behaviours. Scores ≤30 produce low-expression behaviours. Middle scores produce balanced, contextual behaviours.

**3 judge agents** score each run independently. Judges are tuned profiles: high Adaptive Intelligence, high Philosophy Cohesion, high Feedback Orientation, Volatility fixed at 50 (neutral). Critically: judges evaluate **only the team's final extracted deliverable** against binary rubric criteria — not the full transcript. For chain topology, the final deliverable is the last agent's synthesized output. For flat topology, it is the complete final round of responses. This eliminates formatting bias from sequential vs parallel transcript structure.

### Team Composition

Each run selects a team from the worker pool using one of three composition conditions:

**Drafted** — A captain (highest scorer on task-relevant dimensions) selects teammates by gap-filling: each pick maximises dimensional coverage not already represented. Most cognitively diverse team possible.

**Homogeneous** — Workers selected for minimum dimensional variance. Everyone thinks alike.

**Founder-brained** — High Drive Alignment, high Philosophy Cohesion, high Volatility Vector. High-conviction, high-drive, low-agreeableness. Mirrors early-stage startup teams.

Team sizes tested: **1, 2, 4, 8, 16 agents** (flat skips size-16; cross-model run skips size-1 and size-16).

### Scenarios

Four structured business scenarios, each mapped to a Tuckman phase:

| Scenario | Phase | Task |
|---|---|---|
| Series A Product Fork | Forming | Recommend: double down, pivot, or hybrid on a $2M-runway startup |
| Resource Allocation | Storming | Allocate $500K across three initiatives — one must receive ≥50% |
| Post-Mortem Under Pressure | Storming | Identify 3 root causes of a failed launch, assign accountability |
| Security Breach Crisis | Performing | 45 minutes before public disclosure: 3 actions, notification, irreversible decision |

Each scenario has an explicit rubric with binary point checkpoints. The judge evaluates only the team's final output against those criteria.

### Topologies

**Chain topology** — Linear sequential handoff: A → B → C → END. Each agent receives full history but produces output only once, in order. No agent can reopen what a prior agent settled.

**Flat (round-table) topology** — Every agent speaks once per round for two rounds, with full conversation history from all prior speakers. Perfect information. No routing cost.

### Infrastructure

- **Orchestration**: LangGraph state graphs
- **Worker models**: Gemini 2.5 Flash (primary) and Anthropic Claude 3.5 Sonnet (cross-model replication)
- **Judge model**: Gemini 2.5 Flash throughout — consistent across all runs
- **Temperature**: 0.0 (fully deterministic — same inputs always produce same outputs)
- **Database**: Supabase (PostgreSQL) — every run persisted with resume capability and transcript storage
- **Token budget**: 800 output tokens per agent per turn; cull threshold at 2,400 cumulative output tokens

---

## Results

### Dataset

- **118 total runs**: 94 Gemini (55 chain + 39 flat) + 24 Anthropic (12 chain + 12 flat, drafted composition only)
- **4 scenarios** × **5 team sizes** × **3 compositions** (Gemini); **4 scenarios** × **3 team sizes** × **1 composition** (Anthropic)
- **Seed 42** — fully reproducible

### Topology Finding (Cross-Model)

| Model | Chain | Flat | Gap | Verdict |
|---|---|---|---|---|
| Gemini 2.5 Flash | 40.3 | 23.4 | +16.9 | chain > flat |
| Claude 3.5 Sonnet | 42.4 | 20.4 | +21.9 | chain > flat |

Chain outperforms flat in both model families. The finding is architectural.

### Gemini: Chain Results by Composition

| Composition | Mean Task Score | Consensus Rate |
|---|---|---|
| Homogeneous | 48.6 | 64.7% |
| Drafted (diverse) | 37.7 | 40.9% |
| Founder-brained | 35.1 | 62.5% |

### Gemini: Flat Results by Composition

| Composition | Mean Task Score | Consensus Rate |
|---|---|---|
| Founder-brained | 26.4 | 36.4% |
| Drafted (diverse) | 26.1 | 25.0% |
| Homogeneous | 17.1 | 33.3% |

Composition ranking is topology-dependent: homogeneous wins on chain, founder-brained wins on flat.

### Topology × Composition (Gemini)

| Composition | Chain | Flat | Δ |
|---|---|---|---|
| Homogeneous | 48.6 | 17.1 | −31.5 |
| Drafted | 37.7 | 26.1 | −11.5 |
| Founder-brained | 35.1 | 26.4 | −8.7 |

---

## Findings

### Finding 1: Sequential Structure Outperforms Parallel Deliberation

Chain topology outperforms flat by 17–22 points across both model families and all compositions. This is the most robust finding in the dataset.

**The mechanism (GEQ data):** In chain topology, task cohesion and social cohesion track within 23.9 points. In flat topology, the gap is 39.6 points — social cohesion stays high (agents are engaged, FIRO inclusion hits 1.0) while task cohesion collapses. Agents are socially present and taskfully absent. The meeting is productive; the meeting does not produce a decision.

Chain forces sequential commitment. Each agent builds on committed prior output and cannot reopen settled questions. Flat enables deliberation without commitment.

### Finding 2: The Bell (2007) Result Is Topology-Dependent

Bell (2007) found cognitive diversity reliably predicts team performance in humans. In chain topology, the opposite holds — homogeneous teams (48.6) outperform diverse drafted teams (37.7). In flat topology, the ranking flips again: founder-brained edges out diverse teams, with homogeneous scoring lowest (17.1).

**The inversion is not structural — it is topology-dependent.** The composition that wins changes with the communication structure. The mechanism on chain: agent constitutions are fixed behavioral constraints that don't adapt. A diverse team produces constraint collision; agents whose operating rules are incompatible degrade the output. Sequential structure amplifies this because each agent's constraint shapes what the next one receives.

### Finding 3: Psychological Safety Is the Strongest Cross-Topology Predictor

| Predictor | Chain r | Flat r |
|---|---|---|
| GEQ Task Cohesion | 0.73*** | 0.79*** |
| Psychological Safety | 0.70*** | 0.65*** |
| GEQ Social Cohesion | 0.28* | 0.34* |
| Diversity | −0.06 (n.s.) | +0.04 (n.s.) |
| Conscientiousness | ~0.01 (n.s.) | ~0.11 (n.s.) |

Psychological safety (consensus + low contradictions + high inclusion) is the only predictor significant at p<0.001 in both topologies. Diversity does not predict performance in either. Conscientiousness proxies show no significant effect.

### Finding 4: Flat Topology Produces Social Engagement Without Task Convergence

GEQ task/social cohesion gap: **chain = 23.9 points, flat = 39.6 points**. In flat topology, FIRO inclusion hits 1.0 — every agent addresses every other agent. Consensus rate: chain 52.2%, flat 31.4%. Flat teams talk; chain teams decide.

### Finding 5: TCI Innovation Climate Replicates

TCI innovation scores predict novel approach counts at r=0.74*** (chain) and r=0.87*** (flat). The innovation climate instrument successfully identifies which teams generate non-obvious approaches — the cleanest replication in the dataset.

---

## Design Rules for Multi-Agent Systems

Empirically derived from 118 simulations. Apply to bounded, structured decision tasks.

**Rule 1: Default to chain topology.** Chain outperforms flat by 18 points on average. When building a multi-agent pipeline, use sequential handoffs. Each agent should receive prior committed output and build on it.

**Rule 2: Keep teams small.** Size 2 chain (57.6) outperforms size 8 flat (19.1). The largest gain is 1→2 agents. Returns diminish past size 4. Diminish past size 8. Size 16 underperforms size 8.

**Rule 3: Add a synthesis node after any deliberation phase.** If exploration is needed before commitment, run a constrained deliberation round, then route all output to a single synthesis agent. Do not let deliberation continue without a convergence mechanism.

**Rule 4: Optimise agent constitutions for psychological safety behaviours.** Agents that acknowledge prior output, avoid contradiction, and converge toward resolution produce better outcomes than agents optimised for narrow capability or strong directional pull.

**Rule 5: Match composition to topology.** Homogeneous compositions are most stable on chain (high score, lower variance). Founder-brained compositions lead on flat but with high variance. Diverse compositions underperform on chain; use only when exploration is the explicit goal.

---

## How to Run

### Setup

```bash
git clone https://github.com/aryanvnit-maker/agent-psychometry-simulations
cd agent-psychometry-simulations
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env     # Add GEMINI_API_KEY, DATABASE_URL, and optionally ANTHROPIC_API_KEY
```

Run the schema in your Supabase SQL editor (`src/telemetry/schema.sql`) before first run. Also run:
```sql
ALTER TABLE runs ADD COLUMN IF NOT EXISTS model_family TEXT NOT NULL DEFAULT 'gemini';
ALTER TABLE runs ADD COLUMN IF NOT EXISTS transcript TEXT;
```

### Run Simulations

```bash
# Both topologies (92 combinations)
python run_all.py --topology all

# Cross-model replication (24 combinations, requires ANTHROPIC_API_KEY)
python run_cross_model.py --provider anthropic
```

Safe to interrupt and restart — completed runs are persisted to Supabase and skipped automatically.

### Analyse Results

```bash
python analyze.py
```

Prints chain summary, flat summary, topology comparison, and cross-model comparison. Saves 8 charts to `/reports/`.

### Utilities

```bash
# Archive and purge runs before re-running (backs up to runs_backup first)
python purge_all_runs.py

# Re-score stored transcripts with updated judge (no re-running needed)
python rescore.py
```

---

## Theoretical Grounding

| Human Finding | Source | AI Replication Status |
|---|---|---|
| Cognitive diversity predicts team performance | Bell (2007) | **Topology-dependent** — homogeneous wins on chain, founder-brained wins on flat; diversity penalised in both |
| Conscientiousness variance predicts better than mean | Barrick et al. (1998) | **Not replicated** — neither measure significant in either topology |
| Psychological safety is the strongest team predictor | Google Project Aristotle (2015) | **Replicated** — strongest predictor in both topologies (r=0.70***, 0.65***) |
| Task cohesion and social cohesion are distinct | GEQ (Carron et al., 1985) | **Replicated** — diverge 39.6 points in flat, 23.9 in chain |
| Innovation climate predicts novel output | TCI (Anderson & West, 1994) | **Replicated** — r=0.74*** (chain), r=0.87*** (flat) |

---

## Limitations

- **118 runs.** Key findings reach significance, but effect size confidence intervals are wide. Pre-registered replication with 300+ runs per topology per model would substantially increase confidence.
- **Model uniformity within teams.** All agents in a given run share the same underlying model. Constitutions shift behavioral probability distributions but not cognitive architectures. A diverse human team has genuinely different cognitive processing; a diverse agent team has different prompts on identical processing.
- **Task scope.** All four scenarios are bounded decision tasks with rubric-scorable outputs. Findings may not transfer to open-ended research, creative generation, or long-horizon planning.
- **Determinism.** Temperature=0.0 eliminates sampling variance. Human team performance varies across replications; these simulations do not.
- **Cross-model scope.** The Anthropic replication tested drafted composition only at sizes 2, 4, 8. Composition and size-16 findings are Gemini-only.
- **Judge model uniformity.** All judges run on Gemini 2.5 Flash. Final-answer-only evaluation reduces but does not eliminate potential model-preference effects.

---

## Project Structure

```
agent-psychometry-simulations/
├── src/
│   ├── agents/
│   │   ├── profile.py          # KalibrDimensions, AgentProfile
│   │   ├── constitution.py     # Dimension scores → behavioral system prompt
│   │   └── pool.py             # 32 workers + 3 judges, captain draft logic
│   ├── orchestration/
│   │   └── engine.py           # LangGraph graphs: chain, flat; SimState; cull logic
│   ├── evaluation/
│   │   ├── judge.py            # Final-answer-only judge, 3-judge panel, JSON extraction
│   │   └── schema.py           # EvaluatorOutput Pydantic model
│   ├── scenarios/
│   │   └── library.py          # 4 scenarios with briefs, rubrics, task dimensions
│   ├── analysis/
│   │   ├── query.py            # load_results(topology, model_family)
│   │   └── plots.py            # 8 charts
│   └── telemetry/
│       ├── database.py         # Supabase connection, insert_run, rescore helpers
│       └── schema.sql          # runs + evaluations table definitions
├── run_all.py                  # Batch runner — all combinations, retry logic
├── run_cross_model.py          # Cross-model topology replication (24 combinations)
├── run_simulation.py           # Single run CLI
├── analyze.py                  # Chain + flat + cross-model analysis
├── rescore.py                  # Re-score stored transcripts with updated judge
├── purge_all_runs.py           # Archive + delete runs (backup-safe)
├── reproduce.py                # Single-command demo, no DB required
└── export_constitutions.py     # Generate static constitution files
```
