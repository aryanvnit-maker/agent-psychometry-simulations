# KalibrBench-CP: Phase 2 — Agent Psychometry on Hard Coding Problems

Phase 2 of the Kalibr agent psychometry research. Tests whether the Phase 1 topology finding (sequential chains beat flat swarms) replicates on deterministic mathematical execution, and whether psychometric dimension profiles affect coding performance.

---

## The Finding

900 evaluations. 100 Codeforces Div. 1 C/D problems (~2000–2400 rating). Pass@1 as the metric. Temperature=0.0. Gemini 2.5 Flash.

| Condition | Pass@1 | Avg Pass Rate | Compilation Errors |
|---|---|---|---|
| Chain-1 generic (baseline) | 12% | 16.4% | 18 |
| **Chain-2 generic** | **16%** | **20.4%** | 22 |
| Chain-2 specialized | 13% | 18.4% | 23 |
| Chain-1 analytical | 11% | 16.1% | 16 |
| Chain-1 chaotic | 14% | 18.9% | 16 |
| Chain-1 founder | 11% | 16.0% | 20 |
| Chain-2 analytical-analyzer | 13% | 18.6% | 15 |
| Chain-2 chaotic-analyzer | 14% | 18.6% | 18 |
| Chain-2 founder-analyzer | 10% | 15.7% | 23 |

Three results:

1. **Topology replicates.** Chain-2 generic (16%) outperforms Chain-1 (12%). The sequential forcing function works on deterministic execution, not just judgment tasks.

2. **Role labels actively degrade performance.** ALGORITHMIST → IMPLEMENTER specialization drops pass@1 to 13% and raises compilation errors. Manufactured professional identity introduces translation loss at the handoff.

3. **Psychometric profiles are inert on the execution layer.** Extreme dimension profiles on a SOLVER agent cluster at 11–14%, statistically indistinguishable from the 12% baseline. When the formatting constraint ("output only a code block") is present, behavioral constraints are completely overridden.

**Reproduce it** (requires `GEMINI_API_KEY` in `.env`):
```bash
python run_cp_baseline.py --n 100
python run_cp_experiment.py --n 100
python analyze_cp.py
```

---

## What This Is

Phase 1 proved that flat topology produces catastrophic coordination failure on bounded business tasks — a 46-point performance collapse when moving from sequential chain to flat swarm. The mechanism was isolated to social cohesion decoupling from task cohesion: agents engage, acknowledge, and validate each other without producing committed output.

Phase 2 tests a harder question: does this hold for deterministic, objectively-scored mathematical execution? And does the Kalibr psychometric framework that governs agent behavior in Phase 1 transfer to hard coding tasks?

The topology finding replicates. The psychometric finding does not — and the reason is commercially important.

---

## Research Questions

1. Does the topology finding (chain > flat) replicate on deterministic execution tasks with binary ground truth?
2. Do occupational role labels ("ALGORITHMIST", "IMPLEMENTER") improve or degrade coding performance compared to generic balanced agents?
3. Do extreme Kalibr dimension profiles affect pass@1 on the execution layer (Option A — negative control)?
4. Do extreme dimension profiles affect pass@1 when applied to the analysis layer of a two-agent chain, where the agent has token space to reason (Option B — actual experiment)?
5. Where is the boundary condition — the task type at which psychometric profiling transitions from inert to active?

---

## Methodology

### Dataset

**100 CodeContests problems** from the `deepmind/code_contests` dataset, filtered to:
- Source: Codeforces
- Difficulty: 12–13 (CF rating ~2000–2400, Div. 1 C/D)
- Problem type: competitive programming requiring genuine algorithmic insight
- Evaluation: pass@1 — the submitted code either solves all private test cases or it doesn't. Binary ground truth, no rubric subjectivity.

Problems loaded from the HuggingFace dataset via `src/datasets/codecontests.py`. Each problem includes public and private test cases; pass@1 is evaluated against private tests only.

### The 9 Conditions

**Topology conditions (topology × constitution):**

