# AI Agent Swarms Reproduce the Failure Modes of Flat Human Organisations

Most multi-agent AI systems are built with flat topology — all agents see everything, all agents respond, everyone deliberates together. This feels correct. More perspectives, more information sharing, better output.

We ran 91 controlled simulations to test it. The flat topology consistently underperformed sequential chains by 33 points on task scores (0–100, rubric-graded). The mechanism is visible in the data and it connects directly to 40 years of human organisational research.

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

We ran each team through four structured business scenarios covering strategic decision-making, zero-sum resource allocation, post-mortem analysis, and crisis response. Three independent judge agents — tuned for analytical neutrality — scored each transcript against explicit rubrics on a 0–100 scale. Judges received the full transcript plus the rubric; they did not receive any metadata about team composition or topology. This means judges score both the quality of the final output *and* the deliberation that produced it, which creates a potential formatting bias: an LLM judge may favour transcripts that read like clean sequential reasoning over messy multi-speaker deliberation, regardless of output merit. This is noted in Limitations. All agents run on the same underlying model (Gemini 2.5 Flash) at temperature=0.0, making every run fully deterministic and reproducible.

Two topologies were tested:

**Chain** — linear sequential handoff: A → B → C → END. Each agent receives full conversation history but produces output only once, in order. No agent can reopen what a prior agent settled.

**Flat** — round-table: every agent speaks once per round for two rounds, receiving the full conversation history from all prior speakers. Perfect information. No routing cost. Theoretical upper bound.

91 total runs: 51 chain, 40 flat.

---

## Results

### The Single-Agent Baseline

Before comparing topologies, establish the floor: a single agent working alone, no coordination cost.

| Condition | Task Score (0–100) |
|---|---|
| Single agent, chain | 10.0 |
| Single agent, flat | 35.4 |

The chain single-agent score is low because a lone agent in chain topology receives the scenario once and produces one response — no iterative prompting. The flat single-agent gets two structured rounds of prompting, which improves output substantially.

Now add a second agent in flat topology: **16.3.**

Adding a second agent to a flat swarm dropped performance from 35.4 to 16.3 — a 19-point decrease. The flat topology's coordination overhead destroyed more value than the second agent contributed. This is not inefficiency. It is active degradation.

### Topology (All Team Sizes, Mean Score 0–100)

| Topology | Mean Task Score |
|---|---|
| Chain | 70.2 |
| Flat | 36.9 |
| **Gap** | **−33.3** |

| Team Size | Chain | Flat | Δ |
|---|---|---|---|
| 1 | 10.0 | 35.4 | +25.4 |
| 2 | 60.8 | 16.3 | −44.5 |
| 4 | 76.8 | 38.9 | −37.9 |
| 8 | 85.8 | 54.4 | −31.4 |

A chain of 2 agents (60.8) outperforms a flat swarm of 8 (54.4). The coordination overhead of flat topology is not overcome by adding more agents — it compounds.

This gap is not composition-specific. Every composition performs worse in flat than chain:

| Composition | Chain | Flat | Δ |
|---|---|---|---|
| Founder-brained | 82.2 | 41.0 | −41.2 |
| Homogeneous | 72.8 | 42.4 | −30.4 |
| Drafted (diverse) | 57.8 | 29.4 | −28.4 |

The flat topology penalty is consistent, large, and topology-controlled. It is not a noise artefact.

---

## The Diversity Finding

Most enterprise teams building agent swarms compose them the way HR taught them to: a Coder, a Critic, a Planner. Diverse roles, diverse perspectives, better outcomes. This is the Bell (2007) intuition applied to AI.

It is wrong, by the data here.

Diverse teams (drafted composition — captain-selected to maximise dimensional coverage) finished last in every condition tested:

| Composition | Chain | Flat |
|---|---|---|
| Founder-brained | 82.2 | 41.0 |
| Homogeneous | 72.8 | 42.4 |
| **Drafted (diverse)** | **57.8** | **29.4** |

