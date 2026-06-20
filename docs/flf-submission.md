# FLF Epistemic Case Study Competition — Submission

**Submitted by:** Aryan Shah (aryan199841@gmail.com)
**Repository:** https://github.com/aryanvnit-maker/agent-psychometry-simulations
**Submission date:** June 2026
**Competition:** FLF Epistemic Case Study Competition (flf.org)

---

**TL;DR:** The critical bottleneck in AI epistemic investigation is not agent diversity — it is the terminal synthesis prompt. Prior research across 2,400+ evaluations established that a decisive synthesis prompt adds +38.8 pts on judgment tasks but costs −13.3 pts on reflective investigation. This submission presents a methodology and prototype that replaces the decisive prompt with an epistemic variant tuned for calibrated uncertainty, and tests whether that swap closes the gap on contested epistemic cases (COVID origins, eggs/CVD, nuclear risk, alcohol J-curve). Results are pending the full run; this submission is presented for early methodology feedback. The architecture produces structured JSON artifacts that compound across evidence updates and is transferable to any existing multi-agent pipeline.

---

## What This Is

A methodology spec and prototype testing whether a single architectural intervention — replacing a decisive synthesis prompt with one tuned for calibrated uncertainty — improves AI-assisted epistemic investigation quality. Tested on five contested epistemic cases including COVID-19 origins and eggs/CVD from the competition's case studies.

**Core claim:** The same synthesis architecture that improves judgment quality by 2.5× in structured business tasks (34.3 → 86.3 pts, Phase 5) is known to *degrade* performance on reflective investigation tasks when the synthesis prompt demands decisiveness (Phase 9, −13.3 pts). We have empirical evidence of what goes wrong, a prompt variant designed to fix it, and an experiment to test whether the fix works.

---

## The Prior Research (Why This Is Credible)

This submission builds on nine phases of multi-agent orchestration research, totaling 2,400+ evaluations. The relevant findings:

**Phase 5 (160 runs, 4 conditions):** Isolated the synthesis step as the dominant mechanism for output quality. A single terminal synthesis prompt adds +38.8 points on judgment tasks. The flat round-table without synthesis (the LangChain/CrewAI/AutoGen default) scores 34.3. With synthesis: 86.3. The synthesis step is not a minor improvement — it is the mechanism.

**Phase 8 (79 runs, compute-matched):** Agent diversity adds zero measurable value over structured self-refinement at equal compute (Δ=+0.7, p=0.854). The synthesis step is what matters. Who provides the first analysis is irrelevant.

**Phase 9 (40 runs, Kalibr vs Grok multi-agent panel):** Kalibr's 2-call explicit synthesis chain matches xAI's internal ~4-agent multi-agent panel (Δ=−1.8, p=0.809) on the same base model. The synthesis architecture generalises to proprietary comparisons.

**Phase 9 post-mortem finding:** The decisive synthesis prompt ("close every open question, be decisive") scored −13.3 pts on reflective backward-looking analysis tasks. This is the critical datum for epistemic investigation: decisiveness is the *wrong* epistemic posture for investigation. The synthesis mechanism is real — but the synthesis prompt needs to change for a different class of tasks.

**Phase 10 (this submission):** A new synthesis prompt variant tuned for epistemic investigation. Applied to five scenarios — COVID-19 origins, eggs/CVD, LHC black holes, nuclear power risk, and alcohol J-curve — spanning contested disputes, essentially-settled science, and canonical performed-as-settled confounds. Tests whether the architecture generalises when the prompt is correctly tuned for reflection rather than commitment.

---

## The Methodology

### The Problem With Existing AI Investigation Workflows

The default multi-agent configuration in every major framework (LangChain, CrewAI, AutoGen) is a flat round-table: every agent speaks, full conversation history, no forced commitment structure. This configuration reliably fails on judgment and epistemic tasks because:

1. **No forcing function:** the deliberation loop stays open. Agents surface considerations but no structural mechanism converts deliberation into a structured output.
2. **Social cohesion substitutes for task cohesion:** agents engage with each other productively but produce no deliverable. (Measured: geq_social_cohesion 90+, geq_task_cohesion <40 in flat runs.)
3. **Role constitutions suppress output delivery:** agents with evaluation or oversight role functions tend to critique rather than produce.

The synthesis step fixes this by overriding role functions and demanding a structured terminal output. Without it, the system is running but broken — it produces output but the output lacks the structure required for epistemic use.

