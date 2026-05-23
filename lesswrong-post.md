# AI Agent Swarms Reproduce the Failure Modes of Flat Human Organisations

Most multi-agent AI systems are built with flat topology — all agents see everything, all agents respond, everyone deliberates together. This feels correct. More perspectives, more information sharing, better output.

We ran 118 controlled simulations across two model families to test it. Flat topology consistently underperformed sequential chains by 17–22 points on task scores (0–100, rubric-graded against final deliverables only). The mechanism is visible in the data and connects directly to 40 years of human organisational research.

The less expected finding: multi-agent chains peak at N=2. Adding agents to a flat topology drops performance by 46 points while multiplying compute costs. We found an inverse scaling law for coordination — more agents, worse output.

---

## Background: The Default Is Unexamined

The major multi-agent frameworks — CrewAI, AutoGen, many LangGraph implementations — default to patterns where agents share a full context window and contribute simultaneously or in loosely ordered rounds. Call this flat topology: every agent has perfect information, every agent speaks, no agent is structurally forced to commit to what came before.

This default was chosen because it is easy to implement and intuitively appealing. It was not chosen because anyone measured the output quality against the alternative.

We measured it.

---

## What We Did

We built a simulation infrastructure using the Kalibr psychometric framework — a 10-dimension behavioral assessment tool — to assign distinct personality profiles to 32 AI agents. Each agent's system prompt (its *constitution*) is generated from its dimensional scores across dimensions including drive alignment, adaptive intelligence, volatility, ambiguity tolerance, and feedback orientation. Scores ≥70 produce high-expression behaviours; scores ≤30 produce low-expression behaviours. The same threshold logic that generates a human behavioral report generates an agent's operating constraints.

We composed these agents into teams of 1, 2, 4, 8, and 16 under three composition conditions:

- **Drafted** — captain selects teammates to maximise dimensional diversity (gap-filling)
- **Homogeneous** — teammates selected for minimum dimensional variance
- **Founder-brained** — high Drive Alignment, high Philosophy Cohesion, high Volatility; mirrors early-stage startup team culture

We ran each team through four structured business scenarios: strategic product decisions, zero-sum resource allocation, post-mortem analysis, and crisis response.

**Evaluation methodology:** Three independent judge agents scored each run. Critically, judges evaluated only the team's **final extracted deliverable** against hard binary rubric criteria — not the full transcript. For chain topology, the final deliverable is the last agent's synthesized output. For flat topology, it is the complete final round of responses. This eliminates the formatting bias inherent in evaluating full transcripts: a judge reading a chain transcript sees clean sequential reasoning; reading a flat transcript sees overlapping voices. Evaluating the deliverable alone removes that structural advantage. Judges always run on Gemini 2.5 Flash regardless of worker model, for consistent cross-model evaluation.

Two topologies:

**Chain** — linear sequential handoff: A → B → C → END. Each agent receives full conversation history but produces output only once, in order. No agent can reopen what a prior agent settled.

**Flat** — round-table: every agent speaks once per round for two rounds, receiving the full conversation history from all prior speakers. Perfect information. No routing cost.

94 Gemini runs + 24 Anthropic Claude 3.5 Sonnet runs = 118 total.

---

## Results

### The Single-Agent Baseline

Before comparing topologies, establish the floor.

| Condition | Task Score (0–100) |
|---|---|
| Single agent, chain | 15.3 |
| Single agent, flat | 31.2 |

The flat single-agent advantage: the agent receives two structured rounds of prompting rather than one, which improves output. This is the ceiling for single-agent performance.

Now add a second agent in flat topology: **10.7.**

Adding a second agent to a flat swarm dropped performance from 31.2 to 10.7 — a 21-point decrease. Coordination overhead destroyed more value than the second agent contributed. This is active degradation, not inefficiency.

### Topology (Gemini, All Compositions)

| Topology | Mean Task Score |
|---|---|
| Chain | 40.3 |
| Flat | 23.4 |
| **Gap** | **−16.9** |

| Team Size | Chain | Flat | Δ |
|---|---|---|---|
| 1 | 15.3 | 31.2 | +15.9 |
| 2 | 57.6 | 10.7 | −46.9 |
| 4 | 50.4 | 35.5 | −14.9 |
| 8 | 40.4 | 19.1 | −21.3 |
| 16 | 16.5 | — | — |

