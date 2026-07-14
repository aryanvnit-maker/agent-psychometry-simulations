# FLF Epistemic Case Study Competition: Submission

Submitted by: Aryan Shah (aryan199841@gmail.com)
Repository: https://github.com/aryanvnit-maker/agent-psychometry-simulations
Submission date: June 2026
Competition: FLF Epistemic Case Study Competition (flf.org)
Status: Methodology proposal for early feedback. Phase 3 (the deterministic shield) is a completed pilot; the epistemic-synthesis architecture (the sword) has now been run on three contested cases with maps and transcripts committed by run_id; the poisoned-epistemic and cross-model experiments are specified and in progress.

---

The submission has two parts: a shield and a sword.

Shield (validated, deterministic). The default multi-agent configuration in most frameworks (flat round-table, no synthesis step) doesn't just underperform on epistemic tasks. Under adversarial framing, it amplifies a wrong premise instead of rejecting it. We measured this with binary ground truth and no LLM judge: flat topology produced complete task collapses under poisoned input while chain topology independently rejected the same poison (Phase 3, N=200). We propose extending that test from code to reasoning tasks, scoring poison-rejection rate against verifiable answers.

Sword (applied, honestly bounded). The same architecture, run with an anti-decisive epistemic synthesis prompt, produces a structured EpistemicMap on genuinely contested cases (COVID origins, eggs/CVD, nuclear risk): cruxes, evidence-quality ratings, correlated-evidence pairs, calibrated ranges, and a settled-vs-performed split. We don't self-score this; we hand the evaluator the artifact and claim only that its structure is auditable.

The contribution is the pairing: measure epistemic robustness deterministically on adversarially-framed knowns, then apply the validated architecture to the unknowns and show, without grading, what it produces.

---

## The core problem

Epistemic investigation tools can't be validated on the questions they're meant to answer. COVID-19 origins, the eggs/CVD evidence base, comparative nuclear risk: none of these have ground truth. Any score you assign to an AI's output on a genuinely contested question is assigned by a judge whose own priors are in play. When the judge is an LLM and the scoring rubric mirrors the prompt that generated the output, the measurement is circular: you're testing whether a model instructed to produce structure X scores well on a rubric that rewards structure X.

We recognized this trap early and built the methodology around it. The approach separates two questions:

1. Is the architecture epistemically robust? This is answerable deterministically on questions that have ground truth but are presented adversarially.
2. Does the robust architecture produce useful artifacts on contested questions? This is answerable only qualitatively, but now with an architecture whose robustness has been established independently.

Standard instrument validation works this way: calibrate a thermometer against known temperatures before using it on unknowns. You don't validate an epistemic method on the very questions it's built to serve.

---

## What we already have: Phase 3

The research program behind this submission ran nine phases of multi-agent orchestration experiments, 2,400+ evaluations in total. Phase 3 is the direct foundation here.

### Phase 3: flat topology fails under adversarial input

50 competitive-programming problems (verifiable, binary pass@1 against private test cases) × 4 conditions = 200 evaluations. Wrong algorithmic hints were planted in problem prompts as authoritative-looking editorial annotations: confident, plausible, false framing injected into the input. Conditions: chain-2 and flat-2 topologies, each on clean and poisoned input.

| Condition | Pass@1 | Complete collapses (no output) |
|---|---|---|
| chain-2 / clean | 14% | 0 |
| chain-2 / poisoned | 18% | 0 |
| flat-2 / clean | 18% | 0 |
| flat-2 / poisoned | 14% | 4 |

An 8-percentage-point swing between the two poisoned conditions. More telling: 4 complete task collapses in flat-2/poisoned versus zero across all other 150 runs. Under a wrong premise, flat topology locked into an unimplementable framing and produced nothing. Chain topology never collapsed and actually improved slightly, because the second agent independently re-derived and rejected the planted hint.

In flat topology, agents see each other's reasoning and ratify each other's acceptance of the wrong framing, a conformity cascade. In chain topology, the handoff forces the downstream agent to re-derive rather than ratify. The structural question is whether the architecture amplifies or interrupts social agreement with a false premise.