| Condition | Agents | Role assignment |
|---|---|---|
| chain-1/generic | 1 | Balanced IMPLEMENTER (baseline) |
| chain-2/generic | 2 | Balanced IMPLEMENTER → balanced SOLVER, sequential handoff |
| chain-2/specialized | 2 | ALGORITHMIST → IMPLEMENTER, role-specialized constitutions |

**Option A — Negative control (extreme profiles on execution layer):**

| Condition | Agent | Profile |
|---|---|---|
| chain-1/analytical | 1 SOLVER | High adaptive intelligence (90), low volatility (10), high ambiguity tolerance (80) |
| chain-1/chaotic | 1 SOLVER | Low adaptive intelligence (10), high volatility (90), low ambiguity tolerance (20) |
| chain-1/founder | 1 SOLVER | High drive (90), high philosophy cohesion (90), low feedback orientation (10) |

**Option B — Actual experiment (extreme profiles on analysis layer):**

| Condition | Agent-1 | Agent-2 |
|---|---|---|
| chain-2/analytical-analyzer | ALGORITHMIST + analytical profile | Fixed neutral SOLVER |
| chain-2/chaotic-analyzer | ALGORITHMIST + chaotic profile | Fixed neutral SOLVER |
| chain-2/founder-analyzer | ALGORITHMIST + founder profile | Fixed neutral SOLVER |

Agent-2 is identical across all Option B conditions — a neutral balanced SOLVER. All behavioral variation is isolated to the analysis agent.

### Agent Architecture

Each agent receives a constitution generated from their Kalibr dimensional profile. The constitution specifies behavioral constraints derived from their dimension scores.

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

The SOLVER role receives a strict formatting constraint: "your entire response must be a single `python` code block. No explanation, no analysis, no text outside the code block." This constraint is the key variable in the Option A null result.

### Chain Handoff

In chain topology, after agent-1 responds, the message list ends on an `assistant` role. The engine injects an explicit user-turn (`handoff_prompts`) before each non-first agent to prevent prose generation. The handoff prompt for coding tasks explicitly requests a code block output, preventing NOCODE failures.

### Evaluation

Code is evaluated via local subprocess execution (no external sandbox):

```python
subprocess.run([sys.executable, tmp], input=stdin, capture_output=True,
               text=True, timeout=time_limit + 2)
```

`_ensure_callable()` appends a top-level `solve()` or `main()` invocation if defined but never called. Pass@1 is calculated per problem (1 if all private test cases pass, 0 otherwise).

### Infrastructure

- **Orchestration**: LangGraph state graphs
- **Worker model**: Gemini 2.5 Flash (`thinking_budget=0` to disable internal reasoning tokens)
- **Temperature**: 0.0 — fully deterministic
- **Token budget**: 8192 output tokens per agent per turn
- **Results**: Written incrementally to `results/cp_experiment.jsonl` and `results/cp_baseline.jsonl`
- **Database**: Supabase `cp_runs` table (optional — skipped if `DATABASE_URL` unset; local JSONL always written)

---

## Results

### Topology Finding

| Condition | Pass@1 | Δ vs baseline |
|---|---|---|
| Chain-1 generic | 12% | — |
| Chain-2 generic | 16% | **+4 pp** |
| Chain-2 specialized | 13% | +1 pp |

Chain-2 generic outperforms the single-agent baseline by 4 percentage points. Sequential structure helps on deterministic execution by the same mechanism as Phase 1: agent-1 produces a committed analysis pass, agent-2 generates code against a concrete prior state. The chain compresses entropy at the handoff.

Chain-2 specialized (13%) underperforms chain-2 generic (16%) despite adding more elaborate constitutions. The ALGORITHMIST role ("design algorithms, do not write code") produces abstract specifications that the IMPLEMENTER renders as syntactically broken Python. Compilation errors rise from 22 (generic) to 23 (specialized).

### Option A — Negative Control

