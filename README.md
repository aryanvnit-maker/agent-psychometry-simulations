# Kalibr-v2: Agent Psychometry Simulations

Empirical research infrastructure for testing whether validated human team psychology instruments predict AI agent team performance — and where they break down.

---

## The Finding

91 controlled simulations. Two topology types. Four scenarios. The result:

| Topology | Mean Task Score (0–100) |
|---|---|
| **Chain** (sequential handoffs) | **70.2** |
| Flat (round-table, all-to-all) | 36.9 |
| Gap | −33.3 points |

| Team Size | Chain | Flat | Δ |
|---|---|---|---|
| 1 agent | 10.0 | 35.4 | +25.4 |
| 2 agents | 60.8 | 16.3 | −44.5 |
| 4 agents | 76.8 | 38.9 | −37.9 |
| 8 agents | 85.8 | 54.4 | −31.4 |

**A chain of 2 agents (60.8) outperforms a flat swarm of 8 (54.4).**
Adding a second agent to a flat swarm drops score from 35.4 → 16.3. Coordination overhead destroys more value than the second agent contributes.

Diversity hurts: diverse (drafted) teams score 57.8 on chain vs 82.2 for founder-brained alignment.

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

Human organizational psychology has spent 40 years building instruments to predict team performance: who to hire, how to compose teams, what conditions produce cohesion. Almost none of that work has been tested on AI agent teams.

This project runs those instruments on multi-agent LLM simulations and measures where the human findings replicate, where they invert, and where they produce novel patterns with no human analogue.

We used the **Kalibr psychometric framework** — a 10-dimension behavioral assessment — to assign distinct personality profiles to AI agents, composed them into teams under controlled conditions, and ran them through structured business scenarios. Three independent AI judges scored each transcript against validated rubrics. 91 simulations across two topology types produced the results documented here.

---

## Research Questions

1. Does cognitive diversity predict AI agent team performance the way it predicts human team performance (Bell, 2007)?
2. Does team-level conscientiousness predict performance (Barrick et al., 1998)?
3. Does psychological safety predict performance more than composition (Google Project Aristotle, 2015)?
4. Do GEQ task cohesion and social cohesion remain distinct constructs in AI teams (Carron et al., 1985)?
5. Does topology (how agents are connected) interact with composition to produce performance differences?

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

Scores ≥70 produce high-expression behaviours. Scores ≤30 produce low-expression behaviours. Middle scores produce balanced, contextual behaviours. The same threshold logic that produces a human behavioral report produces an agent's operating constraints.

**3 judge agents** score transcripts independently. Judges are tuned profiles: high Adaptive Intelligence, high Philosophy Cohesion, high Feedback Orientation, Volatility fixed at 50 (neutral). They receive no information about the team composition — they only see the transcript and rubric.

### Team Composition

Each run selects a team from the worker pool using one of three composition conditions:

**Drafted** — A captain (the worker with the highest score on the task-relevant dimensions) selects teammates by gap-filling: each pick maximises coverage of dimensions not already represented in the team. Produces the most cognitively diverse team possible for the given scenario.

**Homogeneous** — Team is assembled by selecting the workers whose dimensional profiles are most similar to each other. Minimal variance across all 10 dimensions. Everyone thinks alike.

**Founder-brained** — Team is assembled by selecting agents with high Drive Alignment, high Philosophy Cohesion, and high Volatility Vector. High-conviction, high-drive, low-agreeableness. Mirrors early-stage startup teams where the founder hires people who share their intensity.

Team sizes tested: **1, 2, 4, 8, 16 agents**.

### Scenarios

Four structured business scenarios, each mapped to a Tuckman phase and a set of task-relevant dimensions:

| Scenario | Phase | Task | Tests |
|---|---|---|---|
| Series A Product Fork | Forming | Recommend: double down, pivot, or hybrid on a $2M-runway startup | Initiative-taking, ambiguity resolution, convergence speed |
| Resource Allocation | Storming | Allocate $500K across three initiatives — one must receive ≥50% | Zero-sum negotiation, deadlock resistance |
| Post-Mortem Under Pressure | Storming | Identify 3 root causes of a failed product launch, assign accountability | Genuine critique vs blame diffusion, causal reasoning |
| Security Breach Crisis | Performing | 45 minutes before public disclosure: 3 actions, customer notification, irreversible decision | Speed of convergence, role coverage, quality under pressure |