A chain of 2 agents (57.6) outperforms a flat swarm of 8 (19.1). The coordination overhead of flat topology is not overcome by adding more agents — it compounds.

This gap is not composition-specific:

| Composition | Chain | Flat | Δ |
|---|---|---|---|
| Homogeneous | 48.6 | 17.1 | −31.5 |
| Drafted (diverse) | 37.7 | 26.1 | −11.5 |
| Founder-brained | 35.1 | 26.4 | −8.7 |

The flat topology penalty is consistent across all compositions.

### Cross-Model Replication

We ran 24 additional combinations using Anthropic Claude 3.5 Sonnet as the worker model (judges remained on Gemini throughout). Drafted composition only, team sizes 2, 4, 8.

| Model | Chain | Flat | Gap | Verdict |
|---|---|---|---|---|
| Gemini 2.5 Flash | 40.3 | 23.4 | +16.9 | chain > flat |
| Claude 3.5 Sonnet | 42.4 | 20.4 | +21.9 | chain > flat |

The chain advantage holds across both model families. The finding is architectural, not a property of a specific model's output style.

Chain scores are nearly identical across models (40.3 vs 42.4). Different model family, same performance level — the task structure and agent constitutions are doing the work, not model capability differences.

---

## The Diversity Finding

Most enterprise teams building agent swarms compose them the way HR taught them to: a Coder, a Critic, a Planner, a Reviewer. Diverse roles, diverse perspectives, better outcomes. This is the Bell (2007) intuition applied to AI.

The data does not support it — but the pattern is more nuanced than a simple inversion.

**On chain topology:** diverse (drafted) teams score 37.7. Homogeneous teams score 48.6. Diverse teams finish last.

**On flat topology:** homogeneous teams drop to 17.1 — worst of any composition. Founder-brained (26.4) and drafted (26.1) score comparably.

The composition that wins changes with the communication structure. The mechanism on chain: agent constitutions are fixed behavioral constraints, not adaptive strategies. A diverse team means agents with incompatible behavioral profiles — one agent is constitutionally compelled to challenge, another to seek consensus, another to defer. Human team members with diverse personalities adapt to each other over time. Agent constitutions don't adapt. The incompatibility produces constraint collision, which degrades the deliverable.

On flat topology, the dynamic is different: diverse agents fragment across simultaneous contributions without a synthesis structure to resolve them, while homogeneous agents echo each other without building a coherent output. Founder-brained agents — high-conviction, aligned — hold their position clearly enough that their final-round outputs are individually complete, scoring comparably to drafted teams.

**The Bell inversion is topology-dependent, not structural.** Diversity hurts on chain. Homogeneity hurts on flat. Composition cannot be evaluated without knowing the topology.

The exact system prompts for each composition condition are in the repository.

---

## The Mechanism: Social Cohesion ≠ Task Cohesion

This is where the data becomes more interesting than just "chain wins."

