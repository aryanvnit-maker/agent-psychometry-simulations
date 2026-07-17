# FLF Epistemic Case Study Competition — Submission

**Submission documents:**
- **[docs/flf-submission-concise.md](docs/flf-submission-concise.md)** — the primary entry (~1,800 words).
- [docs/flf-submission.md](docs/flf-submission.md) — full method history, appendices, and the proposed benchmark spec.

**What this is:** a pipeline that turns a contested question into a typed, versioned, adversarially-tested knowledge artifact (an `EpistemicMap`), plus a deterministic, no-LLM way to audit that artifact. Demonstrated on all three FLF-named cases (COVID origins, LHC black holes, eggs/CVD). Central result: under a planted false premise, chain topology resists conformity where the framework-default round-table conforms — replicated across two model families (chain 28/30 vs flat 15/30, p<0.001) — and chain resistance is re-grounded on deterministic checks, not an LLM judge.

## Replicate the core claim in ~30 seconds — no API key required

The headline de-circularization can be verified against the committed artifacts with zero setup or cost. This runs three no-LLM checks over the 35 committed `EpistemicMap`s and prints the numbers cited in the submission:

```bash
pip install -r requirements.txt
python phases/phase_e/deterministic_audit.py
```

Expected output: calibrated-confidence audit (71/73 chain ranges kept ≥15pt of uncertainty under poisons that demanded high confidence), field-scoped poison-marker audit (2/27 conform), and the dependency-flagging check with its disclosed 65–100% definitional sensitivity. Committed maps are in `results/epistemic_maps/`; raw transcripts (the mechanism) in `results/transcripts/`, keyed by the `run_id`s cited in the submission.

## Reproduce the runs from scratch — needs an API key

```bash
cp .env.example .env    # set GEMINI_API_KEY and JUDGE_MODEL=<a currently-available model>
                        # (or MODEL_PROVIDER=anthropic + ANTHROPIC_API_KEY for the Claude replication)

# The adversarial epistemic poison test (chain vs flat, 3 poison variants):
python phases/phase_e/run_phase_e.py --scenarios e02p1_eggs_poison_consensus e02p2_eggs_poison_fallacy e02p3_eggs_poison_source --conditions kalibr-chain flat-no-handoff --reps 5
python phases/phase_e/summarize.py --scenario e02p2_eggs_poison_fallacy

# A clean EpistemicMap on any named case (e01 COVID, e03 LHC, e02 eggs):
python phases/phase_e/run_phase_e.py --scenarios e03_lhc_black_holes --conditions kalibr-chain --reps 1

# The completed deterministic code-domain pilot (Phase 3, no LLM judge; needs Judge0 via docker):
python phases/phase3/run_phase3.py && python phases/phase3/analyze_phase3.py
```

Note: `run_phase_e.py`'s LLM judge reads `JUDGE_MODEL`; set it to a model your key can access. Results append to `results/phase_e.jsonl`; each record carries its `model`, `run_id`, and `map_parsed` status.

---

# Kalibr

*(The submission above was built on the research program documented below. The Kalibr multi-agent findings are the origin of the topology/conformity result the submission extends into the epistemic domain.)*

**Kalibr is the synthesis layer for multi-agent AI systems.**

Most multi-agent pipelines silently fail not because of the wrong framework, wrong topology, or too few agents — but because no agent is ever forced to commit to a final answer. Kalibr fixes this with one corrective prompt at the terminal step.

Nine experiments. 2,400+ evaluations. Temperature=0.0 throughout.

→ **[Full research write-up](docs/lesswrong-post-combined.md)**

---

## The Finding

The out-of-the-box flat roundtable — the default in most framework quickstarts when no terminal synthesis step is added — scores **34.3/100** on structured judgment tasks. Agents address each other constantly while nobody commits to a deliverable.

Adding more agents doesn't help. Adding a different model doesn't help. Adding a synthesis prompt at the terminal step takes it from 34.3 → 76.5 (+42 pts). The synthesis step accounts for **38.8 pts** of the gap. Topology accounts for 16.6 pts. Agent count or diversity: **0.7 pts (p=0.854, not significant)**.

Phase 9: Kalibr's 2-call chain matched xAI's internal 4-agent panel (79.8 vs 81.5, Δ=-1.8, p=0.809) at half the compute. Score-per-LLM-call: Kalibr 39.9, Grok panel 20.4.

---

## SDK

> **Status: research preview. Works reliably on judgment and execution tasks. Known gaps below.**

```bash
pip install git+https://github.com/aryanvnit-maker/agent-psychometry-simulations
```

