# AI Agent Swarms Reproduce the Failure Modes of Flat Human Organisations

Most multi-agent AI systems are built with flat topology — all agents see everything, all agents respond, everyone deliberates together. This feels correct. More perspectives, more information sharing, better output.

118 controlled simulations across two model families tested it. Flat topology consistently underperformed sequential chains by 17–22 points on task scores (0–100, rubric-graded against final deliverables only). The mechanism is visible in the data and connects directly to 40 years of human organisational research.

The less expected finding: for bounded execution tasks, multi-agent chains peak at N=2. Adding agents to a flat topology imposes a coordination tax — 46 points of performance loss while multiplying compute costs. More agents, worse output, higher bill.

---

## Background: The Default Is Unexamined

The major multi-agent frameworks — CrewAI, AutoGen, many LangGraph implementations — default to patterns where agents share a full context window and contribute simultaneously or in loosely ordered rounds. Call this flat topology: every agent has perfect information, every agent speaks, no agent is structurally forced to commit to what came before.

This default was chosen because it is easy to implement and intuitively appealing. It was not chosen because anyone measured the output quality against the alternative.

It was measured.

---

## What Was Built and Measured

A simulation infrastructure was built using the Kalibr psychometric framework — a 10-dimension behavioral assessment tool — to assign distinct personality profiles to 32 AI agents. Each agent's system prompt (its *constitution*) is generated from its dimensional scores across dimensions including drive alignment, adaptive intelligence, volatility, ambiguity tolerance, and feedback orientation. Scores ≥70 produce high-expression behaviours; scores ≤30 produce low-expression behaviours. The same threshold logic that generates a human behavioral report generates an agent's operating constraints.

These agents were composed into teams of 1, 2, 4, 8, and 16 under three composition conditions:

- **Drafted** — captain selects teammates to maximise dimensional diversity (gap-filling)
- **Homogeneous** — teammates selected for minimum dimensional variance
- **Founder-brained** — high Drive Alignment, high Philosophy Cohesion, high Volatility; mirrors early-stage startup team culture

Each team ran through four structured business scenarios: strategic product decisions, zero-sum resource allocation, post-mortem analysis, and crisis response.

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

Adding a second agent to a flat swarm dropped performance from 31.2 to 10.7 — a 21-point decrease. The coordination tax destroyed more value than the second agent contributed. This is active degradation, not inefficiency.

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

A chain of 2 agents (57.6) outperforms a flat swarm of 8 (19.1). The coordination tax of flat topology is not overcome by adding more agents — it compounds.

This gap is not composition-specific:

| Composition | Chain | Flat | Δ |
|---|---|---|---|
| Homogeneous | 48.6 | 17.1 | −31.5 |
| Drafted (diverse) | 37.7 | 26.1 | −11.5 |
| Founder-brained | 35.1 | 26.4 | −8.7 |

The flat topology penalty is consistent across all compositions.

### Cross-Model Replication

24 additional combinations were run using Anthropic Claude 3.5 Sonnet as the worker model (judges remained on Gemini throughout). Drafted composition only, team sizes 2, 4, 8.

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

