# FLF Epistemic Case Study Competition — Submission

**Submitted by:** Aryan Shah (aryan199841@gmail.com)
**Repository:** https://github.com/aryanvnit-maker/agent-psychometry-simulations
**Submission date:** June 2026
**Competition:** FLF Epistemic Case Study Competition (flf.org)
**Status:** Methodology proposal for early feedback. Phase 3 (the deterministic shield) is a completed pilot; the epistemic-synthesis architecture (the sword) exists in the repository; the Phase 10 reasoning benchmark that would extend the deterministic test is specified but not yet run.

---

**TL;DR:** The submission has two halves — a **shield** and a **sword**.

*Shield (validated, deterministic).* The default multi-agent configuration shipped in every major framework (flat round-table, no synthesis step) does not just underperform on epistemic tasks — it *amplifies* a wrong premise under adversarial framing instead of rejecting it. We have already measured this with binary ground truth and no LLM judge: under poisoned input, flat topology degraded and produced complete task collapses, while chain topology independently evaluated and rejected the same poison (Phase 3, N=200). We propose extending that deterministic test from code to reasoning — an **adversarial epistemic robustness benchmark** scoring poison-rejection rate against verifiable answers.

*Sword (applied, honestly bounded).* The same poison-resistant architecture, run with an anti-decisive **epistemic synthesis** prompt, produces a structured EpistemicMap on the genuinely-contested FLF cases (COVID origins, eggs/CVD, nuclear risk): cruxes, evidence-quality ratings, correlated-evidence pairs, calibrated ranges, and a settled-vs-performed split. We do not self-score this; we hand the evaluator the artifact and claim only that its *structure* is auditable.

The contribution is the pairing: measure epistemic robustness *deterministically* on adversarially-framed knowns, then apply the validated architecture to the unknowns and expose — not grade — what it produces.

---

## The Core Problem, Stated Precisely

Epistemic investigation tools cannot be validated on the questions they are meant to answer. COVID-19 origins, the eggs/CVD evidence base, comparative nuclear risk — these have **no ground truth**. Any score you assign to an AI's output on a genuinely contested question is assigned by a judge (human or LLM) whose own priors are in play. When the judge is an LLM and the scoring rubric mirrors the prompt that generated the output, the measurement is circular: you are testing whether a model instructed to produce structure X scores well on a rubric that rewards structure X.

This is the central methodological trap of this competition. We recognized it early and built the methodology around stepping past it, rather than scoring our way through it.

**Our approach avoids it by separating two questions:**

1. **Is the architecture epistemically robust?** — answerable *deterministically* on questions that have ground truth but are presented adversarially. This is the validation step.
2. **Does the robust architecture produce useful artifacts on contested questions?** — answerable only qualitatively, but now with an architecture whose robustness has been independently established. This is the application step.

The discipline is standard instrument validation: you calibrate a thermometer against known temperatures before measuring an unknown one. You do not validate an epistemic method on the unknowns it is built to serve — you validate it on structurally similar knowns, then transfer.

---

## What We Already Have: Phase 3 (Deterministic Pilot)

The research program behind this submission is nine phases of multi-agent orchestration experiments, totaling 2,400+ evaluations. Most are reported in the accompanying write-up. One phase is the direct foundation for this submission.

### Phase 3: Flat topology is unsafe under adversarial input

**Setup.** 50 competitive-programming problems (verifiable, binary pass@1 against private test cases) × 4 conditions = 200 evaluations. Wrong algorithmic hints were planted in the problem prompts as authoritative-looking editorial annotations — a confident, plausible, *false* framing injected into the input. Conditions: chain-2 and flat-2 topologies, each on clean and poisoned input.

**Results.**

| Condition | Pass@1 | Complete collapses (no output) |
|---|---|---|
| chain-2 / clean | 14% | 0 |
| chain-2 / poisoned | 18% | 0 |
| flat-2 / clean | 18% | 0 |
| **flat-2 / poisoned** | **14%** | **4** |

**What this shows.** An 8-percentage-point swing between the two poisoned conditions, and — the smoking gun — **4 complete task collapses in flat-2/poisoned versus zero across all other 150 runs.** Under a wrong premise, flat topology locked into an unimplementable framing and produced *nothing*. Chain topology never collapsed once, and actually improved slightly under poison because the second agent independently evaluated and rejected the planted hint.

