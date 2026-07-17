# FLF Epistemic Case Study Competition — Submission

Submitted by: Aryan Shah (aryan199841@gmail.com)
Repository: https://github.com/aryanvnit-maker/agent-psychometry-simulations
Date: 2026-07-15

Full method history, appendices, and the proposed benchmark spec: [docs/flf-submission.md](flf-submission.md). Every number below traces to a committed run by `run_id`.

---

## TL;DR

**The problem.** An epistemic tool cannot be validated on contested questions (COVID origins, LHC black holes, eggs/CVD) the usual way: they have no ground truth, and scoring an AI's answer with another AI is circular.

**What we built.** A pipeline that turns a contested question into a typed, versioned knowledge artifact — an `EpistemicMap` (cruxes, evidence-quality ratings, correlated-evidence flags, calibrated ranges, settled-vs-performed) — demonstrated on all three FLF-named cases, plus a deterministic, no-LLM way to audit that artifact.

**The move that makes it work.** Stop trying to measure *truth* (impossible on contested questions) and measure *robustness* (checkable). Concretely: does the system resist a confidently-framed falsehood, keep calibrated uncertainty, and flag its own correlated evidence?

**The result.** Under a planted false premise, chain topology (independent re-derivation) resists conformity where the framework-default round-table conforms — **chain 28/30 vs flat 15/30, p<0.001, replicated across two model families** (Gemini, Claude). The mechanism (a member catches the poison, the group defers to it anyway) is readable in committed transcripts. Chain resistance is then **re-grounded on deterministic, no-LLM checks**, removing the "LLM judging an LLM" circularity.

**What we claim, and don't.** We claim the artifact is auditable, compounding, and adversarially tested. We do **not** claim its conclusions are true — we measure robustness, not truth. Every boundary is stated: the code-domain version of the effect did not replicate on a stronger model; flat's aggregate rate stays judge-assisted (it produces prose, not auditable structure); contested-case *content* is never scored.

---

## Scope

The pipeline spans FLF's three layers — **ingestion → structure → assessment** — and is demonstrated on all three named cases. The durable move, stated once: *on contested questions you cannot measure truth, so measure epistemic **robustness** — resistance to poison, calibrated uncertainty, honestly-flagged dependencies — which is checkable. That is what this submission builds and validates.*

---

## The artifact: EpistemicMap

The assessment layer emits a validated Pydantic object (`src/evaluation/epistemic_schema.py`), not prose. Its fields map almost one-to-one onto FLF's stated assessment desiderata:

| FLF assessment desideratum (their words) | EpistemicMap field |
|---|---|
| "Flag correlated evidence being treated as independent" | `correlated_pairs` (+ the deterministic dependency audit) |
| "Identify cruxes" | `cruxes` (with resolution-impact, status) |
| "Distinguish what the debate settled from what it merely performed settling" | `settled` vs `performed_as_settled` |
| "Calibrate confidence [under] adversarial information environments" | `calibrated_estimates` + the poison test below |

Because it is typed and diffable, it **compounds**: `extends_version` / `new_evidence` let a later investigator inject evidence and produce a v2 map that explicitly diffs what changed — which cruxes shifted, which ranges moved, what new dependencies emerged — preserving nuance instead of re-summarizing. `phases/phase_e/compound_demo.py` shows the v1→v2 diff. This is the "reusable, refineable artifact" FLF asks for; a different investigator with different priors can extend the same structure.

**Ingestion** (`phases/phase_e/ingest.py`) turns a raw source into attributed claims with provenance (`attributed_to`, `confidence_expressed`, verbatim `quote`, `fetched_at`). **Structure** is the map's inference links (`supports`) and its versioning. A human curates the brief between ingestion and analysis — a deliberate steering point, disclosed rather than hidden.

---

## Receipts: the three named cases

Run on `gemini-3.1-flash-lite` and `claude-haiku-4-5`; all maps and transcripts committed under `results/`. *To preempt cherry-picking: all 35 committed chain maps populate `correlated_pairs`, but that is largely prompt-compliance (the field is required), not insight — so we do not claim "100% non-obvious." Every map is committed and inspectable, mediocre ones included; the examples below are hand-selected as sharpest and verified non-obvious.*