Transcripts were scored on two GEQ (Group Environment Questionnaire) dimensions: task cohesion (did agents converge on a shared output?) and social cohesion (did agents engage with each other's contributions?). These are validated distinct constructs from human team research (Carron et al., 1985).

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

This is not a new pattern in the study of collective decision-making.

The premise of flat organisational design is identical to the flat topology premise: remove hierarchy, give everyone equal voice and full information, better decisions emerge. The empirical record on that premise is long enough to draw conclusions from. Decisions stop getting made. People are engaged, discussions are rich, outputs are scarce.

The mechanism observed in AI agent flat topology is the same mechanism: social cohesion without task cohesion. The meeting is productive. The meeting does not produce a decision.

This pattern appears to be substrate-independent. The physics of it: unconstrained deliberation maximises the entropy of contributions. Sequential commitment structures reduce entropy at each step, compressing prior discussion into a forward state. Convergence requires entropy reduction. Flat topology defers it indefinitely.

Conway's Law states that systems mirror the communication structures of the organisations that build them. The data here suggests the inverse holds too: the communication structure you impose on your agent system determines what class of output it can produce. Structure is not bureaucratic overhead. It is the mechanism by which individual contributions become collective decisions.

---

## Limitations

These should be taken seriously before updating too hard on the findings.

**118 runs is thin.** The key findings reach statistical significance, but confidence intervals on effect sizes are wide. A pre-registered replication with 300+ runs per topology per model would substantially increase confidence.

**Model uniformity within teams.** All agents in a given run share the same underlying model. Constitutions shift the behavioral probability distribution of that model but do not introduce genuine capability differences. A diverse human team has diverse cognitive architectures. A diverse agent team has diverse system prompts on an identical architecture. The diversity penalty may be partially an artifact of this uniformity.

**Task scope.** All four scenarios are bounded decision tasks with rubric-scorable outputs. They test convergence to a defensible answer under constraint. The N=2 performance peak and the topology finding apply specifically to this class of task. Generative, exploratory, or divergent tasks — brainstorming, requirements discovery, open-ended research — likely follow different topological dynamics and have not been tested here.

**Determinism.** Temperature=0.0 eliminates sampling variance. Human team performance varies across replications of the same scenario; these simulations do not.

**Cross-model scope.** The Anthropic replication tested drafted composition only at sizes 2, 4, 8. Composition and team-size findings are Gemini-primary.

**Judge consistency.** All judges run on Gemini 2.5 Flash evaluating only the final deliverable on binary criteria. This substantially reduces but does not eliminate model-preference effects. A fully model-agnostic evaluation would use deterministic rule-based scoring on structured outputs.

---

## Practical Implications

If you are building a multi-agent system to produce a committed output — a decision, a document, a code review, a recommendation — the evidence suggests:

1. **Default to chain topology.** Sequential handoffs outperform round-table deliberation by 17–22 points on bounded tasks. This holds across two model families.

2. **Keep teams small.** For bounded execution tasks, size 2–4 is the performance peak. A chain of 2 agents outperforms a flat swarm of 8. The largest gain is 1→2 agents. Returns diminish past 4, decline past 8.

3. **Add a synthesis node at the end of any deliberation phase.** If exploration is needed, run a constrained deliberation round then route all output to a single synthesis agent. Do not let deliberation continue without a convergence mechanism — it will produce social cohesion and task failure.

4. **Do not build diverse agent teams because it feels correct.** On chain topology, compositional alignment outperforms diversity. The intuition from human team research does not transfer directly to fixed-constitution agents.

5. **Optimise system prompts for psychological safety behaviours.** Agents that acknowledge prior output, avoid contradiction, and converge toward resolution produce better task outcomes than agents optimised for strong directional pull. This is the most robust predictor in the dataset.

---

## An Open Challenge

The findings here cover four scenario types, two model families, and three composition conditions. The infrastructure is public and fully reproducible at seed=42, temperature=0.0.

Three questions this dataset cannot answer that the community could:

**Does the coordination tax hold on generative tasks?** The N=2 ceiling and the chain advantage were measured on convergence tasks with binary rubric criteria. Brainstorming, creative generation, and open-ended research may favour flat topology precisely because they benefit from entropy rather than compression. This is the most important boundary condition to test.

**Does the topology finding hold with heterogeneous model families within a single team?** This study held the worker model constant within runs. A team where one agent is a large general model and others are smaller specialists — the architecture many production systems use — is neither chain nor flat as defined here. How topology interacts with within-team model heterogeneity is untested.

**Does a hybrid topology outperform pure chain?** The data shows flat deliberation followed by chain synthesis should theoretically capture the exploration benefits of flat while forcing convergence. Flat and chain were run as isolated conditions. A deliberation-then-chain hybrid was not tested. If you run it, publish the delta.

The simulation code, agent pool, scenarios, and evaluation harness are at:
[github.com/aryanvnit-maker/agent-psychometry-simulations](https://github.com/aryanvnit-maker/agent-psychometry-simulations)

*This research was conducted independently, without institutional funding or affiliation.*

— Aryan S. | Independent AI Systems Research
