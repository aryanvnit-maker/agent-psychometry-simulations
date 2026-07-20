# FLF Epistemic Case Study Competition — Submission

A pipeline that turns a contested question into a typed, versioned,
adversarially-tested knowledge artifact (an `EpistemicMap`), plus a
deterministic, no-LLM way to audit that artifact. Demonstrated on all three
FLF-named cases (COVID origins, LHC black holes, eggs/CVD). Central result: under
a planted false premise, chain topology resists conformity where the
framework-default round-table conforms — replicated across two model families
(chain 28/30 vs flat 15/30, p<0.001) — and chain resistance is re-grounded on
deterministic checks, not an LLM judge.

> **Licensing:** this submission (the files listed in
> [SUBMISSION_MANIFEST.md](SUBMISSION_MANIFEST.md)) is open — **MIT** for code,
> **CC-BY-4.0** for docs and result data. It is free to use, run, reproduce, and
> publish. It runs *on top of* the Kalibr engine, which is **proprietary** and
> separately licensed (see [README-KALIBR.md](README-KALIBR.md) and
> [LICENSE](LICENSE)); the engine may be run only to reproduce this submission.

## Contents

| To… | Go to |
|---|---|
| Read the submission | **[docs/flf-submission-concise.md](docs/flf-submission-concise.md)** (start here) |
| Read the full method, appendices, and proposed benchmark | [docs/flf-submission.md](docs/flf-submission.md) |
| Verify the core claim in 30s (no API key) | [Replicate — no API key](#replicate-the-core-claim-in-30-seconds--no-api-key-required) below |
| Reproduce every run from scratch | [Reproduce the runs](#reproduce-the-runs-from-scratch--needs-an-api-key) below |
| Inspect the artifacts | `results/epistemic_maps/` (maps) and `results/transcripts/` (raw runs), keyed by `run_id` |
| See the underlying research program | [README-KALIBR.md](README-KALIBR.md) |

## Replicate the core claim in 30 seconds — no API key required

The headline de-circularization can be verified against the committed artifacts
with zero setup or cost. This runs the no-LLM checks over the committed
`EpistemicMap`s and prints the numbers cited in the submission:

```bash
pip install -r requirements.txt
python phases/phase_e/deterministic_audit.py
```

Expected output: calibrated-confidence audit (71/73 chain ranges kept ≥15pt of
uncertainty under poisons that demanded high confidence), field-scoped
poison-marker audit (2/27 conform), and the dependency-flagging check with its
disclosed 65–100% definitional sensitivity. Committed maps are in
`results/epistemic_maps/`; raw transcripts (the mechanism) in
`results/transcripts/`, keyed by the `run_id`s cited in the submission.

To audit the held-out portability case (alcohol J-curve): `python
phases/phase_e/deterministic_audit.py --case e05p2`.

## Reproduce the runs from scratch — needs an API key

```bash
cp .env.example .env    # set GEMINI_API_KEY and JUDGE_MODEL=<a currently-available model>
                        # (or MODEL_PROVIDER=anthropic + ANTHROPIC_API_KEY for the Claude replication)

# The adversarial epistemic poison test (chain vs flat, 3 poison variants):
python phases/phase_e/run_phase_e.py --scenarios e02p1_eggs_poison_consensus e02p2_eggs_poison_fallacy e02p3_eggs_poison_source --conditions kalibr-chain flat-no-handoff --reps 5
python phases/phase_e/summarize.py --scenario e02p2_eggs_poison_fallacy

# A clean EpistemicMap on any named case (e01 COVID, e03 LHC, e02 eggs):
python phases/phase_e/run_phase_e.py --scenarios e03_lhc_black_holes --conditions kalibr-chain --reps 1
```

Note: `run_phase_e.py`'s LLM judge reads `JUDGE_MODEL`; set it to a model your
key can access. Results append to `results/phase_e.jsonl`; each record carries
its `model`, `run_id`, and `map_parsed` status.

## Applying this to a new case

The engine is case-agnostic — a "scenario" is a brief + a scoring rubric. Four
steps, no engine changes:

1. **Add a scenario** in `src/scenarios/epistemic.py`, following the existing
   pattern (for an adversarial test, add a poisoned variant that injects one
   confident falsehood, as the three eggs/CVD poisons do).
2. **(Optional) Run ingestion** (`phases/phase_e/ingest.py`) on the raw sources,
   or hand-curate the brief.
3. **Run both topologies:** `python phases/phase_e/run_phase_e.py --scenarios
   <your_scenario> --conditions kalibr-chain flat-no-handoff --reps 5`.
4. **Audit deterministically:** `python phases/phase_e/deterministic_audit.py
   --case <prefix>` — no LLM in the scoring path.

The same four steps produced every number in this submission. A worked held-out
example (alcohol J-curve, `e05p2_alcohol_poison_fallacy`) ships in the repo.

---

*Independent research. Contact: aryan199841@gmail.com*
