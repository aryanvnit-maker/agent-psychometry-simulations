# KalibrBench

A controlled benchmark for measuring the effect of communication topology and team composition on AI agent task performance.

---

## What It Measures

KalibrBench isolates **topology** (how agents are connected) and **composition** (which agents are selected) as independent variables against **task performance** as the dependent variable. All other variables are held constant: model temperature, agent pool, scenarios, and evaluation methodology.

The primary finding from the reference dataset (118 runs, Gemini and Anthropic): chain topology outperforms flat topology by 17–22 points on task scores (0–100) across all compositions and both model families. The finding is architectural, not model-specific.

---

## Valid Run Protocol

A submission is valid only if it follows all of these constraints:

1. **Agent pool**: `initialise_pool(seed=42)` — 32 fixed worker agents, 3 fixed judge agents, fully deterministic from seed
2. **Temperature**: `0.0` — same inputs always produce same outputs; stochastic variance is not a valid source of run-to-run differences
3. **Topologies**: `chain` (A→B→C→END, each agent receives prior committed output only) and `flat` (2 rounds, all agents see full conversation history)
4. **Team sizes**: 1, 2, 4, 8 agents
5. **Compositions**: `drafted`, `homogeneous`, `founder_brained`
6. **Scenarios**: all 10 scenarios in `src/scenarios/library.py` (s01–s10)
7. **Judge methodology**: 3 independent judge instances per run; judges evaluate **only the final extracted deliverable** against hard binary rubric criteria — not the full transcript; mean `task_score` (0–100) is the dependent variable
8. **Judge model**: Gemini 2.5 Flash at `temperature=0.0`, regardless of worker model — holds evaluation standard constant across all model comparisons

Deviating from any of these constraints produces results that cannot be compared to the reference dataset.

---

## Scenarios

10 structured scenarios across 6 domains and all 4 Tuckman phases. Full briefs and rubrics in `src/scenarios/library.py`.

| ID | Name | Domain | Phase | Max Turns |
|---|---|---|---|---|
| s01 | Series A Product Fork | Strategic | Forming | 6 |
| s02 | Resource Allocation Under Constraint | Resource | Storming | 8 |
| s03 | Post-Mortem Under Pressure | Evaluation | Storming | 8 |
| s04 | Security Breach Crisis | Crisis | Performing | 5 |
| s05 | System Scaling Decision | Technical | Performing | 5 |
| s06 | Hiring Committee Decision | Evaluation | Storming | 8 |
| s07 | Evidence Synthesis | Research | Norming | 8 |
| s08 | Regulatory Compliance Gap Analysis | Strategic | Forming | 6 |
| s09 | Pricing Strategy Restructure | Resource | Storming | 8 |
| s10 | Acquisition Go/No-Go | Strategic | Performing | 5 |

Each rubric uses binary checkpoints: full points or zero per criterion. No partial credit. This eliminates judge subjectivity on scoring granularity.

---

## Leaderboard

**Metric**: mean task_score (0–100) across all scenarios, team sizes 2/4/8, drafted composition.
Scores on s01–s04 (original 4-scenario set) until 10-scenario runs are complete.

| Model | Provider | Chain | Flat | Gap | N (chain / flat) | Submitted |
|---|---|---|---|---|---|---|
| Gemini 2.5 Flash | Google | 40.3 | 23.4 | −16.9 | 55 / 39 | Aryan V. — 2026-05 |
| Claude 3.5 Sonnet | Anthropic | 42.4 | 20.4 | −21.9 | 12 / 12 | Aryan V. — 2026-05 |

*Submit a PR to add your model. See Submitting Results below.*

---

## Running the Benchmark

```bash
# Reference (Gemini workers, Gemini judges)
python run_cross_model.py --provider gemini

# Anthropic Claude workers (judges remain on Gemini)
python run_cross_model.py --provider anthropic

# DeepSeek V3 workers — add DEEPSEEK_API_KEY to .env
python run_cross_model.py --provider deepseek

# Qwen2.5-72B workers — add DASHSCOPE_API_KEY to .env
python run_cross_model.py --provider qwen
```

Safe to interrupt and restart — completed runs are persisted and skipped automatically.

### Adding a New Provider

Any model with an OpenAI-compatible API can be added to `MODEL_CONFIGS` in `run_cross_model.py`:

```python
"your_model": {
    "MODEL": "your-model-id",
    "MODEL_PROVIDER": "openai_compat",
    "OPENAI_COMPAT_BASE_URL": "https://api.your-provider.com",
    "OPENAI_COMPAT_API_KEY_ENV": "YOUR_API_KEY_ENV_VAR",
},
```

### Minimum Valid Submission

20 runs: all 10 scenarios × 2 topologies × team_size=4, composition=drafted.
This is sufficient to populate the leaderboard with a chain and flat score.

### Full Submission

240 runs: 10 scenarios × 2 topologies × 4 team sizes × 3 compositions.

---

## Submitting Results

1. Run the benchmark using `run_cross_model.py --provider <your-provider>`
2. Ensure judges ran on Gemini 2.5 Flash (default in the runner — do not change this)
3. Run `python analyze.py` and include the output in your PR
4. Open a PR adding one row to the leaderboard table above with: model name, provider, chain score, flat score, gap, N runs, your name and date
5. Include your `cross_model.log` in the PR for verification

---

## Compute Cost Reference

Judges always run on Gemini 2.5 Flash. Worker costs vary by provider.

| Provider | Model | Est. cost per run (chain-4, incl. judges) |
|---|---|---|
| Google | Gemini 2.5 Flash | ~$0.01 |
| Anthropic | Claude 3.5 Sonnet | ~$0.08 |
| DeepSeek | deepseek-chat (V3) | ~$0.01 |
| Qwen | qwen2.5-72b-instruct | ~$0.01 |

Minimum valid submission (20 runs): ~$0.20–$1.60 depending on provider.
Full submission (240 runs): ~$2.40–$19.20 depending on provider.

---

## Schema Note

KalibrBench adds `technical` and `research` to the `scenario_category` column. If running against an existing Supabase instance, apply this migration before running s05–s10:

```sql
ALTER TABLE runs DROP CONSTRAINT IF EXISTS runs_scenario_category_check;
ALTER TABLE runs ADD CONSTRAINT runs_scenario_category_check
  CHECK (scenario_category IN ('strategic', 'crisis', 'resource', 'evaluation', 'creative', 'technical', 'research'));
```

---

## Citation

```
Shah, A. (2026). KalibrBench: A controlled benchmark for AI agent team topology and composition.
GitHub: https://github.com/aryanvnit-maker/agent-psychometry-simulations
```

---

## License

AGPLv3. Open for academic use, replication, and non-commercial research.
Commercial use of the benchmark infrastructure or methodology requires a separate license — contact aryan199841@gmail.com.