Each scenario has an explicit rubric with point-weighted criteria. The judge evaluates the *team's final output* against those criteria, not the quality of individual agent turns.

### Scoring Instruments

Judges score each transcript on seven proxy measures drawn from validated human instruments:

| Proxy | Source Instrument | What It Measures |
|---|---|---|
| Task Score | Custom rubric | Overall output quality against stated criteria (0–100) |
| GEQ Task Cohesion | Group Environment Questionnaire (Carron et al., 1985) | Did agents converge on a shared output? |
| GEQ Social Cohesion | GEQ | Did agents build on each other's context? |
| TCI Innovation | Team Climate Inventory (Anderson & West, 1994) | Rate of novel vs obvious approaches |
| FIRO Inclusion | FIRO-B (Schutz, 1958) | Fraction of agents addressed at least once |
| Contradiction Count | — | Number of direct agent-to-agent contradictions |
| Consensus Achieved | — | Binary: did the team reach a resolution? |

A psychological safety composite is derived from consensus + low contradictions + high inclusion, normalised 0–100. This operationalises Google Project Aristotle's construct.

### Topologies

**Chain topology** — Agents are arranged in a linear sequence. Each agent receives the full conversation history but only one agent produces output per turn. Information flows forward only: A → B → C → D → END. Sequential, no backtracking.

**Flat (round-table) topology** — Every agent speaks once per round, for two rounds. Each agent receives the full conversation history from all prior speakers before generating their response. All-to-all information flow. No routing cost — this is the theoretical upper bound.

The gap between chain and flat performance = the cost of routing structure.

### Infrastructure

- **Orchestration**: LangGraph state graphs
- **Model**: Gemini 2.5 Flash, temperature=0.0 (fully deterministic — same inputs always produce same outputs)
- **Database**: Supabase (PostgreSQL) — every run persisted with resume capability
- **Evaluation**: 3-judge panel, independent scoring, inter-rater reliability via variance across judges
- **Token budget**: 800 output tokens per agent per turn; cull threshold at 2400 cumulative output tokens

---

## Results

### Dataset

- **91 total runs**: 51 chain topology + 40 flat topology
- **4 scenarios** × **5 team sizes** × **3 compositions** (team-of-1 runs drafted only; flat skips size-16)
- **Seed 42** — fully reproducible

### Chain Topology Results (51 runs)

| Composition | Mean Task Score | Std | Consensus Rate |
|---|---|---|---|
| Founder-brained | 82.2 | 23.5 | 81.2% |
| Homogeneous | 72.8 | 31.7 | 81.2% |
| Drafted (diverse) | 57.8 | 39.7 | 52.6% |

| Team Size | Mean Task Score |
|---|---|
| 1 | 10.0 |
| 2 | 60.8 |
| 4 | 76.8 |
| 8 | 85.8 |
| 16 | 78.6 |

### Flat Topology Results (40 runs)

| Composition | Mean Task Score | Std | Consensus Rate |
|---|---|---|---|
| Homogeneous | 42.4 | 38.1 | 46.2% |
| Founder-brained | 41.0 | 42.8 | 45.5% |
| Drafted (diverse) | 29.4 | 30.4 | 25.0% |

### Topology Comparison

| Composition | Chain | Flat | Δ |
|---|---|---|---|
| Drafted | 57.8 | 29.4 | −28.4 |
| Homogeneous | 72.8 | 42.4 | −30.4 |
| Founder-brained | 82.2 | 41.0 | −41.2 |

**Chain mean: 70.2 — Flat mean: 36.9 — Gap: −33.3 points**

---

## Findings

### Finding 1: The Bell (2007) Inversion — Confirmed Structural

Bell's 2007 meta-analysis found that cognitive diversity reliably predicts team performance in human teams. In our simulations, the opposite holds: **diverse (drafted) teams consistently finish last across every condition tested**.

This was initially flagged as a possible chain topology artifact. Running flat topology — where every agent has access to all information simultaneously — was designed to eliminate that hypothesis. The inversion survived. Homogeneous and founder-brained compositions outperform diverse compositions regardless of whether agents can see each other's full output.

**Why this likely happens:** Agent constitutions are behavioral constraints, not adaptive strategies. A diverse team means agents with incompatible constraints: one agent is constitutionally compelled to challenge, another to seek consensus, another to defer. In a human team, diverse members *adapt*. Agent constitutions don't adapt — they collide. The collision degrades output.