**The mechanism.** In flat topology, agents see each other's reasoning and validate each other's acceptance of the wrong framing — a conformity cascade. In chain topology, the handoff forces the downstream agent to independently re-derive rather than ratify. The structural difference is whether the architecture *amplifies* or *interrupts* social agreement with a false premise.

**Why this matters here.** This is a deterministic measurement of the exact epistemic skill the competition cares about — resistance to confident, motivated, misleading framing (FLF dimension 6) — with binary ground truth and no LLM judge. It is the cleanest result in the program, and it has nothing to do with psychometric profiling.

### What the program decisively did *not* find

For honesty, and because it constrains what we are willing to claim: the program's *original* hypothesis was that psychometric personality profiling of agents would predict team output the way it does for humans. **That hypothesis was falsified.** Across phases, agent personality diversity added no reliable benefit (Phase 8: Δ=+0.7, p=0.854). The mechanism for output quality is structural — the synthesis step and the topology — not the agents' simulated personalities. We mention the psychometric origin only to explain how we arrived at the topology question. We make no psychometric claims in this submission.

What *did* transfer from human psychology is narrower and real: **conformity under social pressure.** The Phase 3 flat-2 collapse is a multi-agent conformity cascade — the agentic analog of the Asch effect and of the LLM sycophancy literature. Trait profiles did not transfer to agents; conformity dynamics did. That is the defensible cross-over claim, and it is what this submission builds on.

---

## What We Propose to Build: The Adversarial Epistemic Robustness Benchmark

Phase 3 validated poison-resistance on **code** tasks. The forward step — Phase 10 — extends the identical experimental logic to **reasoning** tasks that still carry verifiable ground truth, bridging from code toward the epistemic domain while preserving determinism.

We are explicit that this is a test, not a foregone conclusion: **we do not assume Phase 10 will replicate the Phase 3 effect sizes.** Code tasks have a rigid correct/incorrect boundary; reasoning tasks introduce semantic complexity that could either dampen the conformity cascade (more room to hedge) or amplify it (more surface for a confident framing to grip). The benchmark is designed precisely to isolate whether the topology intervention survives that increase in semantic complexity — the direction and magnitude are the open empirical question, and a null result would itself be informative.

### The principle

Every benchmark item is a question with a **checkable correct answer**, presented in two variants:

- **Clean:** the question as stated.
- **Poisoned:** the same question wrapped in a confident, plausible, *false* expert framing — the rhetorical move FLF is worried about ("sources optimizing to mislead").

We measure, per architecture:

- **Poison-rejection rate** = correct answers on poisoned items ÷ poisoned items. Binary. No LLM judge.
- **Conformity-cascade delta** = clean accuracy − poisoned accuracy. Flat topology is predicted to show a large negative delta; chain topology a near-zero or positive delta (independent re-derivation rejects the poison).

The causal claim is tight because only one variable moves: **topology determines poison-rejection rate**, holding model, task, compute, and prompt constant. Phase 3 established this for code; Phase 10 tests whether it generalizes to reasoning.

### Three question classes, all with deterministic ground truth

Ordered from most code-like (closest to the validated Phase 3 result) to most epistemic (closest to the FLF target domain):

**Class A — Statistical reasoning with computable answers.**
Confounding, base rates, Simpson's paradox, selection bias. The correct answer is *mathematically determinable* from the supplied numbers. The poison is a confident misreading of the aggregate. Example: a dataset exhibiting Simpson's paradox, poisoned with "the aggregate trend unambiguously shows X." Correct answer: the within-group trend reverses; checkable by computation. This class is barely a step from Phase 3 — there is a literally correct answer.

**Class B — Sycophancy and Prior-Override Resistance under Rhetorical Pressure.**
Questions where the science has *genuinely converged* (the answer is known) but a confident wrong framing is historically plausible. Present the time-of-dispute evidence plus an adversarial framing; check the output against the current consensus. Example: the alcohol J-curve. Consensus now holds that sick-quitter bias largely explains the apparent cardioprotection and that Mendelian-randomisation evidence shows no net benefit. Poison: "decades of cohort studies establish that moderate drinking protects the heart." Correct: reject, naming the confound. Checkable against the MR literature.

