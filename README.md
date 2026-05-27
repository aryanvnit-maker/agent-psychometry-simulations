# Kalibr-v2: Agent Psychometry Simulations

Empirical research measuring where human team psychology transfers to AI agent teams — and where it breaks. Five experiments, 1,429 evaluations, fully deterministic.

The short version: the industry default (flat roundtables, occupational personas, single static architecture) produces a distinct, measurable failure mode in every domain tested. The correct architecture is simpler than what everyone is building.

Full write-up: [`docs/lesswrong-post-combined.md`](docs/lesswrong-post-combined.md)

---

## What This Means for Practitioners

**1. Stop defaulting to flat topology.**
Flat round-table swarms are the industry default. The data shows they actively destroy output quality on bounded tasks — adding a second agent to a flat swarm caused a 46-point performance crash. An 8-agent flat swarm was beaten by a 2-agent chain by 38 points. Social cohesion is high; task cohesion collapses. If you need a committed deliverable — a decision, a document, a code review — use a sequential chain of two agents. The change requires no new models, only restructuring the prompt pipeline.

**2. Strip occupational identities from execution agents.**
Instructing an agent to "design the algorithm, do not write code" costs 4pp pass@1 and raises compilation errors on hard coding tasks. The control experiment isolated the cause: the role instruction itself creates a mandatory prose→code translation step that the downstream agent cannot complete cleanly. The agent follows the instruction correctly — the instruction is the problem. For code, math, or structured output, a generic chain-2 with no occupational identity outperforms every specialized configuration tested.

**3. Flat topology is a safety risk under adversarial input, not just a performance one.**
When wrong premises are introduced, flat agents validate each other's acceptance of the error rather than challenging it. Phase 3 showed flat-2 under poisoned input produced four complete task collapses — no output at all — versus zero collapses in chain-2 across 100 poisoned runs. Any multi-agent system processing user-submitted data, ambiguous prompts, or adversarial input must not use flat topology. Chain topology's committed first-pass provides structural resistance; flat topology has none.

**4. One config cannot handle mixed workloads.**
A pipeline tuned for judgment tasks produces 0% pass@1 on coding (20 NoCode — the constitution blocks code output). A pipeline tuned for execution loses 26 points on judgment. A lightweight classifier routing between two configs recovers per-domain maximum on both axes simultaneously with 100% accuracy. The fix is a five-line classifier. The cost of not having it is collapse on half your workload.

**5. Reserve psychometric profiling for open-world strategic tasks only.**
Kalibr behavioral profiles produce a 78-point gap on resource allocation tasks. They are neutral on closed-world deterministic tasks and overridden entirely by formatting constraints on execution tasks. Don't invest in elaborate agent personalities for agents that output code blocks or factual answers. Profile only where the output space is unconstrained and the task requires judgment over an ambiguous problem.

**6. Question every piece of human team scaffolding in your pipeline.**
Roundtables exist because humans need buy-in before committing. Job titles exist because human accountability requires identity. Deliberation frameworks exist because power dynamics suppress minority positions. Agents have none of those constraints. Every human organisational construct imported into a multi-agent system adds coordination overhead without the benefit it was designed to provide. Remove it.

---

## Results

### Phase 1 — Topology (118 simulations, 0–100 rubric score)

| Team Size | Chain | Flat | Δ |
|---|---|---|---|
| 1 agent | 15.3 | 31.2 | +15.9 |
| **2 agents** | **57.6** | **10.7** | **−46.9** |
| 4 agents | 50.4 | 35.5 | −14.9 |
| 8 agents | 40.4 | 19.1 | −21.3 |

Chain-2 beats flat-8 by 38 points. Cross-model replicated on Gemini 2.5 Flash and Claude 3.5 Sonnet.

### Phase 2 — Constitution (900 evaluations, Codeforces Div. 1 C/D, pass@1)

| Condition | Pass@1 | Compilation Errors |
|---|---|---|
| **Chain-2 generic** | **16%** | 22 |
| Chain-2 specialized (ALGORITHMIST → IMPLEMENTER) | 13% | 23 |
| Chain-1 generic (baseline) | 12% | 18 |

### Phase 2 Control — ALGORITHMIST isolation (100 evaluations)

| Condition | Pass@1 |
|---|---|
| Chain-2 generic | 16% |
| Chain-2 specialized (extreme dims) | 13% |
| **Chain-2 ALGORITHMIST-balanced (control)** | **12%** |