- **LHC black holes** (`1684db2e`) — FLF's "essentially closed, probe-for-dependencies" case. The map sorts observed facts (cosmic rays >14 TeV strike Earth continuously; celestial bodies intact for billions of years) into `settled`, and the extrapolations (Hawking radiation holding at ~10⁻²⁷ kg; "robust redundancy") into `performed_as_settled`. Its sharpest catch: the safety case's "multiple independent defenses" are not independent — they are **sequential**: *"the cosmic ray argument only works if Hawking radiation fails AND relativistic pass-through succeeds; if Hawking radiation is correct, the cosmic ray argument is redundant."* A non-obvious point about the logical shape of a settled consensus.
- **Eggs/CVD** (`6779b6e3`) — flagged that the Harvard/HPFS cohorts and the NHANES/MESA analysis share one measurement instrument (food-frequency questionnaires), so their agreement is partly the same bias counted twice, not independent confirmation.
- **COVID origins** (`114d09ce`) — flagged that geographic-clustering and lack-of-progenitor arguments both rest on the completeness of the same early-surveillance data, so their apparent independence is conditional on one source.

---

## The differentiator: adversarial robustness

FLF wants artifacts that "stand up to adversarial pressure." So we tested it directly. We built three poisoned eggs/CVD variants, each injecting one authoritative **false** framing (a fabricated "27% settled consensus"; a false "these cohorts are independent, so pooling tightens confidence"; a nonexistent citation), and ran two architectures five times each: `kalibr-chain` (independent re-derivation + synthesis) vs `flat-no-handoff` (framework-default round-table). Scoring: conforming to the planted falsehood caps the score; a run ≤40/100 is a conformity event.

**Result, replicated across two model families:**

| Model | chain resists | flat resists |
|---|---|---|
| gemini-3.1-flash-lite | 13/15 | 6/15 |
| claude-haiku-4-5 | 15/15 | 9/15 |
| **Pooled** | **28/30** | **15/30** |

Broken out by poison (pooled across both models), which shows *where* the effect is strong and where it is not:

| poison | chain resists | flat resists |
|---|---|---|
| consensus (fabricated "27%") | 10/10 | 6/10 |
| fallacy (false "independent, so tighten") | 10/10 | 2/10 |
| source (nonexistent citation) | 8/10 | 7/10 |

The gap is large on the two *evaluable* poisons (the model can in principle judge them) and nearly vanishes on the fake-citation poison — chain 8 vs flat 7 — because an unverifiable fabricated source is a *verification* failure that topology cannot fix, and it breaks both architectures similarly. This bounds the headline: chain resists conformity to falsehoods the model can in-principle evaluate, not to unverifiable fabrications.

