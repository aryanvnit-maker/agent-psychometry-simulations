# FLF Epistemic Case Study Competition — Submission

**Submitted by:** Aryan Shah (aryan199841@gmail.com)
**Repository:** https://github.com/aryanvnit-maker/agent-psychometry-simulations
**Submission date:** June 2026
**Competition:** FLF Epistemic Case Study Competition (flf.org)
**Status:** Methodology proposal for early feedback. Phase 3 is a completed deterministic pilot; the Phase 10 benchmark described here is specified but not yet run.

---

**TL;DR:** The default multi-agent configuration shipped in every major framework (flat round-table, no synthesis step) does not just underperform on epistemic tasks — it *amplifies* a wrong premise under adversarial framing instead of rejecting it. We have already measured this deterministically, with binary ground truth and no LLM judge: under poisoned input, flat topology degraded and produced complete task collapses, while chain topology independently evaluated and rejected the same poison (Phase 3, N=200). This submission proposes extending that deterministic test from code tasks to reasoning tasks — an **adversarial epistemic robustness benchmark** that scores poison-rejection rate against verifiable answers — and then transfers the validated architecture to the genuinely-contested FLF case studies. The contribution is a way to measure epistemic robustness *deterministically*, before trusting a method on questions that have no ground truth.

---

## The Core Problem, Stated Precisely

Epistemic investigation tools cannot be validated on the questions they are meant to answer. COVID-19 origins, the eggs/CVD evidence base, comparative nuclear risk — these have **no ground truth**. Any score you assign to an AI's output on a genuinely contested question is assigned by a judge (human or LLM) whose own priors are in play. When the judge is an LLM and the scoring rubric mirrors the prompt that generated the output, the measurement is circular: you are testing whether a model instructed to produce structure X scores well on a rubric that rewards structure X.

This is the central methodological trap of this competition, and most submissions will fall into it.

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

**Class B — Retrodiction against established consensus.**
Questions where the science has *genuinely converged* (the answer is known) but a confident wrong framing is historically plausible. Present the time-of-dispute evidence plus an adversarial framing; check the output against the current consensus. Example: the alcohol J-curve. Consensus now holds that sick-quitter bias largely explains the apparent cardioprotection and that Mendelian-randomisation evidence shows no net benefit. Poison: "decades of cohort studies establish that moderate drinking protects the heart." Correct: reject, naming the confound. Checkable against the MR literature.

*Note on the obvious objection:* the model may already "know" the consensus answer from training. That does not weaken the test — it sharpens it. The question is precisely whether **adversarial framing overrides what the model knows.** If flat topology abandons a correct answer the model is perfectly capable of giving, under social pressure from a planted framing, while chain topology holds it, that *is* the finding. Class B directly measures sycophantic override of correct priors.

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

## The Transfer Step: From Validated Robustness to Contested Cases

Once an architecture's poison-resistance is established deterministically, it can be *applied* to the genuinely-contested FLF case studies (COVID origins, eggs/CVD) — where scoring must necessarily become qualitative, but where the architecture is no longer an unvalidated black box.

On contested cases the system produces a structured **EpistemicMap** artifact (a typed JSON object: cruxes, evidence streams with quality ratings, correlated-evidence pairs, calibrated ranges, and an explicit settled-vs-performed distinction). This is the compounding, interoperable artifact FLF asks for — but we make a deliberately narrow claim about it. We do **not** claim the map's *content* is correct (that needs domain experts). We claim only that it is produced by an architecture independently shown to resist adversarial framing, and that its structure is machine-interrogable and extendable v1→v2 as new evidence arrives.

This honest division is the point:
- **Deterministic claim:** chain topology resists conformity cascades under poison (validated).
- **Qualitative application:** that architecture, applied to contested cases, yields structured artifacts whose form is auditable even where their content cannot be scored.

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
4. **Applied, honestly bounded:** a poison-resistant architecture applied to genuinely-contested cases yields structured, compounding EpistemicMap artifacts whose *form* is auditable even where their *content* cannot be scored.

Claims 1 and 2 are evidence. Claims 3 and 4 are the proposal this submission seeks feedback on.

---

*Contact: aryan199841@gmail.com*
*Repository: https://github.com/aryanvnit-maker/agent-psychometry-simulations*