**Implication:** The human intuition that "diverse teams are better" does not transfer to AI agent composition. For bounded, structured tasks, compositional alignment outperforms compositional diversity.

### Finding 2: Sequential Structure Outperforms Perfect Information

This is the most counterintuitive result. Flat topology gives every agent complete information — no routing cost, no information loss. By any naive information-theoretic argument, flat should outperform chain. It does the opposite, by 33 points.

Chain topology forces sequential commitment. Each agent receives prior output and must build on it — they cannot re-open settled questions because the prior agent has already moved forward. This produces convergence. Flat topology enables every agent to respond to everything simultaneously, which produces deliberation without commitment. Agents engage socially but fail to converge on output.

**The GEQ data shows this directly:** In chain topology, task cohesion and social cohesion track together (gap: 8.9 points). In flat topology, they diverge sharply (gap: 37 points). Social cohesion stays high in flat — everyone is talking, everyone is included (FIRO inclusion = 1.00). But task cohesion collapses. Agents are socially present and taskfully absent.

**Implication:** More communication is not better. Forcing sequential commitment produces better outputs than enabling open deliberation, at least on bounded decision tasks. This has direct design implications for multi-agent system architecture.

### Finding 3: Founder-Brained Advantage Is Topology-Specific

Founder-brained composition achieves 82.2 on chain and 41.0 on flat — the largest topology-dependent drop of any composition (−41.2 points). High-drive, high-conviction agents excel when building sequentially on each other's work. In open deliberation, they conflict: each agent's strong directional pull creates incompatible vectors, and the team deadlocks or produces incoherent output.

**Implication:** High-drive agent compositions should only be deployed in topologies that enforce sequential handoffs. In any topology that allows simultaneous contribution, founder-brained compositions degrade to approximately the same level as homogeneous.

### Finding 4: Psychological Safety Is the Only Cross-Topology Predictor

Across both chain (r=0.66\*\*\*) and flat (r=0.77\*\*\*) topologies, the psychological safety composite — operationalised as consensus achievement + low contradictions + high inclusion — is the strongest predictor of task performance. This replicates Google Project Aristotle's central finding.

Diversity, by contrast, shows r=0.48\*\*\* in chain but collapses to r=0.17 (n.s.) in flat. The diversity signal is topology-dependent. The psychological safety signal is not.

**Implication:** If optimising for a single lever, optimise for psychological safety in the agent team — constitutions that seek consensus, avoid contradiction, and include all agents in the conversation — rather than for compositional diversity.

### Finding 5: Barrick's Variance Finding Partially Replicates

Barrick et al. (1998) found that variance in team conscientiousness predicts performance better than mean conscientiousness. In chain topology, this holds clearly: conscientiousness variance r=0.53\*\*\* vs mean r=0.19 (n.s.). In flat topology, both drop to non-significance.

The directional pattern (variance > mean) holds in both topologies, but statistical significance is lost in flat — likely a combination of smaller sample and high score variance from the topology-induced performance degradation. The finding is directionally consistent across both conditions.

---

## Design Rules for Multi-Agent Systems

These are empirically derived from 91 simulation runs across two topology types and four scenario categories. They apply to bounded, structured decision tasks. They may not generalise to open-ended or creative tasks without further testing.

---

### Rule 1: Use Chain Topology as Your Default

**What the data says:** Chain topology outperforms flat (round-table) by 33 points on average across all compositions and scenarios. The gap is not marginal — it is the largest single effect in the dataset.

**What this means in practice:** When building a multi-agent pipeline, default to sequential handoffs rather than parallel deliberation. Each agent should receive the prior output and be asked to build on it, not respond to a shared prompt simultaneously with other agents.

**Where this likely breaks:** Tasks that require genuine exploration of the solution space before committing — brainstorming, requirements gathering, open-ended research — may benefit from a deliberation phase before the chain takes over. The data here only covers structured decision tasks with clear right/wrong rubrics.

**Anti-pattern to avoid:** Round-table discussion nodes where N agents all respond to the same prompt. This consistently produces social engagement without task convergence.

---

### Rule 2: Match Composition to Topology, Not Just to Task

**What the data says:** Founder-brained composition achieves 82.2 on chain and 41.0 on flat. The composition ranking changes between topologies: founder-brained wins on chain, homogeneous wins on flat.

