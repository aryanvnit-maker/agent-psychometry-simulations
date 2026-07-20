# Kalibr

> **Licensing:** Kalibr and all research below are **proprietary — all rights
> reserved** (see [LICENSE](LICENSE)). The repository is public for transparency
> and to let the FLF competition reproduce the submission that was built on top of
> it; a narrow license permits running the engine **only** to reproduce that
> submission. Any other use — commercial or not — requires a written license (see
> [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md)). The FLF submission is separate
> and is licensed for **non-commercial use only**: see
> [README-FLF.md](README-FLF.md) and
> [SUBMISSION_MANIFEST.md](SUBMISSION_MANIFEST.md).

The FLF submission was built on this research program. The Kalibr multi-agent
findings are the origin of the topology and conformity results the submission
extends into the epistemic domain.

**Kalibr is the synthesis layer for multi-agent AI systems.**

Most multi-agent pipelines silently fail not because of the wrong framework,
wrong topology, or too few agents — but because no agent is ever forced to commit
to a final answer. Kalibr fixes this with one corrective prompt at the terminal
step.

Nine experiments. 2,400+ evaluations. Temperature=0.0 throughout.

→ **[Full research write-up](docs/lesswrong-post-combined.md)**

---

## The Finding

The out-of-the-box flat roundtable — the default in most framework quickstarts
when no terminal synthesis step is added — scores **34.3/100** on structured
judgment tasks. Agents address each other constantly while nobody commits to a
deliverable.

Adding more agents doesn't help. Adding a different model doesn't help. Adding a
synthesis prompt at the terminal step takes it from 34.3 → 76.5 (+42 pts). The
synthesis step accounts for **38.8 pts** of the gap. Topology accounts for 16.6
pts. Agent count or diversity: **0.7 pts (p=0.854, not significant)**.

Phase 9: Kalibr's 2-call chain matched xAI's internal 4-agent panel (79.8 vs
81.5, Δ=-1.8, p=0.809) at half the compute. Score-per-LLM-call: Kalibr 39.9,
Grok panel 20.4.

---

## SDK

> **Status: research preview.** Use of the engine requires a license (see
> [LICENSE](LICENSE) / [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md)).

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

- **Reflective tasks underperform.** Post-mortems, retrospectives, and audits get
  the decisiveness synthesis prompt ("close every open question, be decisive"),
  which is the wrong posture for backward-looking analysis. Phase 9: Kalibr scored
  66.7 vs panel's 80.0 on a post-mortem scenario (-13.3 pts). Fix pending
  (reflection domain classifier + separate handoff prompt).
- **chain() is hardcoded to 2 agents.** The synthesis prompt fires at position
  [1]. For chains longer than 2, the synthesis step lands in the middle, not at
  the terminal agent.
- **Classifier always calls Gemini** regardless of `MODEL_PROVIDER`. One Gemini
  Flash call per `route()` invocation even if your worker is xAI or Anthropic.
- **Reasoning models require higher token budget.** Set `AGENT_TOKEN_BUDGET=8000`
  or higher in `.env` when using reasoning-class models.
- **Tasks over 1,500 chars may be misclassified.** The classifier truncates input
  at 1,500 characters.
- **Not tested on creative tasks** (story generation, open-ended brainstorming).

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

Synthesis step: **+38.8 pts**. Topology: **+16.6 pts**. Agent diversity: **+0.7
pts (p=0.854, n.s.)**.

A single agent running draft → synthesize matches a full multi-agent chain at the
same compute.

### vs. xAI's internal panel (Phase 9 — 40 runs, same Grok base model)

| Condition | Calls | Score | Score/call |
|---|---|---|---|
| kalibr-chain (2 LLM calls) | 2 | 79.8 | **39.9** |
| grok-panel (~4 internal agents) | ~4 | 81.5 | 20.4 |
| **Δ** | | **−1.8, p=0.809** | |

Kalibr matches xAI's proprietary 4-agent system at 2 calls. Nearly 2× more
score-efficient per LLM call.

---

## All Results

### Phase 1 — Topology (118 simulations)

| Team size | Chain | Flat | Δ |
|---|---|---|---|
| 1 agent | 15.3 | 31.2 | +15.9 |
| **2 agents** | **57.6** | **10.7** | **−46.9** |
| 4 agents | 50.4 | 35.5 | −14.9 |
| 8 agents | 40.4 | 19.1 | −21.3 |

Chain-2 beats flat-8 by 38 pts. Replicated on Gemini 2.5 Flash and Claude 3.5
Sonnet.
*Note: Phase 5 showed the full gap includes a synthesis confound. True
topology-only gap: ~10–17 pts.*

### Phase 3 — Adversarial robustness (200 evaluations, poisoned hint injection)