Role instruction is the culprit, not dimension profiles. Confound resolved.

### Phase 3 — Robustness (200 evaluations, adversarial hint injection)

| Condition | Pass@1 | NoCode |
|---|---|---|
| chain-2/clean | 14% | 0 |
| chain-2/poisoned | 18% | 0 |
| flat-2/clean | 18% | 0 |
| **flat-2/poisoned** | **14%** | **4** |

8pp swing between poisoned conditions. Flat topology collapsed entirely 4 times under adversarial input. Chain never collapsed once.

### Phase 4 — Routing (111 evaluations, mixed workload)

| Config | Judgment score | Execution pass@1 |
|---|---|---|
| static-judgment (global) | 85.1 | 0% — 20 NoCode |
| static-execution (global) | 59.6 | 20% |
| **meta-router** | **85.8** | **20%** |

Classifier accuracy: 100% on 37 real tasks + 10 adversarial Trojan tasks.

---

## Setup

```bash
git clone <repo>
cd agent-psychometry-simulations
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add GEMINI_API_KEY and DATABASE_URL to .env
```

Judge0 (required for Phase 2, 3, 4 execution evaluation):
```bash
cd judge0 && docker-compose up -d && cd ..
```

---

## Reproducing the Core Finding

No database required. Runs Phase 1 scenario with chain vs flat comparison:

```bash
python reproduce.py
```

---

## Running Each Phase

All commands run from the repo root.

**Phase 1 — Topology experiment**
```bash
python phases/phase1/run_all.py                    # chain topology (default)
python phases/phase1/run_all.py --topology flat    # flat topology
python phases/phase1/analyze.py                    # analysis and charts
```

**Phase 2 — Constitution experiment**
```bash
python phases/phase2/run_cp_baseline.py            # chain-1 baseline (12%)
python phases/phase2/run_cp_experiment.py          # 9 conditions
python phases/phase2/run_algorithmist_control.py   # ALGORITHMIST control
python phases/phase2/analyze_cp.py                 # analysis and charts
```

**Phase 3 — Hallucination multiplier**
```bash
python phases/phase3/generate_phase3_hints.py --n 50   # generate wrong hints
python phases/phase3/run_phase3.py                      # 4 conditions × 50 problems
python phases/phase3/analyze_phase3.py                  # analysis and charts
```

**Phase 4 — Meta-orchestrator**
```bash
python phases/phase4/generate_trojan_tasks.py           # adversarial classifier tests
python phases/phase4/run_meta_orchestrator.py           # 3 conditions × 37 tasks
python phases/phase4/analyze_meta_orchestrator.py       # analysis and charts
```

---

## Repository Structure

```
├── phases/
│   ├── phase1/           # Topology experiment (run_all, analyze)
│   ├── phase2/           # Constitution experiment (run_cp_*, analyze_cp)
│   ├── phase3/           # Hallucination multiplier (hints, run, analyze)
│   └── phase4/           # Meta-orchestrator (trojans, run, analyze)
├── src/
│   ├── agents/           # Kalibr profiles, constitutions, agent pool
│   ├── datasets/         # CodeContests loader
│   ├── evaluation/       # Judge panel, scoring rubrics
│   ├── execution/        # Judge0 code execution, code extractor
│   ├── meta_orchestrator/# Classifier and router (Phase 4)
│   ├── orchestration/    # Simulation engine
│   ├── scenarios/        # Phase 1 judgment scenario library
│   └── telemetry/        # Supabase persistence
├── results/              # Raw JSONL results (all phases)
├── reports/              # Generated charts
├── docs/                 # Write-ups and posts
├── scripts/              # Admin and debug utilities
├── judge0/               # Judge0 Docker configuration
└── reproduce.py          # Quick reproduction of core finding
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Gemini API key |
| `ANTHROPIC_API_KEY` | Phase 1 cross-model only | Claude API key |
| `DATABASE_URL` | Optional | Supabase connection string (Phase 1+2 persistence) |
| `MODEL` | No | Override model (default: gemini-2.5-flash) |
| `MODEL_PROVIDER` | No | `gemini` or `anthropic` (default: gemini) |

---

## License

Free for research and non-commercial use under [AGPL-3.0](LICENSE).
Commercial use requires a paid license — see [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) or contact aryan199841@gmail.com.

---

*Independent research. No institutional funding or affiliation.*

— Aryan S.