**What this means in practice:** The question is not just "which composition is best for this task?" — it is "which composition is best for this task *in this topology*?" They interact.

- **Chain + founder-brained**: Highest performing combination in the dataset (mean 82.2). Use when you have a bounded task, a clear deliverable, and a sequential pipeline.
- **Chain + homogeneous**: Strong and stable (72.8). Lower variance than founder-brained. Prefer when reliability matters more than peak performance.
- **Flat + homogeneous**: Best available option if you must use flat topology (42.4). Avoids the conflict that destroys founder-brained in open deliberation.
- **Any topology + drafted (diverse)**: Lowest performing composition in both topologies. Do not default to diverse composition because it seems intuitively correct.

---

### Rule 3: Do Not Build Diverse Agent Teams for Structured Tasks

**What the data says:** Diverse (drafted) teams finish last in every condition. The gap between diverse and non-diverse is 15–25 points in chain, 12–13 points in flat. This finding survived a direct topology robustness check.

**What this means in practice:** For task-completion agents — support, analysis, decision support, code review — resist the intuition that diverse agent personalities produce better output. They do not, on the evidence available.

**The mechanism:** Agent constitutions are fixed behavioral constraints, not adaptive strategies. A diverse team produces constraint collision — agents whose operating rules are structurally incompatible with each other. Unlike humans, agents cannot recognise the collision and adapt. The incompatibility degrades output directly.

**What to do instead:** Use compositional alignment — agents whose behavioral profiles are compatible for the task type. For execution tasks, aligned high-drive profiles. For evaluation tasks, aligned analytical profiles.

**Caveat:** This applies to structured, bounded tasks. The diversity penalty may not hold for open-ended ideation tasks, where constraint collision might produce genuinely novel directions. That has not been tested here.

---

### Rule 4: Optimise Agent Constitutions for Psychological Safety, Not Capability

**What the data says:** Psychological safety (consensus + low contradictions + high inclusion) predicts task score at r=0.66\*\*\* on chain and r=0.77\*\*\* on flat — the strongest and most consistent predictor in the dataset. Compositional diversity predicts at r=0.48\*\*\* on chain and r=0.17 (n.s.) on flat.

**What this means in practice:** When writing agent system prompts, the most important design choice is not "what capabilities does this agent have" — it is "what behaviours does this agent exhibit toward other agents in the conversation?"

Specifically, build constitutions that:
- **Acknowledge prior agent output** before contributing new content
- **Avoid direct contradiction** of prior agents unless explicitly tasked as a critic
- **Reference other agents by role or output** — inclusion behaviours
- **Converge toward resolution** rather than reopening settled questions

These behaviours are operationally simple to encode in a system prompt and produce the largest performance gains in the data.

**Anti-pattern:** Building specialist agents with sharp capability boundaries and instructing them to hold their ground. This produces high contradiction counts and low consensus rates — the signature of low psychological safety — which is the strongest predictor of poor performance.

---

### Rule 5: Social Cohesion and Task Cohesion Are Not Interchangeable

**What the data says:** In flat topology, GEQ task cohesion averages 29–52 while social cohesion averages 65–81 — a 37-point gap. In chain topology, both dimensions track within 9 points of each other.

**What this means in practice:** An agent team where everyone is talking to everyone is not the same as an agent team that is converging on an output. These are independent constructs. You can have full social cohesion (every agent addresses every other agent, FIRO inclusion = 1.00) and near-zero task cohesion (no shared output produced).

**The diagnostic:** If you are seeing high token usage and turn count but poor output quality, and every agent appears to be "participating," you likely have a social cohesion / task cohesion split. The fix is not to increase deliberation — it is to add a convergence mechanism. In practice: add a final agent whose explicit role is to synthesize the prior discussion into a committed output, and put them at the end of a chain.

---

### Rule 6: Team Size Has Diminishing Returns After Size 4

**What the data says (chain topology):** Size 1: 10.0, Size 2: 60.8, Size 4: 76.8, Size 8: 85.8, Size 16: 78.6. The largest gain is from 1→2 agents (+50.8 points). The 4→8 gain is +9 points. 8→16 is negative (−7.2).

**What this means in practice:** The marginal return on adding agents beyond 4 is small and potentially negative. Size 8 is approximately the performance ceiling in chain topology on the task types tested here.

