# Kalibr-v2: Agent Psychometry Simulations

Empirical research measuring where human team psychology transfers to AI agent teams — and where it breaks. Five experiments, 1,429 evaluations, fully deterministic.

The short version: the industry default (flat roundtables, occupational personas, single static architecture) produces a distinct, measurable failure mode in every domain tested. The correct architecture is simpler than what everyone is building.

Full write-up: [`docs/lesswrong-post-combined.md`](docs/lesswrong-post-combined.md)

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

**Phase 1 — Topology experiment**
```bash
python run_all.py                    # chain topology (default)
python run_all.py --topology flat    # flat topology
python analyze.py                    # analysis and charts
```

**Phase 2 — Constitution experiment**
```bash
python run_cp_baseline.py            # chain-1 baseline (12%)
python run_cp_experiment.py          # 9 conditions
python run_algorithmist_control.py   # ALGORITHMIST control
python analyze_cp.py                 # analysis and charts
```

**Phase 3 — Hallucination multiplier**
```bash
python generate_phase3_hints.py --n 50   # generate wrong hints
python run_phase3.py                      # 4 conditions × 50 problems
python analyze_phase3.py                  # analysis and charts
```

**Phase 4 — Meta-orchestrator**
```bash
python generate_trojan_tasks.py           # adversarial classifier tests
python run_meta_orchestrator.py           # 3 conditions × 37 tasks
python analyze_meta_orchestrator.py       # analysis and charts
```

---

## Repository Structure

```
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
├── run_*.py              # Phase runners
├── analyze_*.py          # Phase analysis scripts
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