We initially flagged this as a possible chain topology artifact: sequential handoffs limit information flow, maybe diverse agents couldn't coordinate across the constraint. We ran flat topology — perfect information, every agent sees everything — precisely to test that hypothesis. The inversion survived. Diverse teams finished last in flat topology too.

**The Bell (2007) inversion is structural, not topological.**

The mechanism: agent constitutions are fixed behavioral constraints, not adaptive strategies. A diverse team means agents with incompatible behavioral profiles — one agent is constitutionally compelled to challenge, another to seek consensus, another to defer. Human team members with diverse personalities adapt to each other over time. Agent constitutions don't adapt. The incompatibility produces constraint collision, which degrades output directly.

The exact system prompts for each composition condition are in the repository. The drafted (diverse) team prompts in particular show the specific constraint combinations that produce the deadlock pattern — they are worth examining directly if you want to reproduce or challenge this finding.

This finding has a narrow scope: *cognitive diversity as implemented through fixed behavioral constraints hurts performance on bounded decision tasks*. It does not generalise to capability diversity (different models for different roles), dynamic constitutions, or open-ended tasks where constraint collision might produce genuinely novel directions. But for the task types most production swarms are actually running, the diversity premium is a liability.

---

### The Mechanism: Social Cohesion ≠ Task Cohesion

This is where the data becomes more interesting than just "chain wins."