```python
from kalibr import chain, route

# 2-agent synthesis chain — optimal for judgment tasks
result = chain(task="Should we pivot to enterprise or stay SMB?")
print(result.output)

# Auto-route: classifies task and picks the right config
result = route(task="Implement a binary search in Python.")
print(result.output)

# With judge-panel scoring (+3 LLM calls)
result = chain(task="Evaluate this acquisition offer.", score=True)
print(result.score)   # 0–100
```

Configure via `.env`:
```
GEMINI_API_KEY=...        # required (judge always uses Gemini)
MODEL=gemini-2.5-flash    # worker model
MODEL_PROVIDER=gemini     # gemini | anthropic | xai
```

### Known limitations

- **Reflective tasks underperform.** Post-mortems, retrospectives, and audits get the decisiveness synthesis prompt ("close every open question, be decisive"), which is the wrong posture for backward-looking analysis. Phase 9: Kalibr scored 66.7 vs panel's 80.0 on a post-mortem scenario (-13.3 pts). Fix pending (reflection domain classifier + separate handoff prompt).
- **chain() is hardcoded to 2 agents.** The synthesis prompt fires at position [1]. For chains longer than 2, the synthesis step lands in the middle, not at the terminal agent.
- **Classifier always calls Gemini** regardless of `MODEL_PROVIDER`. One Gemini Flash call per `route()` invocation even if your worker is xAI or Anthropic.
- **Reasoning models require higher token budget.** Set `AGENT_TOKEN_BUDGET=8000` or higher in `.env` when using reasoning-class models (`grok-*-reasoning`, `gemini-2.5-*`). The default (4000) is sufficient for standard models but reasoning models consume most of their budget on internal chain-of-thought before generating visible output.
- **Tasks over 1,500 chars may be misclassified.** The classifier truncates input at 1,500 characters.
- **Not tested on creative tasks** (story generation, open-ended brainstorming). The judgment/execution binary may misclassify these.

---

## Evidence

### Core mechanism (Phase 5 — 160 runs, 2×2 factorial)

| Condition | LLM calls | Score |
|---|---|---|
| flat / no synthesis (out-of-the-box default) | 4 | 34.3 |
| chain / no synthesis | 2 | 50.9 |
| flat / with synthesis | 5 | 76.5 |
| **chain / with synthesis** | **2** | **86.3** |
| single-agent-refine (Phase 8) | 2 | 85.7 |

Synthesis step: **+38.8 pts**. Topology: **+16.6 pts**. Agent diversity: **+0.7 pts (p=0.854, n.s.)**.

A single agent running draft → synthesize matches a full multi-agent chain at the same compute.

### vs. xAI's internal panel (Phase 9 — 40 runs, same Grok base model)

| Condition | Calls | Score | Score/call |
|---|---|---|---|
| kalibr-chain (2 LLM calls) | 2 | 79.8 | **39.9** |
| grok-panel (~4 internal agents) | ~4 | 81.5 | 20.4 |
| **Δ** | | **−1.8, p=0.809** | |

Kalibr matches xAI's proprietary 4-agent system at 2 calls. Nearly 2× more score-efficient per LLM call.

---

## All Results

### Phase 1 — Topology (118 simulations)

| Team size | Chain | Flat | Δ |
|---|---|---|---|
| 1 agent | 15.3 | 31.2 | +15.9 |
| **2 agents** | **57.6** | **10.7** | **−46.9** |
| 4 agents | 50.4 | 35.5 | −14.9 |
| 8 agents | 40.4 | 19.1 | −21.3 |

Chain-2 beats flat-8 by 38 pts. Replicated on Gemini 2.5 Flash and Claude 3.5 Sonnet.
*Note: Phase 5 showed the full gap includes a synthesis confound. True topology-only gap: ~10–17 pts.*

### Phase 2 — Role personas (900 evaluations, Codeforces Div. 1 C/D, pass@1)

| Condition | Pass@1 | Compilation errors |
|---|---|---|
| **Chain-2 generic** | **16%** | 22 |
| Chain-2 specialized (ALGORITHMIST → IMPLEMENTER) | 13% | 23 |
| Chain-1 baseline | 12% | 18 |

Occupational role labels cost 4pp pass@1 (25% relative) on execution tasks. No personas.

### Phase 3 — Adversarial robustness (200 evaluations, poisoned hint injection)

| Condition | Pass@1 | Complete collapses |
|---|---|---|
| chain-2 / clean | 14% | 0 |
| chain-2 / poisoned | 18% | 0 |
| flat-2 / clean | 18% | 0 |
| **flat-2 / poisoned** | **14%** | **4** |

Flat locked in poisoned answers and produced zero output 4 times. Chain: zero collapses across 100 poisoned runs.

### Phase 4 — Task router (111 evaluations, mixed workload)