| Condition | Pass@1 | Complete collapses |
|---|---|---|
| chain-2 / clean | 14% | 0 |
| chain-2 / poisoned | 18% | 0 |
| flat-2 / clean | 18% | 0 |
| **flat-2 / poisoned** | **14%** | **4** |

Flat locked in poisoned answers and produced zero output 4 times. Chain: zero
collapses across 100 poisoned runs. (This is the deterministic backbone the FLF
submission cites.)

### Phase 5 — Synthesis isolation (160 runs, 2×2 factorial)

| Condition | Mean score |
|---|---|
| **chain / handoff** | **86.3** |
| flat / handoff | 76.5 |
| chain / no-handoff | 50.9 |
| flat / no-handoff | 34.3 |

Handoff effect: **+38.8 pts**. Topology (no handoff): **+16.6 pts**.

### Phase 6 — Objective benchmarks (749 evaluations, no LLM judge)

| Condition | Calls | HumanEval | GSM8K |
|---|---|---|---|
| single-agent | 1 | 94.0% | 85.0% |
| single-agent-refine | 2 | 98.0% | 92.0% |
| kalibr-chain | 2 | 96.0% | 94.0% |
| kalibr-flat-handoff | 5 | 98.0% | 92.0% |
| **kalibr-flat-no-handoff** | **4** | **28.0%** | **56.6%** |

The flat/no-handoff collapse (28% HumanEval, 57% GSM8K) is the result.

*(Phases 2, 4, 8, 9, B and full CIs: see the [research write-up](docs/lesswrong-post-combined.md).)*

---

## Epistemic Investigation (Phase E) — the FLF track

Phase E applies the chain topology and synthesis architecture to genuinely
contested epistemic questions. **It is the FLF Epistemic Case Study Competition
submission and is openly licensed — see [README-FLF.md](README-FLF.md).** It is
not part of the proprietary Kalibr SDK.

The architecture runs a 4-step human-AI loop: `ingest.py` (source → structured
claims) → human curates the brief → chain + epistemic synthesis prompt produces a
typed EpistemicMap → `compound_demo.py` (new evidence → v2 map + diff). The
epistemic synthesis prompt is deliberately anti-decisive (calibrated ranges, not
verdicts) — the opposite posture from the Kalibr SDK synthesis prompt.

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

## Running Each Phase

All commands run from repo root. Phases 1–4 require Judge0 for execution
evaluation (`cd judge0 && docker-compose up -d`). Phases 5, 8, 9 run on any
machine with API keys. See the [research write-up](docs/lesswrong-post-combined.md)
for the per-phase command list.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Judge always uses Gemini; required even for non-Gemini worker runs |
| `ANTHROPIC_API_KEY` | Cross-model only | Claude API key |
| `XAI_API_KEY` | Phase 9 only | xAI API key for Grok |
| `MODEL` | No | Worker model (default: `gemini-2.5-flash`) |
| `MODEL_PROVIDER` | No | `gemini` \| `anthropic` \| `xai` (default: `gemini`) |
| `JUDGE_MODEL` | No | Override judge model |
| `AGENT_TOKEN_BUDGET` | No | Max output tokens per agent call (default: `4000`; `8000+` for reasoning models) |

## Repository Structure

```
├── kalibr/               # SDK (chain, route, KalibrResult)          [proprietary]
├── phases/
│   ├── phase1..9, phase_b/   # Kalibr experiments                    [proprietary]
│   └── phase_e/          # Epistemic investigation (FLF submission)  [MIT]
├── src/
│   ├── agents/           # Kalibr profiles, constitutions, pool      [proprietary]
│   ├── evaluation/       # Judge panel, scoring                      [proprietary]
│   │   └── epistemic_schema.py  # EpistemicMap (FLF submission)      [MIT]
│   ├── execution/ meta_orchestrator/ orchestration/ telemetry/      [proprietary]
│   └── scenarios/        # Judgment scenario library                 [proprietary]
│       └── epistemic.py  # Epistemic + poison scenarios (FLF)        [MIT]
├── results/              # Raw JSONL + committed EpistemicMaps
├── docs/                 # Research write-ups + FLF submission docs
├── judge0/               # Judge0 Docker config                      [proprietary]
├── SUBMISSION_MANIFEST.md   # authoritative licensing boundary
├── LICENSE                  # Kalibr proprietary license
├── LICENSE-FLF-CODE         # Non-commercial (FLF code)
└── LICENSE-FLF-DOCS         # CC-BY-NC-4.0 (FLF docs/data)
```

---

## License

**Proprietary — all rights reserved.** See [LICENSE](LICENSE). Use of the Kalibr
engine (anything outside the FLF submission listed in
[SUBMISSION_MANIFEST.md](SUBMISSION_MANIFEST.md)) requires a written license;
contact aryan199841@gmail.com or see [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md).
A narrow license in `LICENSE` permits running the engine solely to reproduce the
FLF submission.

---

*Independent research. No institutional funding.*

— Aryan S.