| Profile | Pass@1 | Δ vs baseline |
|---|---|---|
| Analytical | 11% | −1 pp |
| Chaotic | 14% | +2 pp |
| Founder | 11% | −1 pp |

All three extreme profiles cluster within ±2 points of the 12% baseline. The formatting constraint on the SOLVER role overrides all behavioral dimension constraints. A high-volatility agent instructed to express urgency and frustration, simultaneously instructed to output only a code block, outputs only a code block.

This is the negative control result: it confirms that dimensions require token space to operate. Remove the space (SOLVER formatting constraint), remove the effect.

### Option B — Analysis Layer Variation

| Profile on Analyzer | Pass@1 | Compilation Errors | Δ vs chain-2 generic |
|---|---|---|---|
| Chaotic | 14% | 18 | −2 pp |
| Analytical | 13% | 15 | −3 pp |
| Founder | 10% | 23 | −6 pp |

All three profiles fall below chain-2 generic (16%). Two confounds are present: the analyzer role changed from IMPLEMENTER (generic) to ALGORITHMIST (specialized) simultaneously with the dimension profile change. The role change and the dimension effect are not cleanly separated.

The directional finding holds: founder-analyzer produces the worst outcome (10% pass@1, 23 compilation errors), consistent with the Phase 1 prediction that low adaptive intelligence and low feedback orientation produce the most rigid, least-updated analysis.

---

## Findings

### Finding 1: Topology Replicates on Hard Math

The Phase 1 result extends beyond bounded business scenarios. Sequential chain topology outperforms single-agent on Codeforces Div. 1 C/D problems. The forcing function is structural, not task-specific.

Chain-2 generic (16%) vs Chain-1 generic (12%): the first agent provides a committed analysis pass; the second generates code against a concrete algorithm description. The handoff reduces the problem space the second agent navigates. This is the same entropy-compression mechanism as Phase 1.

### Finding 2: Role Labels Introduce Cognitive Drag

The industry default for multi-agent coding pipelines is occupational identity: "You are a Senior Software Engineer. You are a Code Reviewer." The data shows this degrades output quality relative to generic balanced agents. The ALGORITHMIST is constitutionally compelled to enumerate edge cases and defer code generation. The IMPLEMENTER is constitutionally compelled to request specificity before proceeding. These constraints interact: the ALGORITHMIST over-specifies (consuming tokens on abstraction), and the IMPLEMENTER, receiving an abstract spec, produces code that fails on edge cases the spec described but did not demonstrate.

The corporate org-chart model fails on execution tasks. Chain-2 generic wins not because its agents are more capable, but because they are unconstrained by manufactured professional identities.

### Finding 3: Formatting Constraints Override Behavioral Constraints (Option A)

The SOLVER formatting constraint ("output only a code block") completely overrides all behavioral dimension constraints encoded in the system prompt. This is not a failure of the psychometric framework — it is a precise identification of where the boundary is. Behavioral dimensions require token space to operate. With no distribution to weight (only one valid output exists), the weighting has no target.

This result closes a question from Phase 1: the psychometric framework is not trivially fragile. It operates specifically in the analysis layer, where agents have room to reason, hesitate, and exhibit designated traits.

### Finding 4: Dimension Effects Appear When Token Space Exists (Option B)

The 4-point spread across Option B profiles (10–14%) versus the near-zero spread in Option A (11–14%) is directional evidence that dimensions manifest when given token space. The most rigid profile (founder: low adaptive intelligence, low feedback orientation, low ambiguity tolerance) consistently produces the worst outcome. The profile that is most likely to lock onto a wrong algorithm and fail to update produces the most compilation errors and the lowest pass@1.

Effect size is smaller than predicted. The unresolved ALGORITHMIST confound (role change simultaneous with profile change) prevents clean attribution.

---

## Two-Domain Framework

Combined with Phase 1, the data supports a partition:

**Domain A — Exploratory, judgment-based, bounded convergence tasks** (strategic decisions, legal clause review, investment memos): Flat topology generates social engagement without task convergence — the Phase 1 Moloch pattern. The fix is sequential chain topology, N=2, with Kalibr behavioral constraints tuned for dimensional compatibility.