### The Epistemic Synthesis Prompt

The synthesis prompt used in Phases 5, 8, and 9:

> "OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN. You are the terminal synthesis agent. Identify what the prior analysis got right, what it missed, produce a COMPLETE, DEFINITIVE final answer. Close every open question. Be decisive."

This prompt is tuned for strategy, resource allocation, and crisis response — tasks where commitment is the correct epistemic posture. For investigation tasks, "be decisive" and "close every open question" are structurally wrong. Post-mortem analysis, COVID origins, and egg/CVD evidence require preserving uncertainty, identifying cruxes, and flagging what cannot be resolved.

**The epistemic synthesis prompt (Phase 10):**

> "OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN.
> You are the terminal epistemic synthesis agent.
> Your goal is NOT a confident verdict. Your goal is a calibrated epistemic map.
>
> Produce the following in order:
> 1. CRUXES: The 2-3 specific factual or inferential questions where resolution would most shift the overall probability. Be specific — name the question, not the theme.
> 2. EVIDENCE QUALITY: For each major evidence stream, rate it: strong / weak / contested / missing. Name the specific weakness or strength.
> 3. CORRELATED EVIDENCE: Identify at least one pair of evidence streams that appear independent but share a methodological assumption or source. Explain why this matters.
> 4. CALIBRATED ASSESSMENT: Give a probability range (not a point estimate) with explicit conditions. E.g. '55-70% for hypothesis A, conditional on X being accurately measured.' A range is required.
> 5. SETTLED vs PERFORMED: Distinguish what has actually been resolved from what was merely performed as resolved. State at least one open question the evidence cannot close.
>
> Preserve uncertainty where it is warranted. Do not collapse to false certainty."

The structure of this prompt directly implements three of FLF's assessment layer desiderata:
- *Identify cruxes* → step 1
- *Flag correlated evidence treated as independent* → step 3
- *Distinguish what the debate settled from what it merely performed settling* → step 5

### The Architecture

```
Input (scenario brief + evidence streams)
        │
        ▼
   Agent A (analyst)
   Full constitution from Kalibr psychometric framework
   Task: maps the evidence landscape, identifies key claims and their support
        │
        ▼
   EPISTEMIC_SYNTHESIS_PROMPT injected
        │
        ▼
   Agent B (epistemic synthesiser)
   Same constitutional framework, different agent profile
   Task: produces structured epistemic map per prompt instructions
        │
        ▼
   Output: calibrated epistemic map
```

Two LLM calls. No more.

### Why Two Agents Instead of One?

Phase 8 showed agent diversity adds no statistical benefit over self-refinement (Δ=+0.7, p=0.854). This finding likely holds for epistemic tasks too. The chain-2 architecture is used because:

1. The first agent produces an initial pass without the synthesis constraint — it can explore freely
2. The synthesis prompt is injected between passes, not at the start — this prevents the analyst from pre-committing to a structured format when exploration is more useful
3. Architecturally, the chain structure separates the two epistemic modes (explore vs synthesise) cleanly

A single-agent self-review with the same epistemic synthesis prompt is expected to produce statistically similar results (per Phase 8). Both are included as conditions in Phase 10.

### The Four Conditions

| Condition | Synthesis prompt | LLM calls | Purpose |
|---|---|---|---|
| `kalibr-chain` | EPISTEMIC (calibrated uncertainty + JSON output) | 2 | Primary: tests synthesis architecture |
| `kalibr-chain/decisive` | DECISIVE (Phase 5/8/9 prompt) | 2 | H2 ablation: is prompt type the mechanism? |
| `single-agent` | EPISTEMIC (prose self-review) | 2 | Diversity control: does second agent matter? |
| `flat-no-handoff` | None | 4 | Baseline: framework default without synthesis |

The `kalibr-chain/decisive` condition directly tests H2 within Phase 10 rather than inferring it from the Phase 9 post-mortem. If the decisive prompt again underperforms on epistemic tasks (as it did by −13.3 pts on s03), this confirms the mechanism is the synthesis prompt design, not something specific to post-mortem analysis.

### Human Steering in the Workflow

The automated chain-2 architecture is designed to support, not replace, a human researcher. The natural steering point is between Agent A and Agent B — after initial evidence mapping, before synthesis commitment. A researcher can:

1. **Review Agent A's draft cruxes** — redirect or add one if a perspective is missing
2. **Flag a missing evidence stream** — e.g., "you haven't addressed the undisclosed sequence database question" — before passing to Agent B
3. **Gate the v1→v2 compounding step** — the `compound_demo.py` script accepts new evidence as researcher-supplied input, making humans the curators of what counts as new and relevant

This is the recommended operational workflow; the automated pipeline is the fallback for high-throughput screening. The key property is that the human intervention point is *before* synthesis commitment, not after — correcting the analyst's frame is far less costly than correcting a committed output.

### Integration with the Full Stack

Phase 10 deliberately isolates the Assessment bottleneck — the step where evidence maps become calibrated epistemic outputs. But the architecture is designed to connect with the full ingestion → structure → assessment stack:

- **Ingestion → Phase 10:** `ingest.py` extracts attributed claims (claim, claim_type, attributed_to, confidence_expressed, quote) from raw URLs into a structured JSON file. A researcher uses this output to draft scenario briefs — replacing free-form summarisation with claim-level attribution before the brief is passed to the agents.
- **Phase 10 → downstream:** The `EpistemicMap` JSON output is a machine-readable artifact. Cruxes, probability ranges, and correlated-pair annotations are in typed fields that downstream tools can query — e.g., to surface all claims where `quality: "contested"` or to track probability range shifts across v1→v2 updates.
- **Addressing the nuance-vs-interoperability tension:** The `EpistemicMap` schema pairs structured fields (`range_low`, `range_high`, `quality`) with mandatory free-text fields (`conditions`, `weakness`, `shared_assumption`, `implication`). The structured fields enable machine comparison and compounding; the free-text fields prevent flattening complex arguments into binary states. A crux is not just tagged "unresolved" — it carries the specific question text and a resolution impact rating. A correlated pair names the shared assumption, not just the two streams.

The current prototype weights Assessment heavily, with Ingestion and Structure implemented as lightweight scaffolding. The submission is presented as *solving the Assessment bottleneck to enable the full stack* — the bottleneck where AI systems currently collapse calibrated uncertainty into performed certainty.

---

## Demonstration: COVID-19 Origins

### Scenario Design

The COVID-19 origins scenario presents the key evidence streams from the Rootclaim vs Miller debate (Jan 2024) and asks the agent team to produce an epistemic map, NOT a verdict. The rubric explicitly penalises overconfidence: a team that produces a confident verdict without calibrated uncertainty scores a maximum of 50.

**Evidence streams included:**
1. Geographic clustering around the Huanan Seafood Market
2. Raccoon dog presence at the market
3. The furin cleavage site (absent in close relatives, unusual for natural coronaviruses)
4. WIV proximity and bat coronavirus research
5. Lack of documented progenitor virus in animal populations
6. Timeline of adaptation to human transmission
7. Access restrictions limiting investigation

**Rubric criteria:**
1. Crux identification: 2-3 specific questions (25 pts)
2. Evidence quality: 4+ streams assessed with named weaknesses/strengths (25 pts)
3. Calibration: probability range with explicit conditions (25 pts)
4. Correlated evidence: ≥1 instance identified and explained (15 pts)
5. Epistemic honesty: settled vs performed-as-settled distinguished (10 pts)

### Why This Rubric Is Hard

The 23-orders-of-magnitude spread across six independent Bayesian analyses of the same evidence is the most important datum in this case. It reflects genuine prior disagreement and genuine contested evidence, not analytical error. A system that produces a confident answer is doing something wrong — it is either ignoring the genuine uncertainty or performing resolution rather than achieving it.

The rubric rewards a system that can say: "The geographic clustering evidence is strong but not independent of WIV proximity (both locate outbreak origin at the same site for different reasons). The furin cleavage site is genuinely unusual but absence of evidence is not evidence of absence for natural recombination. Conditional on the WIV not having an undisclosed database of sequences, probability of natural spillover: 60-75%. The crux is the undisclosed sequence database question."

---

## Demonstration: Eggs and Cardiovascular Disease

### Scenario Design

The eggs/CVD scenario presents the same rubric structure on the nutrition evidence base — a prototypically messy, industry-influenced, methodologically contested domain. The rubric penalises dietary recommendations without calibrated uncertainty.