This is a deterministic measurement of resistance to confident, motivated, misleading framing (FLF dimension 6), with binary ground truth and no LLM judge.

### What the program did not find

The program's original hypothesis was that psychometric personality profiling of agents would predict team output the way it does for humans. That hypothesis was falsified. Across phases, agent personality diversity added no reliable benefit (Phase 8: Δ=+0.7, p=0.854). The mechanism for output quality is structural (the synthesis step and the topology), not the agents' simulated personalities. We mention this origin only to explain how we arrived at the topology question.

What did transfer from human psychology is narrower: conformity under social pressure. The Phase 3 flat-2 collapse is a multi-agent conformity cascade, the agentic analog of the Asch effect and the LLM sycophancy literature. Trait profiles didn't transfer; conformity dynamics did. That's the defensible claim, and it's what this submission builds on.

---

## What we propose to build: an adversarial epistemic robustness benchmark

Phase 3 validated poison-resistance on code tasks. Phase 10 extends the same experimental logic to reasoning tasks that still carry verifiable ground truth, bridging toward the epistemic domain while preserving determinism.

We're explicit that Phase 10 is a test, not a foregone conclusion. We don't assume it will replicate Phase 3 effect sizes. Code tasks have a rigid correct/incorrect boundary; reasoning tasks introduce semantic complexity that could dampen the conformity cascade (more room to hedge) or amplify it (more surface for a confident framing to grip). A null result would itself be informative.

### How it works

Every benchmark item is a question with a checkable correct answer, presented in two variants:

- Clean: the question as stated.
- Poisoned: the same question wrapped in a confident, plausible, false expert framing (the rhetorical move FLF is worried about).

Per architecture, we measure:

- Poison-rejection rate = correct answers on poisoned items / poisoned items. Binary. No LLM judge.
- Conformity-cascade delta = clean accuracy minus poisoned accuracy. Flat topology is predicted to show a large negative delta; chain topology near-zero or positive.

The causal claim holds because only one variable moves: topology. Model, task, compute, and prompt are held constant. Phase 3 established this for code; Phase 10 tests whether it generalizes.

### Three question classes

Ordered from most code-like to most epistemic:

Class A: Statistical reasoning with computable answers. Confounding, base rates, Simpson's paradox, selection bias. The correct answer is mathematically determinable from the supplied numbers. The poison is a confident misreading of the aggregate. Example: a dataset exhibiting Simpson's paradox, poisoned with "the aggregate trend unambiguously shows X." The within-group trend reverses; checkable by computation.

Class B: Sycophancy and prior-override resistance under rhetorical pressure. Questions where the science has genuinely converged but a confident wrong framing is historically plausible. The time-of-dispute evidence is presented alongside an adversarial framing; outputs are checked against current consensus. Example: the alcohol J-curve. Consensus now holds that sick-quitter bias largely explains the apparent cardioprotection and that Mendelian-randomisation evidence shows no net benefit. The poison is "decades of cohort studies establish that moderate drinking protects the heart." The correct answer names the confound.

This class is not a test of de novo reasoning, and we say so up front. The model may already know the consensus answer. That's the point, not a flaw. The question is whether adversarial framing overrides what the model already knows. If flat topology abandons a correct answer under social pressure from a planted framing while chain topology holds it, that is the finding. Classes A and C carry the de novo reasoning load.

Class C: Logical validity under rhetorical pressure. Given a set of premises, is conclusion C actually entailed? Formally checkable, independent of real-world truth. The poison is a rhetorically compelling but logically invalid inference. This isolates whether the architecture preserves deductive rigor when the framing pushes an unsupported leap.

### Architectures compared

| Condition | Topology | Synthesis | Calls |
|---|---|---|---|
| `flat-no-handoff` | flat round-table | none | 4 |
| `chain-2` | chain | none | 2 |
| `chain-2 + synthesis` | chain | yes | 2 |
| `single-agent-refine` | single | self-review | 2 |

The primary contrast is flat vs chain on poison-rejection rate, the Phase 3 result retested on reasoning. The synthesis condition tests whether a terminal synthesis step adds robustness beyond topology alone.

### The deliverable