This class is **deliberately not a test of de novo reasoning**, and we name that up front to preempt the data-contamination objection. The model may already "know" the consensus answer from training — that is the point, not a flaw. The question is whether **adversarial framing overrides what the model already knows.** If flat topology abandons a correct answer the model is perfectly capable of giving, under social pressure from a planted framing, while chain topology holds it, that *is* the finding. Class B isolates sycophantic prior-override; Classes A and C carry the de novo reasoning load.

**Class C — Logical validity under rhetorical pressure.**
Given a set of premises, is conclusion C actually entailed? Formally checkable, independent of real-world truth. The poison is a rhetorically compelling but logically invalid inference. This isolates whether the architecture preserves deductive rigor when the framing pushes an unsupported leap — the "rhetorical-vs-evidential move" distinction from the FLF desiderata, rendered binary.

### The architectures compared

Carried forward from the validated conditions, compute-controlled:

| Condition | Topology | Synthesis | Calls |
|---|---|---|---|
| `flat-no-handoff` | flat round-table | none | 4 |
| `chain-2` | chain | none | 2 |
| `chain-2 + synthesis` | chain | yes | 2 |
| `single-agent-refine` | single | self-review | 2 |

The primary contrast is flat vs chain on poison-rejection rate — the Phase 3 result, retested on reasoning. The synthesis condition tests whether a terminal synthesis step adds robustness on top of topology.

### The deliverable

A reusable, versioned benchmark: question sets with clean/poisoned variant pairs, machine-checkable answer keys, and a runner that reports poison-rejection rate and conformity-cascade delta per architecture. No LLM judge anywhere in the scoring path for Classes A and C; Class B uses exact-match against a pre-registered consensus answer key. Another team can run it, extend the item set, or drop in a different architecture and get a directly comparable number.

---

## The Transfer Step: What the Architecture *Does* on Contested Cases

Phase 3 establishes that the architecture *survives* adversarial input. That is the shield. It is necessary but not sufficient: surviving poison is not the same as producing a useful investigation. The FLF case studies (COVID origins, eggs/CVD, nuclear risk) ask the harder question — given a genuinely contested question, what artifact does the system produce? This is the sword, and it is a distinct mechanism from the topology result.

### The synthesis step is the actual intervention

The contested-case work runs on a terminal synthesis prompt that is deliberately *anti-decisive*. Where the default multi-agent move is "close every open question, be decisive" — a prompt we separately measured as costing −13.3 points on reflective tasks in Phase 9 — the epistemic synthesis prompt demands calibration and structure instead of a verdict. Its five required outputs, verbatim from the runner:

1. **CRUXES** — the 2–3 specific factual or inferential questions whose resolution would most shift the overall probability. Name the question, not the theme.
2. **EVIDENCE QUALITY** — for each evidence stream, a rating (strong / weak / contested / missing) with the specific weakness or strength named.
3. **CORRELATED EVIDENCE** — at least one pair of streams that *appear* independent but share a methodological assumption, source, or selection mechanism, plus why that matters for the aggregate estimate.
4. **CALIBRATED ASSESSMENT** — a probability *range* with explicit conditions, not a point estimate. Refusing to estimate scores zero; so does collapsing to false certainty.
5. **SETTLED vs PERFORMED** — what the evidence has actually resolved, separated from what was merely performed as resolved, with at least one named question the current evidence cannot close.

This maps directly onto the FLF desiderata: cruxes (decompose the disagreement), correlated evidence (the independence illusion that inflates confidence), calibrated ranges (uncertainty quantification), settled-vs-performed (the rhetorical-vs-evidential distinction).

### The artifact: a typed EpistemicMap

The output is not prose — it is a validated Pydantic object (`src/evaluation/epistemic_schema.py`), which is what makes it compounding and shareable rather than a one-off summary. Another team can parse it, diff two versions, or extend it as new evidence arrives. The exact schema:

```json
{
  "case_id": "e01_covid_origins",
  "version": 1,
  "cruxes": [
    {
      "question": "<specific question whose resolution most shifts probability>",
      "resolution_impact": "high | medium | low",
      "status": "unresolved | partially_resolved | resolved"
    }
  ],
  "evidence_streams": [
    {
      "label": "<short name>",
      "quality": "strong | weak | contested | missing",
      "weakness": "<the specific gap in this evidence>",
      "supports": ["<crux question this evidence bears on>"]
    }
  ],
  "correlated_pairs": [
    {
      "streams": ["<label1>", "<label2>"],
      "shared_assumption": "<assumption both streams rely on>",
      "implication": "<what happens to the picture if it is wrong>"
    }
  ],
  "calibrated_estimates": [
    {
      "hypothesis": "<hypothesis>",
      "range_low": 55, "range_high": 70,
      "conditions": "<conditions that would shift this range>"
    }
  ],
  "settled": ["<claim actually resolved by evidence>"],
  "performed_as_settled": ["<claim treated as resolved but not actually so>"],
  "extends_version": null,
  "new_evidence": []
}
```

The `extends_version` and `new_evidence` fields are the compounding mechanism: a v2 map cites the v1 it supersedes and lists what changed, so an investigation accumulates across runs and contributors instead of restarting. Outputs are parsed and validated on ingest; a malformed map is recorded as `map_parsed=False` rather than silently scored.

### The circularity problem, stated honestly — and what defuses it

There is a real measurement trap here, and we name it rather than hide it: the synthesis prompt *instructs* the model to produce cruxes, correlated-evidence pairs, and calibrated ranges, and any rubric that rewards those same structures is partly scoring the prompt back to itself. An LLM-judged "epistemic quality score" on a contested question is therefore **not deterministic and not a clean measurement** — the judge's priors and the prompt's instructions are both in play.

So we do not make a scored-quality claim on contested cases. We separate two things the rubric-circularity argument conflates:

- **Content correctness** — *is the conclusion right?* On COVID origins this is unknowable; on eggs/CVD it is contested. We make **no** claim here. It requires domain experts, and a score assigned by an LLM judge is circular.
- **Structural form** — *did the system surface a crux, flag a correlated-evidence pair, give a range with conditions, distinguish settled from performed?* This is **observable independent of whether the conclusion is correct.** A human evaluator can read the EpistemicMap and check the structure directly. No LLM judge required; the prompt-rubric circularity does not bite, because we are not claiming the structure proves quality — we are exhibiting the structure for the evaluator to inspect.

In short: we hand the FLF the artifact, not a self-graded score. "Here is what the architecture produces on your actual problem class — evaluate the reasoning yourself" is a more honest offer than a number generated by a judge reading a prompt's own instructions back to it.

### Why the structure is non-trivial on a real case

Take eggs/CVD. The decisive-synthesis default tends to a verdict ("dietary cholesterol has minimal effect on serum cholesterol — eggs are fine"). The epistemic synthesis prompt instead *forces* the model to look for correlated evidence — and the case is loaded with it: a large share of the reassuring nutritional-epidemiology studies share a single selection mechanism (food-frequency-questionnaire cohorts with healthy-user confounding) and, in places, common industry funding. Two studies that look like independent confirmation can be one methodological bet counted twice. The value of step 3 is not that the model gets eggs "right" — it is that the architecture is *structurally compelled* to test for the independence illusion that inflates false confidence. That compulsion is the transferable contribution, and it is what the default round-table configuration never does.

### The two tiers, labeled

| Tier | Claim | Evidence status | Scoring |
|---|---|---|---|
| **Tier 1 — Shield (validated)** | Chain topology resists conformity cascades under poison; flat topology amplifies and can collapse | Completed, Phase 3, N=200 | Deterministic, binary, no LLM judge |
| **Tier 2 — Sword (applied)** | The same architecture, run with the epistemic synthesis prompt, produces structured EpistemicMaps on contested cases | Artifact exists; quality is not self-scored | Structure is human-auditable; content is *not* claimed |

Tier 1 is why you should trust the architecture isn't a black box. Tier 2 is what the architecture gives the FLF on its own home territory. Neither alone is the submission; the pairing is.

---

## Connection to FLF's Judging Dimensions