**Evidence streams included:**
1. Harvard Nurses' Health Study / HPFS (large cohort, null association)
2. PREDIMED and similar RCTs (Mediterranean diet, eggs not isolated)
3. Chinese Kadoorie Biobank (N=500k, inverse association)
4. NHANES/MESA cohort analyses (Zhong et al. JAMA 2019, positive association)
5. Mechanistic: dietary cholesterol → LDL-C, variable across individuals
6. Confounding: dietary pattern co-occurrence in Western cohorts
7. Industry funding patterns in egg nutrition research

**Key epistemic challenge:** streams 1, 3, and 4 appear to disagree. A good epistemic map should identify that streams 1 and 3 and 4 all rely on dietary recall instruments with known biases, and that Western cohort confounding (stream 6) could explain the difference between Chinese Kadoorie (stream 3) and NHANES (stream 4) results without either being wrong. The crux is whether controlling for total dietary pattern eliminates the positive association in NHANES — a specific answerable question.

---

## Additional Scenarios (Full Experiment)

Phase 10 tests the architecture across **five scenarios** serving two purposes: generalisability across epistemic challenge types, and adversarial stress-testing of the correlated-evidence detection mechanism. The FLF primary case studies (COVID origins, eggs/CVD) are e01 and e02. Three additional scenarios push on specific failure modes:

### e03: LHC Black Holes — Dependency Mapping on an Essentially Settled Question

A case where the scientific community reached consensus but the reasoning structure is complex. The rubric does not ask whether the LHC was safe (it was); it asks whether the agent can map the *dependency structure* of the safety argument — what each conclusion rests on — and identify the weakest theoretical links (Hawking radiation, extra-dimension models). A system that simply outputs "the LHC was safe" scores low. A system that identifies which steps rest on unverified theoretical inference vs direct empirical evidence scores high.

**Epistemic challenge tested:** Can the architecture produce structured dependency maps for scientific consensus, not just contested disputes?

### e04: Nuclear Power Risk — Institutional Source Adversarialism

This is an adversarial stress test for the correlated evidence detection mechanism. Pro-nuclear and anti-nuclear mortality estimates frequently derive from the *same underlying WHO/UNSCEAR data* but reach opposite conclusions by weighting tail events differently. Both sides cite "the evidence" — but the evidence is the same evidence, processed through opposing methodological commitments.

A system that treats IAEA estimates and Greenpeace estimates as independent evidence streams is being fooled by institutional adversarialism masquerading as independent corroboration. The rubric directly penalises this: citing both sides without identifying the shared source dependency scores zero on the correlated evidence criterion.

**Adversarial robustness tested:** Does the correlated evidence detection step (EPISTEMIC_SYNTHESIS_PROMPT step 3) correctly identify when rival institutional sources are drawing from the same dataset — making them less independent than they appear?

### e05: Alcohol J-Curve — Long-Horizon Performed-as-Settled Adversarialism

A different type of adversarial stress: not competing institutions citing the same data, but a methodological confound (sick-quitter bias) that was known to domain experts for 30+ years yet persisted in public health guidelines and funding-influenced cohort studies. The industry-funded literature and the independent cohort literature appear to disagree on different things — but most streams share the same underlying flaw.

The rubric requires updating on Mendelian randomisation evidence. An output anchored on classic cohort studies without updating for MR is failing to weight evidence correctly — the canonical case of a field performing resolution it has not actually achieved.

**Adversarial robustness tested:** Does the architecture correctly identify that streams 1, 4, and 7 (classic cohorts, industry-funded studies, dietary pattern studies) share the sick-quitter confound — making their apparent independent corroboration an artefact of shared bias rather than genuine convergence?

**Content quality note:** e05 is one of two scenarios (with e03) where a definitively correct crux exists — sick-quitter bias, not generic "confounding." The rubric explicitly checks for this named mechanism, not just structural presence of a crux. For genuinely contested cases (e01 COVID origins, e04 nuclear risk), no ground-truth crux exists; the rubric correctly checks structure only. This asymmetry is intentional: applying content-level scoring to genuinely unresolved disputes would impose false certainty of the exact kind the architecture is designed to resist.

---

## Generalisation: The Transferable Methodology

The architecture is not specific to COVID or eggs. It is a two-prompt pipeline:

1. **Analysis prompt** (the scenario brief): define the evidence base, the dispute, and the task as epistemic mapping — explicitly NOT verdict-seeking
2. **Synthesis prompt** (injected after the first analysis): the EPISTEMIC_SYNTHESIS_PROMPT above