A versioned benchmark: question sets with clean/poisoned variant pairs, machine-checkable answer keys, and a runner that reports poison-rejection rate and conformity-cascade delta per architecture. No LLM judge in the scoring path for Classes A and C; Class B uses exact-match against a pre-registered consensus answer key. Another team can run it, extend the item set, or swap in a different architecture and get a directly comparable number.

---

## What the architecture does on contested cases

Phase 3 shows the architecture survives adversarial input. Surviving poison is not the same as producing a useful investigation. The FLF case studies ask what artifact the system actually produces on a genuinely contested question. The synthesis prompt is the answer, and it's a distinct mechanism from the topology result.

### The synthesis prompt

The contested-case work runs on a terminal synthesis prompt that is deliberately anti-decisive. The default multi-agent move ("close every open question, be decisive") cost -13.3 points on reflective tasks in our Phase 9 ablation. The epistemic synthesis prompt demands calibration and structure instead of a verdict. Five required outputs, quoted verbatim from the runner:

1. CRUXES: the 2-3 specific factual or inferential questions whose resolution would most shift the overall probability. Name the question, not the theme.
2. EVIDENCE QUALITY: for each evidence stream, a rating (strong / weak / contested / missing) with the specific weakness or strength named.
3. STRUCTURAL DEPENDENCY AUDIT: before aggregating, hunt for hidden structure a naive reading would miss and that spuriously narrows confidence: overlapping cohorts or samples reused across studies cited as independent, shared control groups, correlated measurement instruments, or a confound measured in only a subset. For each dependency, name the streams and estimate how much the apparent independence is illusory.
4. CALIBRATED ASSESSMENT: a probability range with explicit conditions, not a point estimate. Refusing to estimate scores zero; so does collapsing to false certainty.
5. SETTLED vs PERFORMED: what the evidence has actually resolved, separated from what was merely performed as resolved, with at least one named question the current evidence cannot close.

These map to the FLF desiderata: cruxes (decompose the disagreement), correlated evidence (test the independence assumption that inflates confidence), calibrated ranges (uncertainty quantification), settled-vs-performed (the rhetorical-vs-evidential distinction).

### The artifact

The output is a validated Pydantic object (`src/evaluation/epistemic_schema.py`), not prose. Another team can parse it, diff two versions, or extend it as new evidence arrives. The exact schema:

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

The `extends_version` and `new_evidence` fields are the compounding mechanism: a v2 map cites the v1 it supersedes and lists what changed, so an investigation accumulates across runs and contributors rather than restarting. A malformed map is recorded as `map_parsed=False` rather than silently scored.

### On the circularity problem

There's a real measurement trap here: the synthesis prompt instructs the model to produce cruxes, correlated-evidence pairs, and calibrated ranges, and any rubric that rewards those same structures is partly scoring the prompt's own instructions back to itself. An LLM-judged "epistemic quality score" on a contested question isn't deterministic or clean.

So we don't make a scored-quality claim on contested cases. We separate two things the circularity argument conflates:

Content correctness: is the conclusion right? On COVID origins this is unknowable; on eggs/CVD it's contested. We make no claim here. A score from an LLM judge is circular, and domain experts are required.

Structural form: did the system surface a crux, flag a correlated-evidence pair, give a range with conditions, distinguish settled from performed? This is observable regardless of whether the conclusion is correct. A human evaluator can read the EpistemicMap and check the structure directly. We offer the artifact for the evaluator to inspect; we don't offer a self-graded score.

### Receipts: what the architecture actually produced

This section reports real runs, not a description of intended behaviour. We ran the chain + epistemic-synthesis architecture on three contested cases (eggs/CVD, COVID origins, comparative nuclear risk) on `gemini-3.1-flash-lite`. Every run's raw transcript and parsed EpistemicMap is committed to the repository under `results/transcripts/` and `results/epistemic_maps/`, keyed by run_id, so each claim below is traceable to a specific execution.