**Cost implication:** Each agent added to a flat topology simulation multiplies the context window cost roughly linearly (every agent sees everyone's output). In chain, cost grows linearly with turns. Neither topology benefits enough from going beyond 8 agents to justify the token cost.

**Recommendation:** Default team size for structured tasks is 4 agents. Experiment with 8 only if 4 fails to produce acceptable output quality.

---

## How to Run

### Setup

```bash
git clone https://github.com/aryanvnit-maker/agent-psychometry-simulations
cd agent-psychometry-simulations
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env     # Add your GEMINI_API_KEY and DATABASE_URL
```

Run the schema in your Supabase SQL editor (`src/telemetry/schema.sql`) before first run.

### Run Simulations

```bash
# Chain topology (52 combinations)
python run_all.py

# Flat topology (40 combinations — skips size-16)
python run_all.py --topology flat

# Both topologies in one batch
python run_all.py --topology all
```

Safe to interrupt and restart — completed runs are persisted to Supabase and skipped automatically.

### Analyse Results

```bash
python analyze.py
```

Prints chain summary, flat summary, and topology comparison. Saves 8 charts to `/reports/`.

### Utilities

```bash
# Delete all flat-topology runs (before re-running with a fix)
python purge_flat_runs.py
```

---

## Theoretical Grounding

| Human Finding | Source | AI Replication Status |
|---|---|---|
| Cognitive diversity predicts team performance | Bell (2007) | **Inverted** — diversity penalises performance in both topologies |
| Conscientiousness variance predicts better than mean | Barrick et al. (1998) | **Directionally consistent** — significant in chain, n.s. in flat |
| Psychological safety is the strongest team predictor | Google Project Aristotle (2015) | **Replicated** — strongest predictor in both topologies |
| Task cohesion and social cohesion are distinct | GEQ (Carron et al., 1985) | **Replicated** — diverge 37 points in flat, track in chain |
| Innovation climate predicts novel output | TCI (Anderson & West, 1994) | **Replicated** — r=0.81\*\*\* (chain), r=0.89\*\*\* (flat) |

---

## Limitations

- **91 runs is thin.** Significance thresholds are met on the key findings, but effect size confidence intervals are wide. Publication would require 200+ runs per topology.
- **Model uniformity.** All agents run on the same underlying model (Gemini 2.5 Flash). The constitutions shift behavioural probability distributions but do not introduce the genuine capability differences that exist between human team members. Cross-model testing is the logical next step.
- **Task scope.** All four scenarios are bounded decision tasks with clear rubric criteria. Findings may not transfer to open-ended, creative, or long-horizon tasks.
- **Temperature=0.0.** Full determinism makes runs reproducible but eliminates sampling variance. Human teams exhibit behavioural variance across identical scenarios; these agent teams do not.
- **Simulated conflict only.** The storming scenarios produce measurable contradiction counts but agents do not experience the social cost of conflict that humans do. The mechanisms underlying human team dysfunction may not map to constraint collision.

---

## Project Structure

```
agent-psychometry-simulations/
├── src/
│   ├── agents/
│   │   ├── profile.py          # KalibrDimensions, GameTheoryParams, AgentProfile
│   │   ├── constitution.py     # Dimension scores → behavioral system prompt
│   │   └── pool.py             # Initialise 32 workers + 3 judges, captain draft
│   ├── orchestration/
│   │   └── engine.py           # LangGraph graphs: chain, flat; SimState; cull logic
│   ├── evaluation/
│   │   ├── judge.py            # 3-judge panel scoring, JSON extraction
│   │   └── schema.py           # EvaluatorOutput Pydantic model
│   ├── scenarios/
│   │   └── library.py          # 4 scenarios with briefs, rubrics, task dimensions
│   ├── analysis/
│   │   ├── query.py            # load_results(topology) — joins runs + evaluations
│   │   └── plots.py            # 8 charts
│   └── telemetry/
│       ├── database.py         # Supabase connection, insert_run, already_completed
│       └── schema.sql          # runs + evaluations table definitions
├── run_all.py                  # Batch runner — all combinations, retry logic
├── run_simulation.py           # Single run CLI
├── analyze.py                  # Chain + flat analysis + topology comparison
├── purge_flat_runs.py          # Delete flat runs before re-running with a fix
├── simulation-methodology.md  # Full research design document
└── psychometric-research-foundations.md  # Source instrument documentation
```