Any existing multi-agent pipeline (LangChain, CrewAI, AutoGen) can implement this by:
1. Adding a terminal synthesis node with the epistemic synthesis prompt
2. Framing the initial brief as investigation, not decision

No architectural rebuild required. The synthesis prompt is the intervention. This is the same insight from Phase 5: the flat round-table can achieve near-identical performance to chain topology simply by adding a synthesis step. The same applies here.

### Compounding: v1 → v2

`phases/phase_e/compound_demo.py` demonstrates the FLF "living document" pattern:

1. Load a v1 `EpistemicMap` produced by `kalibr-chain`
2. Present new evidence (Rootclaim post-debate critique, Weissman Bayesian analysis, Chinese CDC supplementary sampling)
3. Run kalibr-chain with a continuation brief: "given v1 + new evidence, produce v2"
4. Parse v2 — sets `extends_version: 1`, lists changes in `new_evidence`
5. Print human-readable diff: crux status changes, probability range shifts, newly settled claims

This demonstrates that structured epistemic maps are **reusable and extendable** — epistemic work compounds rather than being discarded after each run.

---

## Limitations

**N is thin (by design for early feedback).** Phase 10 runs 5 reps per condition per scenario — sufficient to detect large effects (>20 pts) but not subtle ones. This submission is presented for early methodology feedback before committing compute to a full run. The final submission will use 10+ reps per condition across all five scenarios (200+ total runs). The Phase 5 and 8 results used 10 reps; those effect sizes were large enough (Δ=+38.8, Δ=+0.7) that 5 reps would have detected or ruled them out.

**The judge is an LLM, and the content/structure split is intentional but asymmetric.** Rubric scoring is automated via a Gemini 2.5 Flash judge. For genuinely contested cases (e01, e04) where no ground-truth crux exists, the rubric checks structure: did the output name specific questions rather than themes, give a probability range rather than a point estimate, identify a shared source dependency rather than listing streams as independent? For scenarios with a known correct crux (e03, e05), the rubric checks content: did the output name sick-quitter bias specifically, not just "confounding"? This asymmetry is deliberate — applying content-level scoring to genuinely unresolved disputes would impose false certainty, which is precisely the failure mode the architecture is designed to catch. The remaining limitation is that the judge may have prior beliefs about the contested cases that affect structural scoring; this is bounded but not eliminated by keeping scoring criteria observational.

**The rubric and the synthesis prompt are not independent.** The EPISTEMIC_SYNTHESIS_PROMPT instructs the agent to produce cruxes, evidence quality ratings, correlated evidence, calibrated ranges, and settled-vs-performed distinctions. The rubric awards points for exactly those outputs. This means the primary comparison (kalibr-chain vs flat-no-handoff) is partly testing whether explicitly instructing a model to produce a structure causes it to score higher on a rubric that rewards that structure — which is not a surprising result. The finding with the cleanest interpretation is H2: the decisive and epistemic prompts differ only in what they ask for, and the comparison measures which epistemic posture the rubric rewards. H1 replicates the Phase 5 mechanism finding in a new domain, but the effect size in Phase 10 will be partially inflated by the rubric-prompt alignment. A cleaner test would use a rubric designed independently of the synthesis prompt, or score outputs blind to condition using human domain experts.

**No human validation.** A submission with genuine epistemic value would include human expert review of the outputs, not just automated rubric scoring. This is a prototype — the rubric demonstrates that the architecture produces the *form* of a correct epistemic map. Whether the content is accurate requires domain experts.

**The ingestion layer is scaffolding, not production.** `ingest.py` implements URL → attributed claims extraction and demonstrates the connection between raw sources and the evidence streams fed to agents. However, the Phase 10 scenarios still use researcher-summarised evidence briefs rather than fully automated ingestion. The prototype prioritises Assessment — the layer where epistemic failure currently occurs — with Ingestion implemented as a bridge that is functional but not battle-tested.

**Single model family.** All runs use Gemini 2.5 Flash. The synthesis mechanism generalised across Gemini, Claude 3.5 Sonnet, and Grok in prior phases. Extension to other model families for Phase 10 is straightforward but not yet done.

---

## Connection to FLF's Assessment Layer Desiderata