| Config | Judgment score | Execution pass@1 |
|---|---|---|
| static-judgment (global) | 85.1 | 0% (20 NoCode) |
| static-execution (global) | 59.6 | 20% |
| **meta-router** | **85.8** | **20%** |

Classifier accuracy: 100% on 37 real + 10 adversarial tasks.

### Phase B — Code review replication (N=15/condition)

| Topology | Mean score |
|---|---|
| chain-2 | 70.4 |
| flat-2 (no synthesis) | 35.3 |
| **Δ** | **+35.1** |

Topology direction replicates outside business judgment domain.

### Phase 5 — Synthesis isolation (160 runs, 2×2 factorial)

| Condition | Mean score |
|---|---|
| **chain / handoff** | **86.3** |
| flat / handoff | 76.5 |
| chain / no-handoff | 50.9 |
| flat / no-handoff | 34.3 |

Handoff effect: **+38.8 pts**. Topology (no handoff): **+16.6 pts**.

### Phase 6 — Objective benchmarks (749 evaluations, no LLM judge)

| Condition | Calls | HumanEval | 95% CI | GSM8K | 95% CI |
|---|---|---|---|---|---|
| single-agent | 1 | 94.0% | [83.8–97.9%] | 85.0% | [76.7–90.7%] |
| single-agent-refine | 2 | 98.0% | [89.5–99.6%] | 92.0% | [85.0–95.9%] |
| kalibr-chain | 2 | 96.0% | [86.5–98.9%] | 94.0% | [87.5–97.2%] |
| kalibr-flat-handoff | 5 | 98.0% | [89.5–99.6%] | 92.0% | [85.0–95.9%] |
| **kalibr-flat-no-handoff** | **4** | **28.0%** | **[17.5–41.7%]** | **56.6%** | **[46.7–65.9%]** |

All working conditions near ceiling (CIs overlap — differences not meaningful). The flat/no-handoff collapse (28% HumanEval, 57% GSM8K) is the result.

### Phase 8 — Agent diversity vs self-refinement (79 runs, compute-matched)

| Condition | Calls | N | Mean | p |
|---|---|---|---|---|
| kalibr-chain (2 agents) | 2 | 39 | 86.5 | — |
| single-agent-refine (1 agent) | 2 | 40 | 85.7 | — |
| **Δ** | | | **+0.7** | **0.854** |

Agent diversity adds zero measurable value over structured self-refinement.

### Phase 9 — Kalibr vs xAI Grok panel (40 runs, same Grok base model)

| Condition | Model | Calls | N | Mean | Std |
|---|---|---|---|---|---|
| kalibr-chain | grok-4.20-0309-reasoning | 2 | 20 | 79.8 | 29.3 |
| grok-panel | grok-4.20-multi-agent-0309 | ~4 | 20 | 81.5 | 12.8 |
| **Δ** | | | | **−1.8, p=0.809** | |

Not compute-matched (Kalibr: 2 LLM calls, panel: ~4 internal agents). Score-per-call: Kalibr 39.9 vs panel 20.4.

Per-scenario: Kalibr wins on decision/strategy tasks (+5 pts); panel leads on post-mortem (-13.3 pts — decisiveness posture is wrong for reflective tasks).

---

## Epistemic Investigation (Phase E)

Phase E is a separate research track applying the chain topology and synthesis architecture to genuinely contested epistemic questions (COVID origins, eggs/CVD, nuclear risk, alcohol J-curve). It is not part of the Kalibr SDK; it is the basis of the FLF Epistemic Case Study Competition submission.

The architecture runs a 4-step human-AI loop:

1. `ingest.py` — URL or file to structured claims JSON with provenance (author, expressed confidence, verbatim quote)
2. Human curates the scenario brief from the extracted claims
3. Chain topology + epistemic synthesis prompt produces a typed EpistemicMap (cruxes, evidence-quality ratings, correlated-evidence pairs, calibrated probability ranges, settled-vs-performed split)
4. `compound_demo.py` — human injects new evidence; system produces a v2 map and prints a v1→v2 diff

The synthesis prompt is deliberately anti-decisive: it forces calibrated ranges and correlated-evidence checks rather than verdicts. This is the opposite posture from the Kalibr synthesis prompt, which is why Phase 9's decisive prompt cost -13.3 pts on reflective tasks.

Full write-up: [docs/flf-submission.md](docs/flf-submission.md)

---

## Quick Start

```bash
git clone https://github.com/aryanvnit-maker/agent-psychometry-simulations
cd agent-psychometry-simulations
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — add at minimum GEMINI_API_KEY
```

Reproduce the core finding (chain vs flat, live output):
```bash
python reproduce.py
```

---

## Running Each Phase

All commands from repo root. Phases 1–4 require Judge0 for execution evaluation (see below). Phases 5, 8, 9 run on any machine with API keys.