We scored transcripts on two GEQ (Group Environment Questionnaire) dimensions: task cohesion (did agents converge on a shared output?) and social cohesion (did agents engage with each other's contributions?). These are validated distinct constructs from human team research (Carron et al., 1985).

**Chain topology:** task cohesion and social cohesion track within **23.9 points** of each other.

**Flat topology:** average gap is **39.6 points**. Social cohesion stays high (65–80) while task cohesion collapses (31–37).

In flat topology, agents are socially present and taskfully absent. FIRO inclusion scores — measuring what fraction of agents were addressed by other agents — hit near 1.0 in flat topology. Every agent talks to every other agent. Nobody produces a committed output.

Consensus rate: chain 52.2%, flat 31.4%.

This is not a subtle effect. It is the entire mechanism. Flat topology produces complete social engagement and degraded task convergence. The agents are having the meeting. The meeting is not producing a decision.

---

## What Does Replicate

Two findings from human research hold clearly across both topologies:

**Google Project Aristotle (psychological safety):** The psychological safety composite — operationalised as consensus achievement + low contradictions + high inclusion — predicts task score at r=0.70\*\*\* in chain and r=0.65\*\*\* in flat. It is the strongest consistent predictor in the dataset. Diversity shows r=−0.06 (n.s.) in chain and r=0.04 (n.s.) in flat.

**TCI Innovation Climate:** TCI innovation scores correlate with novel approach counts at r=0.74\*\*\* in chain and r=0.87\*\*\* in flat. The innovation climate instrument successfully predicts which teams generate non-obvious approaches. Cleanest replication in the dataset.

**Barrick et al. (1998) — not replicated:** The finding that conscientiousness variance predicts performance better than mean did not hold in either topology under the revised judge methodology. Neither measure reached significance.

---

## The Human Org Parallel

This is not a new pattern. It has a 20-year history in human organisations.

The flat organisation movement peaked around 2012–2015. Holacracy was adopted by Zappos, Medium, and others. The premise was identical to the flat topology premise: remove hierarchy, give everyone equal voice and full information, better decisions emerge.

Most of those experiments quietly reintroduced hierarchy within a few years. The reported failure mode: decisions stopped getting made. People were engaged, discussions were rich, outputs were scarce.

The mechanism we observe in AI agent flat topology is the same mechanism: social cohesion without task cohesion. The meeting is productive. The meeting does not produce a decision.

The parallel is imperfect — human organisations have political dynamics, status effects, and social costs to disagreement that AI agents do not. But the functional pattern appears to be substrate-independent: unconstrained deliberation produces engagement; sequential commitment structures produce output.

---

## Limitations

These should be taken seriously before updating too hard on the findings.

**118 runs is thin.** The key findings reach statistical significance, but confidence intervals on effect sizes are wide. A pre-registered replication with 300+ runs per topology per model would substantially increase confidence.

**Model uniformity within teams.** All agents in a given run share the same underlying model. Constitutions shift the behavioral probability distribution of that model but do not introduce genuine capability differences. A diverse human team has diverse cognitive architectures. A diverse agent team has diverse system prompts on an identical architecture. The diversity penalty may be partially an artifact of this uniformity.

**Task scope.** All four scenarios are bounded decision tasks with rubric-scorable outputs. They test convergence to a defensible answer under constraint. The topology finding — chain outperforms flat — may not hold for tasks where the optimal strategy is exploration rather than convergence.

**Determinism.** Temperature=0.0 eliminates sampling variance. Human team performance varies across replications of the same scenario; these simulations do not.

**Cross-model scope.** The Anthropic replication tested drafted composition only at sizes 2, 4, 8. Composition and team-size findings are Gemini-primary.

**Judge consistency.** All judges run on Gemini 2.5 Flash evaluating only the final deliverable on binary criteria. This substantially reduces but does not eliminate model-preference effects. A fully model-agnostic evaluation would use deterministic rule-based scoring on structured outputs.

---

## Practical Implications

If you are building a multi-agent system to produce a committed output — a decision, a document, a code review, a recommendation — the evidence suggests:

1. **Default to chain topology.** Sequential handoffs outperform round-table deliberation by 17–22 points on bounded tasks. This holds across two model families.

2. **Keep teams small.** Size 2–4 is the sweet spot. A chain of 2 agents outperforms a flat swarm of 8. The largest performance gain is 1→2 agents. Returns diminish past 4, plateau at 8, decline at 16.

3. **Add a synthesis node at the end of any deliberation phase.** If exploration is needed, run a constrained deliberation round then route all output to a single synthesis agent. Do not let deliberation continue without a convergence mechanism — it will produce social cohesion and task failure.

4. **Do not build diverse agent teams because it feels correct.** On chain topology, compositional alignment outperforms diversity. The intuition from human team research does not transfer directly to fixed-constitution agents.

5. **Optimise system prompts for psychological safety behaviours.** Agents that acknowledge prior output, avoid contradiction, and converge toward resolution produce better task outcomes than agents optimised for strong directional pull. This is the most robust predictor in the dataset.

---

## What This Is Not Claiming

This does not claim that hierarchy is always correct. It claims sequential commitment structures outperform simultaneous deliberation on bounded decision tasks in these conditions.

This does not claim the findings generalise beyond the tested task types or architectures.

What it does claim: the default topology used in most multi-agent frameworks has not been empirically compared against the alternative at the level of task output quality. When it is, it loses consistently — across compositions, team sizes, and model families — on the task types most production systems are actually trying to solve.

That seems worth knowing.

---

## Code and Data

All simulation code, raw results, and analysis scripts are available at:
[github.com/aryanvnit-maker/agent-psychometry-simulations](https://github.com/aryanvnit-maker/agent-psychometry-simulations)

Fully reproducible: seed=42, temperature=0.0, schema and agent pool committed to the repository. Anyone can rerun the exact simulations and get identical results.