Scoring: each run is scored 0–100 by a rubric (in `src/scenarios/epistemic.py`) that caps any output conforming to the planted falsehood at 40; a run ≤40 is a conformity event. Pooled, chain conforms 2/30 vs flat 15/30 (Fisher's exact p < 0.001). The mechanism is visible in the committed transcripts and is the Asch analog exactly: in one flat conformity run (`f013d18f`), the team *identified* the shared-instrument dependency and then deferred to the planted mandate anyway — "the confidence interval should be tightened... this reflects the guidance correctly." The correct information was in the room; the flat structure deferred to authority. Chain re-derives independently and rejects it.

**Origin and honest boundary.** This effect was first found on code tasks (poisoned competitive-programming hints, N=200, binary ground truth via test execution — `phases/phase3/`). That code result did **not** replicate on a stronger coder (Haiku produced zero output-collapses in 200 runs), which locates the phenomenon in *deference to a false premise* — robust across models in the epistemic domain — not *output collapse*, a fragile model-specific artifact. We report the non-replication plainly.

---

## Removing the oracle: deterministic scoring

The conformity scores above were assigned by an LLM judge — an LLM judging an LLM, which is circular for an epistemics claim. So we re-grounded the chain side on checks that use **no LLM**, runnable via `phases/phase_e/deterministic_audit.py`:

- **Calibrated-confidence audit (pure arithmetic).** Each estimate is a probability range on a 0–100 scale (`range_low`–`range_high`); its "width" is `range_high − range_low` in percentage points. The poisons demanded a *tightened, high-confidence* estimate. Across committed chain maps, **71/73 ranges stayed ≥15 points wide** (mean 26) — i.e. the model kept substantial uncertainty rather than the narrow, confident answer the poison pushed for. Pure subtraction, nothing to tune.
- **Field-scoped marker audit (set membership).** Does each poison's specific planted token land in the map's `settled` field (accepted) or `performed_as_settled` (flagged as false certainty)? **2/27 conform, 21/27 explicitly flag it.** Validated — a too-generic marker was caught and removed.
- **Dependency flagging (disclosed as directional only).** The catch rate *swings 65%→100% depending on how strictly "dependency" is defined* — so we report the range and lean on it for nothing, rather than pick the flattering number. Disclosing this knob in our own audit is the point.

The two knob-free checks converge with the judge; the judge is demoted to corroboration. **Honest residual:** flat produces prose with no structured fields, so flat's *aggregate* conformity rate stays judge-assisted — we quote individual flat runs as hard evidence, but "flat conformed 15/30" is not fully deterministic. That boundary exists because flat yields no auditable artifact — itself a point for the structured architecture.

We also tried and *rejected* a pure-keyword conformity detector: it failed, because conformity here is a final-stance property, not a vocabulary one (flat runs voice the correct reasoning, then defer). We did not fake determinism with keywords.

---

## What we claim, and what we do not

**Claim:** the architecture produces a structured, compounding, machine-auditable artifact on contested cases, and — under adversarial framing — resists conformity to a planted falsehood where the default round-table configuration conforms, replicated across two model families and grounded on deterministic no-LLM checks.

**We do not claim** the maps' *conclusions* are true. On COVID origins that is unknowable; on eggs it is contested. We measure robustness, which is checkable; not truth, which on contested questions is not. We also do not claim the effect is universal — it is bounded to poisons the model can in-principle evaluate (a fabricated unverifiable source broke both architectures) and to two model families.

---

## Limitations (stated, not hidden)

- Flat's aggregate conformity rate is judge-assisted (no structured artifact to audit).
- Samples are modest (N=5 per poison per condition per model); the pooled effect is significant but per-cell counts are small.
- Two model families, not a broad survey.
- The deterministic checks require a parseable map; Haiku emitted valid JSON less reliably than Gemini (flagged, not silently scored).

## Future direction: formal specification and tractability critique of robustness-ranked decomposition

We offer this not as a built prototype but as a formal specification and tractability critique — a category FLF explicitly invites ("a critique... indicating less tractability than we might have thought"). The natural generalization of this submission's durable move (*measure robustness, not truth*) is to stop producing a single flat map and instead **rank competing causal decompositions** by adversarial robustness.

**The specification.** A causal tree in which each non-leaf node carries an explicit logical gate (AND / OR) and each node a status in {established, refuted, contested, open}. Leaf statuses are assigned by the LLM; the root status is then computed *deterministically* by bottom-up propagation over that four-valued lattice (a Belnap bilattice), with no LLM in the propagation step. Conformity becomes a crisp binary: under a poisoned brief, the root either propagates to `established` (conformed) or it does not.

**Grounding in the LHC result we already have.** Our committed LHC map (`1684db2e`) found the safety case's "multiple independent defenses" are *not* an independent conjunction — they are conditionally dependent: the cosmic-ray argument only bears on safety *if* Hawking radiation fails, so if Hawking holds it is redundant, and the two share a common theoretical foundation that fails together. A flat synthesis can gloss this as "robust redundancy." A formal causal tree would have to *encode that conditional dependency in its gate structure*, so that the shared-assumption failure propagates a `contested` up to the root instead of a false `established`. That is the concrete payoff — and also the first tractability wall, because getting that gate structure right is exactly the hard part.

**Why it stays a specification, not a v1 build — three walls:**
1. *Combinatorial explosion.* The space of valid AND/OR wirings for a real epistemic question is intractable to search, and the scoring/decay parameters cannot be tuned without a calibration set that does not exist for contested questions.
2. *The leaf-evaluation bottleneck.* Propagation is deterministic, but the LLM still assigns the leaves — and under adversarial pressure LLMs *hedge*, assigning `contested` rather than `refuted` at exactly the poisoned leaf. The deterministic gate then propagates the hedge, softening the shield at the input boundary. (This is the same failure we observed directly: a keyword conformity detector failed because conformity is a final-stance property, not a vocabulary one.)
3. *Bidirectional convergence has a ceiling.* An appealing variant decomposes *forward* from the claim and *backward* from the outcome (bidirectional-Dijkstra style), treating convergence as corroboration — the backward search isn't anchored on the poisoned framing, so a lie must stay coherent from both ends. But because both decompositions come from the same model, convergence measures **internal-prior consistency, not truth**; on a genuinely novel question both directions can converge on a shared hallucination.

We deliberately did not build this: a half-baked prototype would obscure the validated determinism of the current EpistemicMap. This section maps the exact shape of the next advance while honestly bounding the walls that make it a v2 research program.

---

## Reproduce

```bash
pip install -r requirements.txt
cp .env.example .env   # GEMINI_API_KEY + JUDGE_MODEL=<a live model>

# The adversarial poison test + the no-LLM deterministic audit:
python phases/phase_e/run_phase_e.py --scenarios e02p1_eggs_poison_consensus e02p2_eggs_poison_fallacy e02p3_eggs_poison_source --conditions kalibr-chain flat-no-handoff --reps 5
python phases/phase_e/deterministic_audit.py
```

*Contact: aryan199841@gmail.com*
