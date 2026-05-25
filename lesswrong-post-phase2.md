# Psychometric Profiling Destroys Coding Agent Performance: Phase 2 Data

Phase 1 of this research proved that flat topology produces catastrophic coordination failure on bounded business tasks — a 46-point performance collapse when moving from a sequential chain of 2 agents to a flat swarm of 2 agents. The mechanism was isolated: social cohesion and task cohesion decouple in flat topology. Agents engage, acknowledge, and validate each other while producing no committed output. Moloch in a synthetic system, measured precisely.

Phase 2 tests a harder question: does this hold for deterministic, objectively-scored mathematical execution? And does the psychometric framework that governs agent behavior in Phase 1 transfer to hard coding tasks?

The short answer: the topology finding replicates cleanly. The psychometric finding does not transfer — and the reason why is commercially important.

---

## What Was Tested

100 Codeforces Div. 1 C/D problems (difficulty rating ~2000–2400, the level of competitive programming where naive algorithmic approaches fail and genuine mathematical insight is required). Evaluation metric: pass@1 — the submitted code either solves all private test cases or it doesn't. No rubric, no judge subjectivity, binary ground truth.

Nine agent configurations were tested across 900 total evaluations:

**Topology conditions:**
- Chain-1 generic (single SOLVER agent — baseline)
- Chain-2 generic (balanced IMPLEMENTER + SOLVER, sequential handoff)
- Chain-2 specialized (ALGORITHMIST → IMPLEMENTER, role-separated)

**Extreme psychometric profiles on Chain-1 (negative control — Option A):**
- Analytical: high adaptive intelligence (90), low volatility (10), high ambiguity tolerance (80)
- Chaotic: low adaptive intelligence (10), high volatility (90), low ambiguity tolerance (20)
- Founder: high drive alignment (90), high philosophy cohesion (90), low feedback orientation (10)

**Extreme psychometric profiles on Chain-2 analyzer (experimental — Option B):**
- Same three profiles applied to the ALGORITHMIST analyzer role
- Fixed neutral SOLVER as agent-2 in all three — identical compiler across conditions

All runs at temperature=0.0, Gemini 2.5 Flash. Code evaluated via local subprocess execution with wall-time timeout matching the problem's stated time limit.

---

## Results

| Condition | Pass@1 | Avg Pass Rate | Compilation Errors |
|---|---|---|---|
| Chain-1 generic (baseline) | 12% | 16.4% | 18 |
| Chain-2 generic | **16%** | 20.4% | 22 |
| Chain-2 specialized | 13% | 18.4% | 23 |
| Chain-1 analytical | 11% | 16.1% | 16 |
| Chain-1 chaotic | 14% | 18.9% | 16 |
| Chain-1 founder | 11% | 16.0% | 20 |
| Chain-2 analytical-analyzer | 13% | 18.6% | 15 |
| Chain-2 chaotic-analyzer | 14% | 18.6% | 18 |
| Chain-2 founder-analyzer | 10% | 15.7% | 23 |

---

## Finding 1: Topology Replicates on Hard Math

Chain-2 generic (16%) outperforms chain-1 generic (12%). The sequential forcing function works on deterministic mathematical execution, not just subjective business tasks. This is the clean replication.

The mechanism is the same as Phase 1: agent-1 produces a committed analysis pass, agent-2 receives it as a structured input, and generates code against a concrete prior state. The chain structure compresses entropy at the handoff point. The single-agent baseline lacks this compression and scores lower.

This result extends the Phase 1 finding beyond bounded business scenarios. The topology advantage is not task-specific — it is architectural.

---

## Finding 2: Role Labels Actively Hurt Execution Tasks

Chain-2 specialized — where agent-1 is constitutionally defined as an ALGORITHMIST ("design the algorithm, do not write code, produce a specification an implementer can translate") and agent-2 is an IMPLEMENTER — scores 13%. Compilation errors rise from the chain-2 generic baseline (22) to 23.

This is the LangChain critique made precise. The industry default for multi-agent coding pipelines is to assign occupational identities: "You are a Senior Software Engineer. You are a Code Reviewer. You are an Architecture Lead." The data shows this degrades output quality and increases broken code. The role separation introduces translation loss at the handoff — the ALGORITHMIST produces abstract specifications that the IMPLEMENTER renders as syntactically broken Python.

Chain-2 generic wins not because its agents are more capable, but because they are not constrained by manufactured professional identities. They compress and execute. The corporate org-chart model fails on execution tasks.

---

## Finding 3: The Formatting Constraint Overrides All Behavioral Constraints (Option A)

The three extreme psychometric profiles — analytical, chaotic, founder — applied to a Chain-1 SOLVER agent score 11%, 14%, and 11% respectively. The baseline is 12%. All three cluster within 2 points of the baseline.

This is the negative control. The SOLVER role instruction is explicit: "your entire response must be a single ```python code block. No explanation, no analysis, no text outside the code block." When this instruction is present, the behavioral dimension constraints encoded in the system prompt are completely overridden. A high-volatility agent instructed to express urgency and frustration, simultaneously instructed to output only a silent code block, outputs only a silent code block.

This is not a failure of the psychometric framework. It is a precise identification of the conditions under which it operates. Behavioral dimensions require token space — room to reason, hesitate, express, and exhibit the designated traits — to influence downstream logic. Remove the space, remove the effect. The constitution is not a personality; it is a weighting on the output distribution. With no distribution to weight (only one valid output exists — a code block), the weighting has no target.

---

## Finding 4: Dimension Variation in the Analysis Turn Shows Directional Effects (Option B)

When the same extreme profiles are applied to the ALGORITHMIST analyzer in a Chain-2 setup — where agent-1 has full token space to reason and agent-2 is a fixed neutral compiler — the range is 10–14%.