We scored transcripts on two GEQ (Group Environment Questionnaire) dimensions: task cohesion (did agents converge on a shared output?) and social cohesion (did agents engage with each other's contributions?). These are validated distinct constructs from human team research (Carron et al., 1985).

**Chain topology:** task cohesion and social cohesion track within 8.9 points of each other across all compositions.

**Flat topology:** average gap is 37 points. Social cohesion stays high (65–81) while task cohesion collapses (29–52).

In flat topology, agents are socially present and taskfully absent. FIRO inclusion scores — measuring what fraction of agents were addressed by other agents — hit 1.00 in flat topology. Every agent talks to every other agent. Nobody produces a committed output.

This is not a subtle effect. It is the entire mechanism. Flat topology produces complete social engagement and near-complete task failure. The agents are having the meeting. The meeting is not producing a decision.

---

## What Does Replicate

Two findings from human research hold clearly across both topologies:

**Google Project Aristotle (psychological safety):** The psychological safety composite — operationalised as consensus achievement + low contradictions + high inclusion — predicts task score at r=0.66\*\*\* in chain and r=0.77\*\*\* in flat. It is the strongest predictor in the dataset and the only one that is significant in both topologies. Diversity, by contrast, shows r=0.48\*\*\* in chain and r=0.17 (n.s.) in flat. Psychological safety outperforms diversity as a predictor in both conditions.

**TCI Innovation Climate:** TCI innovation scores correlate with novel approach counts at r=0.81\*\*\* in chain and r=0.89\*\*\* in flat. The innovation climate instrument successfully predicts which teams generate non-obvious approaches. This is the cleanest replication in the dataset.

**Barrick et al. (1998) — directional:** The finding that conscientiousness variance predicts performance better than conscientiousness mean holds directionally in chain (variance r=0.53\*\*\* vs mean r=0.19 n.s.) but loses statistical significance in flat, likely due to the topology-induced score compression.

---

## The Human Org Parallel

This is not a new pattern. It has a 20-year history in human organisations.

The flat organisation movement peaked around 2012–2015. Holacracy was adopted by Zappos, Medium, and others. The premise was identical to the flat topology premise: remove hierarchy, give everyone equal voice and full information, better decisions emerge.

Most of those experiments quietly reintroduced hierarchy within a few years. The reported failure mode: decisions stopped getting made. People were engaged, discussions were rich, outputs were scarce.

The mechanism we observe in AI agent flat topology is the same mechanism: social cohesion without task cohesion. The meeting is productive. The meeting does not produce a decision.

The parallel is imperfect — human organisations have political dynamics, status effects, and social costs to disagreement that AI agents do not. But the functional pattern appears to be substrate-independent: unconstrained deliberation produces engagement; sequential commitment structures produce output.

Conway's Law states that systems tend to mirror the communication structures of the organisations that build them. The inverse may also be true: organisations that study how their communication structures affect output quality can design better systems. The implication for AI is that structure is not bureaucratic overhead — it is the mechanism by which individual contributions become collective decisions.

---

## Limitations

These should be taken seriously before updating too hard on the findings.

**91 runs is thin.** The key findings reach statistical significance, but confidence intervals on effect sizes are wide. The Bell inversion finding in particular — which is the most novel claim — rests on 51 chain runs and 40 flat runs across 4 scenarios. A pre-registered replication with 200+ runs per topology would substantially increase confidence.

**Model uniformity.** All 35 agents (32 workers + 3 judges) run on the same underlying model. Agent constitutions shift the behavioral probability distribution of that model, but they do not introduce the genuine capability differences that exist between actual human team members. A diverse human team has diverse cognitive architectures. A diverse agent team has diverse system prompts applied to an identical architecture. These are not the same thing. The diversity penalty may be partially an artifact of this uniformity.

**Task scope.** All four scenarios are bounded decision tasks with rubric-scorable outputs. They test convergence to a defensible answer under constraint. They do not test open-ended research, creative generation, or long-horizon planning. The topology finding in particular — chain outperforms flat — may not hold for tasks where the optimal strategy is exploration rather than convergence.

**Determinism.** Temperature=0.0 eliminates sampling variance. Human team performance varies across replications of the same scenario; these simulations do not. This is useful for reproducibility and harmful for generalisability.

**No capability diversity.** All agents are restricted to the same model. Real swarm architectures often combine a large general model with smaller specialist models. That architecture is neither chain nor flat as defined here and is not covered by this data.

**Judge formatting bias.** LLM judges process tokens sequentially via attention mechanisms and may structurally favour transcripts that read as clean linear reasoning over messy multi-speaker deliberation. Judges here evaluated full transcripts, not isolated final outputs. If this bias exists, it would inflate chain scores relative to flat scores — meaning the 33-point gap may be partially an evaluation artefact rather than a pure output quality difference. Isolating judges to final extracted answers only would partially control for this; it is the first thing to test in a replication.

---

## Practical Implications

If you are building a multi-agent system to produce a committed output — a decision, a document, a code review, a recommendation — the evidence suggests:

1. **Default to chain topology.** Sequential handoffs where each agent builds on committed prior output outperform round-table deliberation by a large margin on bounded tasks.

2. **Add a synthesis node at the end of any deliberation phase.** If you need exploration before commitment, run a constrained deliberation round then route all output to a single synthesis agent whose explicit job is to produce the committed output. Do not let the deliberation loop continue.

3. **Do not build diverse agent teams because it feels correct.** Compositional alignment — agents whose behavioral profiles are compatible for the task — outperforms diversity on every task type tested here. This is the most counterintuitive finding and the one most likely to be wrong for task types not covered here.

4. **Optimise system prompts for psychological safety behaviours.** Agents that acknowledge prior output, avoid contradiction, and converge toward resolution produce better task outcomes than agents optimised for narrow capability. This is the most robust finding in the dataset.

5. **Team size ceiling is around 8 for chain topology.** Size 1→2 produces +50 points. Size 4→8 produces +9 points. Size 8→16 is slightly negative. The marginal return on additional agents flattens quickly.

---

## What This Is Not Claiming

This does not claim that hierarchy is always correct. It claims sequential commitment structures outperform simultaneous deliberation on bounded decision tasks in these conditions.

This does not claim the findings generalise beyond the tested task types, model, or architecture.

What it does claim: the default topology used in most multi-agent frameworks has never been empirically compared against the alternative at the level of task output quality, and when it is, it loses badly on the task types most production systems are actually trying to solve.

That seems worth knowing.

---

## Code and Data

All simulation code, raw results, and analysis scripts are available at:
[github.com/aryanvnit-maker/agent-psychometry-simulations](https://github.com/aryanvnit-maker/agent-psychometry-simulations)

Fully reproducible: seed=42, temperature=0.0, schema and agent pool committed to the repository. Anyone can rerun the exact simulations and get identical results.