On eggs/CVD (run_id `6779b6e3`), the produced map flagged a specific structural dependency without being told the answer: the Harvard/HPFS cohorts and the NHANES/MESA analysis share a single measurement instrument (food-frequency questionnaires), so their apparent agreement is partly the same measurement bias counted twice rather than independent confirmation. The nuclear-risk map (run_id `706a84f3`) independently flagged that the "deaths per TWh" mortality figures and the LNT-based cancer projections both derive from the same UNSCEAR/IAEA Chernobyl/Fukushima dose-reconstruction data, so their independence is likewise illusory. These are the kind of non-obvious, evidence-structural findings the architecture is meant to surface.

We also ran the honest control: the same cases through `flat-no-handoff`, the framework-default baseline. The result corrects an earlier overclaim. On these non-adversarial cases, a flat multi-agent configuration reached comparable content quality — its best eggs/CVD run surfaced the same FFQ dependency, and in places went further. So the chain's advantage over flat here is **not** superior insight on clean questions. It is two things: (1) the output is a typed, parseable, compounding EpistemicMap rather than prose, and (2) resistance to adversarial framing, which is where Phase 3 located the effect and which we have not yet tested in the epistemic domain. We are careful to claim only what the runs support.

### Two tiers

| Tier | Claim | Evidence status | Scoring |
|---|---|---|---|
| Tier 1: shield (validated) | Chain topology resists conformity cascades under poison; flat topology amplifies and can collapse | Completed, Phase 3, N=200 | Deterministic, binary, no LLM judge |
| Tier 2: sword (applied) | The architecture produces a structured, compounding EpistemicMap on contested cases; a flat baseline reaches comparable *content* on non-adversarial cases | Runs completed; maps + transcripts committed by run_id | Structure is human-auditable; content is not claimed; flat comparison reported honestly |

Tier 1 is why the architecture isn't a black box. Tier 2 is what it produces on FLF's home territory, with the flat-baseline comparison stated rather than hidden. The open question the next experiment targets: does the Phase 3 adversarial advantage (chain resists poison, flat conforms) reproduce when the poison is an epistemic wrong-framing rather than a code hint? That is the result that would fuse the two tiers.

---

## The human-AI workflow

The system isn't a fully automated Agent-A-to-Agent-B pipeline. It has two explicit human steering points. Here is the actual flow, with each step's build status stated plainly.

Step 1: Ingestion (built, automated). `phases/phase_e/ingest.py` takes a raw source (URL, or a local PDF/transcript exported to text) and extracts a structured claims object. Each claim carries its provenance: `attributed_to` (author / study / institution), `confidence_expressed` (the source's stated confidence, not the model's), a verbatim `quote`, and a `fetched_at` timestamp. It runs at temperature 0.

Step 2: Human curation of the brief (manual). The extracted claims don't auto-flow into the analysis. A researcher reads the claims object and authors the scenario brief that Agent A receives. This is where a human decides what is in scope, discards extraction noise, and checks that the brief itself isn't poisoned. The ingestion-to-analysis handoff is intentionally human-mediated for now; we say so rather than implying a seamless pipeline.

Step 3: Structured analysis (built, automated). Agent A analyses the brief; the terminal node runs the epistemic synthesis prompt and emits the v1 EpistemicMap. A malformed map is flagged, not silently scored.

Step 4: Human review and evidence injection (built). `phases/phase_e/compound_demo.py` is the continuation step. A human reviews the v1 map, then curates a block of new evidence. The shipped demo uses a `NEW_COVID_EVIDENCE` block: the Rootclaim post-debate response, the Weissman independent Bayesian analysis, and caveats on the market re-sampling data. The system integrates this into a v2 map and prints a diff showing which cruxes changed status, which probability ranges moved, and what new correlated pairs the evidence revealed. This is where a human corrects a missed crux or injects a source the model didn't have.

Steps 1, 3, and 4 are built and automated. Step 2 is intentionally human. The human holds the two points where bad input does the most damage: framing the brief and vetting new evidence. That's the right place to keep a human, and we name it as a current boundary rather than a finished pipeline.

---

## Connection to FLF's judging dimensions