Founder-analyzer performs worst: 10% pass@1, 23 compilation errors — matching the chain-2 specialized failure pattern. The founder profile (high drive alignment, low feedback orientation, low adaptive intelligence, low ambiguity tolerance) produces the most rigid, least-updated analysis specifications. The fixed SOLVER, receiving a rigid and potentially incorrect algorithm spec, generates more broken code.

Analytical-analyzer (13%) and chaotic-analyzer (14%) perform similarly and sit below chain-2 generic (16%). This is partially confounded — chain-2-[profile]-analyzer uses ALGORITHMIST as the analyzer role while chain-2 generic uses a balanced IMPLEMENTER. The role change and the dimension change were not isolated in separate conditions.

The directional finding holds: the most rigid profile (founder) consistently produces the worst outcome. The spread of 4 points (10–14%) across dimension profiles in Option B, compared to near-zero spread in Option A (11–14%), is consistent with the hypothesis that dimensions manifest when given token space — but the effect size is smaller than predicted and does not overcome the role architecture difference.

---

## The Two-Domain Framework

Combined with Phase 1, the data supports a clean partition:

**Domain A — Exploratory, judgment-based, bounded convergence tasks** (customer support triage, legal clause review, investment memo synthesis, strategic decisions): Flat topology generates Moloch — social engagement without task convergence. The fix is sequential chain topology, N=2, with Kalibr behavioral constraints tuned for dimensional compatibility. The 46-point topology gap measures the cost of ignoring this.

**Domain B — Deterministic execution tasks** (code compilation, precise technical output with binary evaluation): Role-playing personas introduce cognitive drag. Elaborate psychometric profiles applied to the execution layer are inert at best (overridden by formatting constraints) and harmful at worst (produce abstract specs that increase compilation errors). The optimal architecture is chain-2 generic — sequential, minimal constitution, no occupational identity.

The enterprise AI industry applies one architecture to both domains. The data shows this produces a different failure mode in each.

---

## The Moloch Connection in Phase 2

The Phase 1 mechanism — unconstrained social deliberation consuming context without producing convergence — does not appear in Phase 2 chain topologies because the chain structure prevents it. But a subtler version of the same dynamic appears in the ALGORITHMIST → IMPLEMENTER specialization.

The ALGORITHMIST role is constitutionally compelled to be thorough, to enumerate edge cases, to defer code generation. The IMPLEMENTER is constitutionally compelled to request specificity before proceeding. In a handoff chain, these two constraints interact: the ALGORITHMIST over-specifies (consuming tokens on abstraction), and the IMPLEMENTER, receiving an abstract spec without runnable examples, produces code that fails on edge cases the spec described but did not demonstrate. It is a two-agent version of the same information loss: the output that looks most complete is the least executable.

---

## Limitations

**Statistical significance on small differences:** The gap between 16% (chain-2 generic) and 13% (chain-2 analytical-analyzer) on N=100 binary outcomes is directional, not conclusive. A pre-registered replication with 300 problems per condition would be required to reach publishable effect size confidence.

**Unresolved confound in Option B:** The analyzer conditions changed both the role (IMPLEMENTER → ALGORITHMIST) and the dimension profile simultaneously. The dimension effect and the role effect are not cleanly separated. A control condition — ALGORITHMIST with balanced 75-baseline dimensions — was not run.

**Task domain:** All CP problems are from a single source (CodeContests, Codeforces origin, difficulty 12–13). Results on different execution task types (SQL generation, systems programming, mathematical proofs) may differ.

**Model uniformity:** All agents use the same underlying model. Behavioral constraints shift the output distribution of that model but do not introduce genuine cognitive differences between agents. This is a design choice, not a limitation, but it bounds the generalizability claim.

---

## Practical Implications

For teams building multi-agent coding pipelines:

1. **Stop writing elaborate agent personas for code generation.** The data shows role-playing identities ("You are a Senior Python Engineer with 10 years of experience") do not improve pass@1 and increase compilation error rates when role constraints conflict with execution requirements.

2. **Use sequential chain topology with N=2.** A generic analysis agent followed by a generic code generation agent outperforms all specialized and psychometrically elaborate configurations tested.

3. **Reserve psychometric profiling for the analysis layer.** The Option B results show directional effects from dimension variation in the reasoning phase. Profiles that increase rigidity (low adaptive intelligence, low ambiguity tolerance, low feedback orientation) consistently underperform on tasks where the specification needs to adapt to problem constraints.

4. **The task type determines the architecture.** The correct architecture for a coding agent and the correct architecture for a business judgment agent are not the same. Systems that apply identical orchestration patterns to both domains are leaving performance on the table in both.

---

## Open Questions

**Does the ALGORITHMIST confound explain the full Option B result?** Running ALGORITHMIST with balanced 75-baseline dimensions would isolate whether the underperformance relative to chain-2 generic comes from the role, the extreme profiles, or their interaction.

**Does the topology finding hold on easier problems?** Div. 1 C/D problems test the ceiling of algorithmic reasoning. At easier difficulty levels (where the model can solve problems reliably), the chain-2 advantage may shrink or disappear — the handoff only adds value when the problem requires a genuine analysis pass.

**Can dimension effects in the analysis layer be amplified by task design?** The Kalibr dimensions are team-coordination instruments. They manifest most clearly when the task structure gives them something to act on — ambiguity to tolerate, feedback to integrate, constraints to discover. A task specifically designed to stress these dynamics (deliberately underspecified problem, iterative refinement required) may produce larger dimension effects in the analysis layer than the fixed CP benchmark.

The full codebase, agent constitutions, problem dataset, and evaluation harness are on the Phase 2 branch of the repository.

*This research was conducted independently, without institutional funding or affiliation.*

— Aryan V. | Independent AI Systems Research