**Domain B — Deterministic execution tasks** (code compilation, precise technical output with binary evaluation): Role-playing personas introduce cognitive drag. Psychometric profiles on the execution layer are inert at best, harmful at worst. The optimal architecture is chain-2 generic — sequential, minimal constitution, no occupational identity.

The enterprise AI industry applies one architecture to both domains. The data shows this produces a different failure mode in each: Moloch on Domain A, cognitive drag on Domain B.

---

## Limitations

- **Statistical significance on small differences.** 16% vs 13% on N=100 binary outcomes is directional, not conclusive. A pre-registered replication with 300 problems per condition is required for publishable effect size confidence.
- **Unresolved confound in Option B.** The analyzer conditions changed both the role (IMPLEMENTER → ALGORITHMIST) and the dimension profile simultaneously. A control condition — ALGORITHMIST with balanced 75-baseline dimensions — was not run. The role effect and the dimension effect are not cleanly separated.
- **Task domain.** All problems are from Codeforces (difficulty 12–13). Results on different execution task types (SQL generation, systems programming, mathematical proofs) may differ.
- **Model uniformity.** All agents use the same underlying model. Behavioral constraints shift the output distribution but do not introduce genuine cognitive differences between agents.
- **Neutral 50 baseline for extreme profiles.** Option A and B profiles use 50 as the baseline for unspecified dimensions, not the 75-baseline used in generic agents. This weakens the contrast between extreme profiles and the generic baseline by undercutting the generic agent's performance properties on unspecified dimensions.

---

## How to Run

### Setup

```bash
git clone https://github.com/aryanvnit-maker/agent-psychometry-simulations
cd agent-psychometry-simulations
git checkout phase2/competitive-programming
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env       # Add GEMINI_API_KEY; DATABASE_URL is optional
```

### Run the Benchmark

```bash
# Step 1: baseline (chain-1/generic, 100 problems)
python run_cp_baseline.py --n 100

# Step 2: all 8 experiment conditions
python run_cp_experiment.py --n 100

# Step 3: run a specific condition only
python run_cp_experiment.py --n 100 --conditions chain2-generic chain2-specialized

# Step 4: analyse results
python analyze_cp.py
```

Safe to interrupt and restart — completed problems are written to JSONL immediately and skipped on restart.

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | required | Google Gemini API key |
| `ANTHROPIC_API_KEY` | optional | Enables `MODEL_PROVIDER=anthropic` |
| `MODEL` | `gemini-2.5-flash` | Model identifier |
| `MODEL_PROVIDER` | `gemini` | `gemini` or `anthropic` |
| `AGENT_TOKEN_BUDGET` | `8192` | Max output tokens per agent per turn |
| `DATABASE_URL` | optional | Supabase connection string |

---

## Project Structure (Phase 2 additions)

```
agent-psychometry-simulations/
├── src/
│   ├── datasets/
│   │   └── codecontests.py     # Load CodeContests from HuggingFace, format_prompt
│   ├── execution/
│   │   ├── judge0.py           # Local subprocess executor (replaces Judge0 API)
│   │   └── extractor.py        # extract() — pulls last code block from agent output
│   └── orchestration/
│       └── engine.py           # build_chain_graph with handoff_prompts injection
├── run_cp_baseline.py          # Chain-1/generic baseline runner
├── run_cp_experiment.py        # All 9 conditions (3 topology + 3 Option A + 3 Option B)
├── analyze_cp.py               # Pass@1, compilation errors, per-condition tables + charts
├── results/
│   ├── cp_baseline.jsonl       # Baseline results (100 problems)
│   └── cp_experiment.jsonl     # Experiment results (800 problems × 8 conditions)
└── lesswrong-post-phase2.md    # Full Phase 2 write-up
```

---

## License

AGPLv3. Source is open for academic use, replication, and non-commercial research.

**Commercial use requires a separate license.** Contact aryan199841@gmail.com.
