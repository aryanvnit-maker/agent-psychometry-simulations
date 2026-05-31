# Kalibr

**Kalibr is the synthesis layer for multi-agent AI systems.**

Most multi-agent pipelines silently fail — not because of the wrong framework, the wrong topology, or too few agents, but because no agent is ever forced to commit to a final answer. Kalibr fixes this with a corrective architecture that sits on top of any existing LangChain, CrewAI, or AutoGen pipeline.

Nine experiments. 2,400+ evaluations. Temperature=0.0 throughout. The root cause of multi-agent failure is one missing prompt.

→ **[Full research write-up](docs/lesswrong-post-combined.md)** · **[kalibriq.com](https://kalibriq.com)**

---

## The Problem

The out-of-the-box flat roundtable configuration — the default in most framework Quickstarts — scores **34.3/100** on structured judgment tasks. Agents address each other constantly (social cohesion is high) while nobody commits to a deliverable (task cohesion collapses). Under adversarial input it fails completely: 4 of 100 runs returned no output at all.

Adding more agents doesn't help. Adding a different model doesn't help. The fix is one synthesis prompt at the terminal step.

---

## What Kalibr Does

Kalibr enforces a synthesis architecture on top of whatever you're already running:

1. **Synthesis layer** — a commit-forcing prompt at the terminal step that overrides role constraints, demands gap identification, and requires a definitive final answer. This single change closes 85% of the gap between broken and optimal multi-agent.

2. **Task router** — a five-line classifier that routes between judgment and execution configs. Any single static config collapses on one axis of a mixed workload; the router achieves per-domain maximum on both simultaneously.

3. **Psychometric profiling** — Kalibr dimension profiles that produce a 78-point performance gap on open-world strategic tasks. Neutral on closed-world deterministic tasks; reserve for judgment and resource allocation.

```python
from kalibr import chain, route

# Drop-in synthesis layer on any existing pipeline
result = chain(agents=[agent_a, agent_b], task=your_task)

# Automatic routing for mixed workloads
result = route(task=your_task, judgment_config=j_cfg, execution_config=e_cfg)
```

---

## The Evidence

| Condition | Calls | Score |
|---|---|---|
| Flat/no-handoff (out-of-the-box default) | 4 | 34.3 |
| Chain/no-handoff | 2 | 50.9 |
| Flat/handoff (explicit synthesis) | 5 | 76.5 |
| **Chain/handoff** | **2** | **86.3** |
| **Single-agent-refine** | **2** | **85.7** |

The synthesis step explains **38.8 pts** of the 52-point gap. Topology explains 16.6 pts. Agent count explains 0.7 pts (p=0.854, not significant).

A single agent running draft → synthesize with a commit-forcing prompt matches a full multi-agent chain compute-for-compute.

---

## What This Means for Practitioners

**1. Add a synthesis step before anything else.**
One agent, two calls, synthesis prompt at step 2. This closes 85% of the gap between broken and optimal multi-agent. The prompt must: override role functions, demand identification of gaps in prior analysis, and require a committed final answer. Do this before touching topology or agent count.

**2. Do not add agents to improve quality.**
Phase 8 (compute-matched, 79 runs, p=0.854): two different agents produce statistically identical output to the same agent running twice. Agent diversity adds zero measurable value once the synthesis step is present.

**3. Stop defaulting to flat topology.**
Without a synthesis step, flat roundtable scores 34.3. If you need a deliverable, use a chain of two with a synthesis handoff.

**4. Flat topology is a safety risk under adversarial input.**
Phase 3: flat-2 under poisoned input produced 4 complete task collapses (no output). Chain-2: zero collapses across 100 poisoned runs. Any system processing user-submitted data or ambiguous prompts must not use flat topology.

**5. Strip occupational personas from execution agents.**
"Design the algorithm, do not write code" costs 4pp pass@1 (25% relative) and raises compilation errors. Generic chain-2 with no occupational identity outperforms every specialized configuration tested.

**6. Classify task domain before deploying.**
A five-line classifier routing between two configs achieves per-domain maximum on both judgment and execution simultaneously. Any single static config collapses on one axis of a mixed workload.

**7. Reserve psychometric profiling for open-world strategic tasks only.**
Kalibr profiles produce a 78-point gap on resource allocation. They are neutral on closed-world deterministic tasks and overridden by formatting constraints on execution.

---

## Results Summary

### Phase 1 — Topology (118 simulations, 0–100 rubric score)

| Team Size | Chain | Flat | Δ |
|---|---|---|---|
| 1 agent | 15.3 | 31.2 | +15.9 |
| **2 agents** | **57.6** | **10.7** | **−46.9** |
| 4 agents | 50.4 | 35.5 | −14.9 |
| 8 agents | 40.4 | 19.1 | −21.3 |

Chain-2 beats flat-8 by 38 points. Cross-model replicated on Gemini 2.5 Flash and Claude 3.5 Sonnet. *Note: Phase 5 shows this gap was partially explained by the synthesis confound — the true topology-only gap is ~10–17 pts.*

### Phase 2 — Constitution (900 evaluations, Codeforces Div. 1 C/D, pass@1)

| Condition | Pass@1 | Compilation Errors |
|---|---|---|
| **Chain-2 generic** | **16%** | 22 |
| Chain-2 specialized (ALGORITHMIST → IMPLEMENTER) | 13% | 23 |
| Chain-1 generic (baseline) | 12% | 18 |

Role instruction is the culprit, not dimension profiles.

### Phase 3 — Robustness (200 evaluations, adversarial hint injection)

| Condition | Pass@1 | NoCode |
|---|---|---|
| chain-2/clean | 14% | 0 |
| chain-2/poisoned | 18% | 0 |
| flat-2/clean | 18% | 0 |
| **flat-2/poisoned** | **14%** | **4** |

Flat collapsed entirely 4 times; chain never collapsed once.

### Phase 4 — Routing (111 evaluations, mixed workload)

| Config | Judgment score | Execution pass@1 |
|---|---|---|
| static-judgment (global) | 85.1 | 0% — 20 NoCode |
| static-execution (global) | 59.6 | 20% |
| **meta-router** | **85.8** | **20%** |

Classifier accuracy: 100% on 37 real + 10 adversarial Trojan tasks.

### Phase B — Code Review Replication (N=15 per condition)

| Topology | N | Mean score |
|---|---|---|
| chain-2 | 15 | 70.4 |
| flat-2 (no synthesis step) | 15 | 35.3 |
| **Δ** | | **+35.1** |

Topology direction replicates on code review, outside the business judgment domain.

### Phase 5 — Topology × Handoff Factorial (160 runs, 2×2 design)

| Condition | Mean score |
|---|---|
| **chain/handoff** | **86.3** |
| flat/handoff | 76.5 |
| chain/no-handoff | 50.9 |
| flat/no-handoff | 34.3 |

Handoff effect: **+38.8 pts**. Topology effect (no handoff): **+16.6 pts**. Synthesis dominates by more than 2:1.

### Phase 6 — Objective Benchmarks (749 evaluations, no LLM judge)

**HumanEval pass@1 (N=50/condition) · GSM8K accuracy (N=99–100/condition)**

| Condition | Calls | HumanEval | 95% CI | GSM8K | 95% CI |
|---|---|---|---|---|---|
| single-agent | 1 | 94.0% | [83.8–97.9%] | 85.0% | [76.7–90.7%] |
| single-agent-refine | 2 | 98.0% | [89.5–99.6%] | 92.0% | [85.0–95.9%] |
| kalibr-chain | 2 | 96.0% | [86.5–98.9%] | 94.0% | [87.5–97.2%] |
| kalibr-flat-handoff | 5 | 98.0% | [89.5–99.6%] | 92.0% | [85.0–95.9%] |
| **kalibr-flat-no-handoff** | **4** | **28.0%** | **[17.5–41.7%]** | **56.6%** | **[46.7–65.9%]** |

All working conditions near ceiling — CIs overlap substantially, rankings not meaningful. Primary finding is the flat/no-handoff collapse (28.0% HumanEval), separated from every working condition by 60+ points.

### Phase 8 — Agent Diversity vs Self-Refinement (79 runs, compute-matched)

| Condition | Calls | N | Mean | p |
|---|---|---|---|---|
| kalibr-chain (2 agents) | 2 | 39 | 86.5 | — |
| single-agent-refine (1 agent) | 2 | 40 | 85.7 | — |
| **Δ** | | | **+0.7** | **0.854** |

Not significant. Agent diversity adds zero measurable value over structured self-refinement.

---

## Quick Start

```bash
git clone https://github.com/aryanvnit-maker/agent-psychometry-simulations
cd agent-psychometry-simulations
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add GEMINI_API_KEY (required) and DATABASE_URL (optional, Phase 1+2 only)
```

Reproduce the core finding (chain vs flat, same team, live output):
```bash
python reproduce.py
```

Judge0 (required for Phase 2, 3, 4 execution evaluation):
```bash
cd judge0 && docker-compose up -d && cd ..
```

---

## Running Each Phase

All commands run from the repo root.

**Phase 1 — Topology experiment**
```bash
python phases/phase1/run_all.py                    # chain topology (default)
python phases/phase1/run_all.py --topology flat    # flat topology
python phases/phase1/analyze.py
```

**Phase 2 — Constitution experiment**
```bash
python phases/phase2/run_cp_baseline.py
python phases/phase2/run_cp_experiment.py
python phases/phase2/run_algorithmist_control.py
python phases/phase2/analyze_cp.py
```

**Phase 3 — Adversarial robustness**
```bash
python phases/phase3/generate_phase3_hints.py --n 50
python phases/phase3/run_phase3.py
python phases/phase3/analyze_phase3.py
```

**Phase 4 — Meta-router**
```bash
python phases/phase4/generate_trojan_tasks.py
python phases/phase4/run_meta_orchestrator.py
python phases/phase4/analyze_meta_orchestrator.py
```

**Phase B — Code review replication**
```bash
python phases/phase_b/run_code_review.py
```

**Phase 5 — Topology × Handoff factorial (mechanism isolation)**
```bash
python phases/phase5/run_handoff_factorial.py
python phases/phase5/analyze_handoff_factorial.py
```

**Phase 6 — Objective benchmarks**
```bash
python phases/phase6/run_humaneval.py
python phases/phase6/run_gsm8k.py
python phases/phase6/analyze_phase6.py
```

**Phase 8 — Agent diversity vs self-refinement**
```bash
python phases/phase8/run_phase8.py
python phases/phase8/analyze_phase8.py
```

**Unified summary across all phases**
```bash
python phases/summarize_all.py
```

---

## Repository Structure

```
├── kalibr/               # Kalibr SDK (chain, route, KalibrResult)
├── phases/
│   ├── phase1/           # Topology experiment
│   ├── phase2/           # Constitution experiment (code)
│   ├── phase3/           # Adversarial robustness
│   ├── phase4/           # Meta-router
│   ├── phase_b/          # Code review replication
│   ├── phase5/           # Topology × Handoff factorial
│   ├── phase6/           # Objective benchmarks (HumanEval, GSM8K)
│   ├── phase8/           # Agent diversity vs self-refinement
│   └── summarize_all.py  # Unified results summary
├── src/
│   ├── agents/           # Kalibr profiles, constitutions, agent pool
│   ├── datasets/         # CodeContests loader
│   ├── evaluation/       # Judge panel, scoring rubrics
│   ├── execution/        # Judge0 code execution, code extractor
│   ├── meta_orchestrator/# Classifier and router (Phase 4)
│   ├── orchestration/    # Simulation engine (chain + flat topologies)
│   ├── scenarios/        # Judgment scenario library
│   └── telemetry/        # Supabase persistence (Phase 1+2)
├── results/              # Raw JSONL results (all phases)
├── docs/
│   ├── lesswrong-post-combined.md   # Full research write-up
│   ├── hn-post-combined.md          # HN submission
│   ├── simulation-methodology.md
│   └── archive/                     # Phase 1+2 standalone posts
├── scripts/
│   └── export_supabase.py           # Export Phase 1+2 data from Supabase
├── judge0/               # Judge0 Docker configuration
└── reproduce.py          # Quick reproduction of core finding
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Gemini API key |
| `ANTHROPIC_API_KEY` | Phase 1 cross-model only | Claude API key |
| `DATABASE_URL` | Optional | Supabase connection string (Phase 1+2) |
| `MODEL` | No | Override model (default: gemini-2.5-flash) |
| `MODEL_PROVIDER` | No | `gemini` or `anthropic` (default: gemini) |
| `AGENT_TOKEN_BUDGET` | No | Output token budget per agent (default: 800) |

---

## License

Free for research and non-commercial use under [AGPL-3.0](LICENSE).
Commercial use requires a paid license — see [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) or contact aryan199841@gmail.com.

---

*Independent research. No institutional funding or affiliation.*

— Aryan S. | [kalibriq.com](https://kalibriq.com)