| FLF desideratum | Phase 10 implementation |
|---|---|
| Identify cruxes | EPISTEMIC_SYNTHESIS_PROMPT step 1: named specific questions, not themes |
| Flag correlated evidence treated as independent | EPISTEMIC_SYNTHESIS_PROMPT step 3: explicit correlation identification |
| Identify rhetorical moves vs evidential weight | Rubric criterion 5: settled vs performed-as-settled |
| Calibrated confidence accounting for out-of-model error | EPISTEMIC_SYNTHESIS_PROMPT step 4: probability range with conditions |
| Surface what's missing | EPISTEMIC_SYNTHESIS_PROMPT step 5: explicit open questions |
| Reusable/refineable structured artifacts | `EpistemicMap` Pydantic schema → JSON saved per run; `compound_demo.py` for v1→v2 updates |
| Source attribution and provenance | `ingest.py` → attributed claims with `quote` + `attributed_to` per claim |
| Adversarial source robustness | e04/e05 scenarios designed around institutional adversarialism and industry-influenced corpora; step 3 forces explicit identification of shared source dependencies before treating streams as independent |

The FLF stack (ingestion → structure → assessment) maps to the Kalibr pipeline as:
- **Ingestion**: the scenario brief (manual in Phase 10; automatable via claim extraction)
- **Structure**: agent A's initial analysis (maps the evidence landscape)
- **Assessment**: agent B with EPISTEMIC_SYNTHESIS_PROMPT (produces the calibrated map)

---

## Running the Demonstration

```bash
# Install dependencies
pip install -e ".[research]"

# Set GEMINI_API_KEY in .env (free tier sufficient for Phase 10)
cp .env.example .env
# Edit .env: add your GEMINI_API_KEY

# Run Phase 10 (all 4 conditions, all 5 scenarios, 5 reps each = 100 runs)
python phases/phase_e/run_phase_e.py

# Or run just COVID and eggs with more reps
python phases/phase_e/run_phase_e.py --reps 10 --scenarios e01 e02

# Or run a single condition
python phases/phase_e/run_phase_e.py --conditions kalibr-chain kalibr-chain/decisive

# Analyze results
python phases/phase_e/analyze_phase_e.py

# Compound demo: v1 → v2 (requires ≥1 kalibr-chain run of e01_covid_origins)
python phases/phase_e/compound_demo.py

# Ingest an article → structured claims JSON
python phases/phase_e/ingest.py --url <article_url> --out results/claims_covid_v1.json
```

Full codebase, agent constitutions, scenarios, and all Phase 1–9 results are in the repository.

---

## What We're Claiming

**Independently supported by prior phases (not circular):**

1. The synthesis step is the primary mechanism for output quality on judgment tasks. This is established across 2,400+ evaluations in Phases 5–9, using rubrics designed before the synthesis prompt existed.
2. Synthesis prompt design is the critical variable — decisive prompts underperform on reflective tasks by a measurable amount (Phase 9, −13.3 pts on s03_post_mortem). This is an empirical result from a rubric that was not designed around the prompt.
3. H2 (epistemic prompt outperforms decisive on calibration tasks): both prompts use the same chain-2 architecture; the only variable is what the synthesis agent is asked to do. Whatever the Phase 10 rubric rewards, it rewards it equally for both conditions. The comparison is clean.

**Dependent on rubric-prompt alignment (interpret with caution):**

4. H1 effect size in Phase 10: the magnitude of kalibr-chain's advantage over flat/no-handoff is partly an artifact of the rubric being designed to reward what the epistemic synthesis prompt produces. The direction of the effect (synthesis > no synthesis) is independently supported; the size in Phase 10 is not.
5. The epistemic synthesis prompt "closes the Phase 9 gap": this is a design claim, not a measurement. We designed a prompt to address a known failure mode and tested it against a rubric that rewards the intended outputs. The claim that it works requires independent validation.

**The practical claim, which is not circular:**

The synthesis prompt is the intervention. Swapping a decisive synthesis prompt for an epistemic one changes what the terminal agent produces, and changes how that output is received by evaluators tuned for calibrated uncertainty. Any existing pipeline can make this swap. Whether the outputs are *epistemically correct* — not just epistemically structured — requires human domain expert review.

The full prior research (Phases 1–9) is the empirical foundation for claims 1–3. Phase 10 is a demonstration of the methodology, not a fully independent validation of claims 4–5.

---

*Contact: aryan199841@gmail.com*
*Repository: https://github.com/aryanvnit-maker/agent-psychometry-simulations*