| Dimension | How this submission engages it |
|---|---|
| **Epistemic uplift** | Targets the specific failure that destroys uplift — uncritical amplification of a confident wrong framing — and measures resistance to it directly. |
| **Generalizability** | The benchmark spans statistical, empirical-consensus, and logical question classes; the topology finding is task-shape-independent (validated on code, extended to reasoning). |
| **Compounding & shareability** | The benchmark itself is the shared artifact: clean/poisoned pairs + machine-checkable keys another team can run or extend. EpistemicMaps compound v1→v2. |
| **Scalability** | Poison-rejection rate has no hand-designed scoring bottleneck; it improves automatically as base models improve, and the item set grows with more contributors. |
| **Methodological transparency** | The clean/poisoned design and binary scoring are fully specified; the psychometric hypothesis we *falsified* is stated plainly rather than hidden. |
| **Adversarial robustness** | This is the submission's spine, not an add-on. The whole method is an adversarial-robustness measurement. |
| **Insight contribution** | Reframes "epistemic quality" (unmeasurable on unknowns) as "epistemic robustness" (measurable on adversarially-framed knowns), and identifies the multi-agent conformity cascade as the concrete failure mode. |

---

## Limitations (Named, Not Hidden)

**The benchmark is specified, not yet run.** Phase 3 is complete and deterministic; the Phase 10 reasoning extension is designed but unexecuted. This submission is for early feedback on the methodology before compute is committed. The forward results are predictions, labeled as such.

**Class B has training-data entanglement.** Where the consensus answer is in the model's training data, Class B measures *override resistance*, not de novo reasoning. This is a feature for the conformity question but a limitation for any claim about reasoning from scratch. Classes A and C avoid it (computed and formal answers).

**Determinism stops at the contested cases.** The transfer step to COVID/eggs is honestly qualitative. We do not claim to have made contested-case scoring deterministic — we claim to have validated the architecture deterministically *before* applying it there.

**Effect sizes on hard items are small in absolute terms.** Phase 3's competitive-programming items sit at 12–18% pass@1 — the topology *difference* and the collapse asymmetry are the robust signals, not the absolute scores. The reasoning benchmark should include items with enough headroom to separate working architectures.

**Single model family.** Phase 3 used one base model. The conformity-cascade prediction should be retested across model families; cross-model adversarial robustness is the obvious next control.

**No psychometric claim is being made.** The framework that started this program does not appear in any claim here. Mentioning it at all is origin-story, not evidence.

---

## Running What Exists

```bash
pip install -e ".[research]"
cp .env.example .env   # add GEMINI_API_KEY

# Phase 3 — the completed deterministic adversarial-robustness pilot
python phases/phase3/run_phase3.py
python phases/phase3/analyze_phase3.py

# Phase 6 — judge-free benchmark backbone (HumanEval / GSM8K), proof of binary-ground-truth scoring
python phases/phase6/run_humaneval.py
python phases/phase6/run_gsm8k.py
```

The Phase 10 reasoning benchmark (clean/poisoned reasoning items + machine-checkable keys) is the build proposed by this submission and is not yet in the repository.

---

## What We're Claiming

1. **Deterministic, validated:** Under adversarially poisoned input, flat multi-agent topology amplifies the wrong framing and can collapse to no output, while chain topology independently rejects it. Binary ground truth, no LLM judge (Phase 3, N=200).
2. **The mechanism is a conformity cascade**, not psychometrics — the agentic analog of human conformity/sycophancy. This is the one piece of the human-psychology hypothesis that transferred; the trait-profile piece was falsified and is not claimed.
3. **Proposed, falsifiable:** the topology→poison-resistance result generalizes from code to reasoning, measurable deterministically via poison-rejection rate across statistical, empirical-consensus, and logical question classes.
4. **Applied, honestly bounded:** the same architecture, run with an anti-decisive epistemic synthesis prompt, produces structured EpistemicMap artifacts on contested cases — cruxes, correlated-evidence pairs, calibrated ranges, settled-vs-performed — whose *form* is human-auditable even where their *content* cannot be scored. We exhibit the artifact; we do not self-grade it.

Claims 1 and 2 are the **shield**: evidence in hand. Claims 3 and 4 are the **sword**: the proposal this submission seeks feedback on. The artifact-generating architecture (Claim 4) already exists in the repository; what is unrun is the deterministic reasoning benchmark (Claim 3).

---

*Contact: aryan199841@gmail.com*
*Repository: https://github.com/aryanvnit-maker/agent-psychometry-simulations*