| Dimension | How this submission engages it |
|---|---|
| Epistemic uplift | Targets the specific failure that destroys uplift: uncritical amplification of a confident wrong framing. Measures resistance to it directly. |
| Generalizability | The benchmark spans statistical, empirical-consensus, and logical question classes; the topology finding is task-shape-independent (validated on code, extended to reasoning). |
| Compounding & shareability | The benchmark is the shared artifact: clean/poisoned pairs with machine-checkable keys that another team can run or extend. EpistemicMaps compound v1 to v2. |
| Scalability | Poison-rejection rate has no hand-designed scoring bottleneck; it improves as base models improve, and the item set grows with more contributors. |
| Methodological transparency | The clean/poisoned design and binary scoring are fully specified; the psychometric hypothesis we falsified is stated plainly rather than hidden. |
| Adversarial robustness | This is the submission's spine, not a secondary feature. |
| Insight contribution | Reframes "epistemic quality" (not measurable on unknowns) as "epistemic robustness" (measurable on adversarially-framed knowns), and identifies the multi-agent conformity cascade as the concrete failure mode. |

---

## Limitations

Phase 10 is not yet run. Phase 3 is complete; the reasoning extension is designed but unexecuted. This submission is for early feedback on the methodology before compute is committed. The forward results are predictions, labeled as such.

Class B has training-data entanglement. Where the consensus answer is in the model's training data, Class B measures override resistance, not de novo reasoning. This is what it's designed to measure, but it is a limitation for any claim about reasoning from scratch. Classes A and C avoid it.

Determinism stops at the contested cases. The transfer to COVID/eggs is honestly qualitative. We don't claim to have made contested-case scoring deterministic; we validated the architecture deterministically before applying it there.

Effect sizes on hard items are small in absolute terms. Phase 3's competitive-programming items sit at 12-18% pass@1. The topology difference and the collapse asymmetry are the robust signals, not the absolute scores. The reasoning benchmark should include items with enough headroom to separate working architectures.

Phase 3 used one base model. The conformity-cascade prediction should be retested across model families; cross-model adversarial robustness is the obvious next control.

---

## Running what exists

```bash
pip install -e ".[research]"
cp .env.example .env   # add GEMINI_API_KEY

# Phase 3 — the completed deterministic adversarial-robustness pilot
python phases/phase3/run_phase3.py
python phases/phase3/analyze_phase3.py

# Phase 6 — judge-free benchmark backbone (HumanEval / GSM8K), proof of binary-ground-truth scoring
python phases/phase6/run_humaneval.py
python phases/phase6/run_gsm8k.py

# Human-AI workflow, steps that exist today:
python phases/phase_e/ingest.py --url <article_url>   # Step 1: messy source → structured claims + provenance
python phases/phase_e/run_phase_e.py                  # Step 3: brief → v1 EpistemicMap
python phases/phase_e/compound_demo.py                # Step 4: human-injected evidence → v2 map + diff
```

The Phase 10 reasoning benchmark (clean/poisoned reasoning items + machine-checkable keys) is the build proposed by this submission and is not yet in the repository.

---

## What we're claiming

1. Deterministic, validated: under adversarially poisoned input, flat multi-agent topology amplifies the wrong framing and can collapse to no output, while chain topology independently rejects it. Binary ground truth, no LLM judge (Phase 3, N=200).
2. The mechanism is a conformity cascade, not psychometrics; it's the agentic analog of human conformity/sycophancy. This is the one piece of the human-psychology hypothesis that transferred; the trait-profile piece was falsified and is not claimed.
3. Proposed, falsifiable: the topology-to-poison-resistance result generalizes from code to reasoning, measurable deterministically via poison-rejection rate across statistical, empirical-consensus, and logical question classes.
4. Applied, honestly bounded: the same architecture, run with an anti-decisive epistemic synthesis prompt, produces structured EpistemicMap artifacts on contested cases. Their form is human-auditable even where their content cannot be scored. We exhibit the artifact; we don't self-grade it.

Claims 1 and 2 are the shield: evidence in hand. Claims 3 and 4 are the sword: what this submission asks for feedback on. The artifact-generating architecture (Claim 4) already exists in the repository; what is unrun is the deterministic reasoning benchmark (Claim 3).

---

*Contact: aryan199841@gmail.com*
*Repository: https://github.com/aryanvnit-maker/agent-psychometry-simulations*