**Phase 1 — Topology**
```bash
python phases/phase1/run_all.py
python phases/phase1/run_all.py --topology flat
python phases/phase1/analyze.py
```

**Phase 2 — Role personas**
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

**Phase 5 — Synthesis isolation (mechanism)**
```bash
python phases/phase5/run_handoff_factorial.py
python phases/phase5/analyze_handoff_factorial.py
```

**Phase 6 — Objective benchmarks (HumanEval + GSM8K)**
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

**Phase 9 — Kalibr vs Grok multi-agent panel**

Requires xAI API key. Set in `.env`:
```
XAI_API_KEY=your_key_here
MODEL=grok-4.20-0309-reasoning
MODEL_PROVIDER=xai
GROK_PANEL_MODEL=grok-4.20-multi-agent-0309
AGENT_TOKEN_BUDGET=8000
```
```bash
# Verify connections before running
python phases/phase9/test_connections.py

# Full run (5 reps × 4 scenarios × 2 conditions = 40 runs)
python phases/phase9/run_phase9.py --reps 5

# Kalibr-chain only (skip panel — if panel model unavailable)
python phases/phase9/run_phase9.py --reps 5 --skip-panel

python phases/phase9/analyze_phase9.py
```

**Phase E — Epistemic investigation (FLF track)**
```bash
python phases/phase_e/ingest.py --url <article_url>   # Step 1: source → structured claims
python phases/phase_e/run_phase_e.py                   # Step 3: brief → v1 EpistemicMap
python phases/phase_e/compound_demo.py                 # Step 4: new evidence → v2 map + diff
python phases/phase_e/analyze_phase_e.py               # Analysis across conditions
```

**All phases — unified summary**
```bash
python phases/summarize_all.py
```

**Judge0 (required for Phases 1–4, execution evaluation)**
```bash
cd judge0 && docker-compose up -d && cd ..
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Judge always uses Gemini; required even for non-Gemini worker runs |
| `ANTHROPIC_API_KEY` | Phase 1 cross-model only | Claude API key |
| `XAI_API_KEY` | Phase 9 only | xAI API key for Grok |
| `DATABASE_URL` | Optional | Supabase connection string (Phase 1+2 telemetry) |
| `MODEL` | No | Worker model (default: `gemini-2.5-flash`) |
| `MODEL_PROVIDER` | No | `gemini` \| `anthropic` \| `xai` (default: `gemini`) |
| `GROK_PANEL_MODEL` | Phase 9 | Panel model name (default: `grok-4.20-multi-agent-0309`) |
| `JUDGE_MODEL` | No | Override judge model (default: `gemini-2.5-flash`) |
| `AGENT_TOKEN_BUDGET` | No | Max output tokens per agent call (default: `4000`; use `8000+` for reasoning models) |

---

## Repository Structure

```
├── kalibr/               # SDK (chain, route, KalibrResult)
├── phases/
│   ├── phase1/           # Topology experiment
│   ├── phase2/           # Role personas (code)
│   ├── phase3/           # Adversarial robustness
│   ├── phase4/           # Meta-router
│   ├── phase_b/          # Code review replication
│   ├── phase5/           # Synthesis isolation (2×2 factorial)
│   ├── phase6/           # Objective benchmarks (HumanEval, GSM8K)
│   ├── phase8/           # Agent diversity vs self-refinement
│   ├── phase9/           # Kalibr vs Grok multi-agent panel
│   ├── phase_e/          # Epistemic investigation (FLF track)
│   └── summarize_all.py
├── src/
│   ├── agents/           # Kalibr profiles, constitutions, pool
│   ├── evaluation/       # Judge panel, scoring, EpistemicMap schema
│   ├── execution/        # Judge0 code execution
│   ├── meta_orchestrator/# Classifier and router
│   ├── orchestration/    # Simulation engine (chain + flat)
│   ├── scenarios/        # Judgment scenario library
│   └── telemetry/        # Supabase persistence
├── results/              # Raw JSONL results
├── docs/
│   ├── lesswrong-post-combined.md
│   ├── hn-post-combined.md
│   ├── simulation-methodology.md
│   └── flf-submission.md          # FLF Epistemic Case Study submission
├── judge0/               # Judge0 Docker config
└── reproduce.py
```

---

## Audits

Running a multi-agent pipeline? Without the synthesis step, Phase 6 shows these systems perform at 28–57% while appearing to work. Confidential back-test audits available — contact aryan199841@gmail.com.

---

## License

Free for research and non-commercial use under [AGPL-3.0](LICENSE).
Commercial use requires a paid license — contact aryan199841@gmail.com.

---

*Independent research. No institutional funding.*

— Aryan S.
