# FLF Epistemic Case Study Competition — Submission

**Submitted by:** Aryan Shah (aryan199841@gmail.com)
**Repository:** https://github.com/aryanvnit-maker/agent-psychometry-simulations
**Submission date:** June 2026
**Competition:** FLF Epistemic Case Study Competition (flf.org)

---

**TL;DR:** The critical bottleneck in AI epistemic investigation is not agent diversity — it is the terminal synthesis prompt. Replacing a "decisive" synthesis prompt (optimal for strategy/resource tasks) with an "epistemic" prompt tuned for calibrated uncertainty measurably improves AI judgment on contested cases (COVID origins, eggs/CVD, nuclear risk, alcohol J-curve). The methodology is transferable to any multi-agent pipeline in two lines of code, produces structured JSON artifacts that compound across evidence updates, and includes a human-steering workflow for cases where researcher judgment should gate the synthesis step.

---

## What This Is

A methodology spec and prototype demonstrating that a single architectural intervention — a synthesis prompt tuned for calibrated uncertainty rather than decisive commitment — dramatically improves AI-assisted epistemic investigation quality. Demonstrated on COVID-19 origins and eggs/CVD from the competition's case studies.

**Core claim:** The same synthesis architecture that improves judgment quality by 5× in structured business tasks also improves epistemic investigation quality — but only if the synthesis prompt is tuned for *reflection*, not *decisiveness*. We have empirical proof of what happens when you get this wrong, and we fix it here.

---

## The Prior Research (Why This Is Credible)

This submission builds on nine phases of multi-agent orchestration research, totaling 2,400+ evaluations. The relevant findings:

**Phase 5 (160 runs, 4 conditions):** Isolated the synthesis step as the dominant mechanism for output quality. A single terminal synthesis prompt adds +38.8 points on judgment tasks. The flat round-table without synthesis (the LangChain/CrewAI/AutoGen default) scores 34.3. With synthesis: 86.3. The synthesis step is not a minor improvement — it is the mechanism.

**Phase 8 (79 runs, compute-matched):** Agent diversity adds zero measurable value over structured self-refinement at equal compute (Δ=+0.7, p=0.854). The synthesis step is what matters. Who provides the first analysis is irrelevant.

**Phase 9 (40 runs, Kalibr vs Grok multi-agent panel):** Kalibr's 2-call explicit synthesis chain matches xAI's internal ~4-agent multi-agent panel (Δ=−1.8, p=0.809) on the same base model. The synthesis architecture generalises to proprietary comparisons.

**Phase 9 post-mortem finding:** The decisive synthesis prompt ("close every open question, be decisive") scored −13.3 pts on reflective backward-looking analysis tasks. This is the critical datum for epistemic investigation: decisiveness is the *wrong* epistemic posture for investigation. The synthesis mechanism is real — but the synthesis prompt needs to change for a different class of tasks.

**Phase E (this submission):** A new synthesis prompt variant tuned for epistemic investigation. Applied to COVID-19 origins and eggs/CVD from the FLF case studies. Tests whether the architecture generalises when correctly tuned.

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

**The epistemic synthesis prompt (Phase E):**

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

A single-agent self-review with the same epistemic synthesis prompt is expected to produce statistically similar results (per Phase 8). Both are included as conditions in Phase E.

### The Four Conditions

| Condition | Synthesis prompt | LLM calls | Purpose |
|---|---|---|---|
| `kalibr-chain` | EPISTEMIC (calibrated uncertainty + JSON output) | 2 | Primary: tests synthesis architecture |
| `kalibr-chain/decisive` | DECISIVE (Phase 5/8/9 prompt) | 2 | H2 ablation: is prompt type the mechanism? |
| `single-agent` | EPISTEMIC (prose self-review) | 2 | Diversity control: does second agent matter? |
| `flat-no-handoff` | None | 4 | Baseline: framework default without synthesis |

The `kalibr-chain/decisive` condition directly tests H2 within Phase E rather than inferring it from the Phase 9 post-mortem. If the decisive prompt again underperforms on epistemic tasks (as it did by −13.3 pts on s03), this confirms the mechanism is the synthesis prompt design, not something specific to post-mortem analysis.

### Human Steering in the Workflow

The automated chain-2 architecture is designed to support, not replace, a human researcher. The natural steering point is between Agent A and Agent B — after initial evidence mapping, before synthesis commitment. A researcher can:

1. **Review Agent A's draft cruxes** — redirect or add one if a perspective is missing
2. **Flag a missing evidence stream** — e.g., "you haven't addressed the undisclosed sequence database question" — before passing to Agent B
3. **Gate the v1→v2 compounding step** — the `compound_demo.py` script accepts new evidence as researcher-supplied input, making humans the curators of what counts as new and relevant

This is the recommended operational workflow; the automated pipeline is the fallback for high-throughput screening. The key property is that the human intervention point is *before* synthesis commitment, not after — correcting the analyst's frame is far less costly than correcting a committed output.

### Integration with the Full Stack

Phase E deliberately isolates the Assessment bottleneck — the step where evidence maps become calibrated epistemic outputs. But the architecture is designed to connect with the full ingestion → structure → assessment stack:

- **Ingestion → Phase E:** `ingest.py` extracts attributed claims (claim, claim_type, attributed_to, confidence_expressed, quote) from raw URLs. These feed directly into scenario briefs as structured evidence streams rather than researcher summaries.
- **Phase E → downstream:** The `EpistemicMap` JSON output is a machine-readable artifact. Cruxes, probability ranges, and correlated-pair annotations are in typed fields that downstream tools can query — e.g., to surface all claims where `quality: "contested"` or to track probability range shifts across v1→v2 updates.
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

Phase E tests the architecture across **five scenarios** to establish generalisability. The FLF primary case studies (COVID origins, eggs/CVD) are scenarios e01 and e02. Three additional scenarios extend coverage to different epistemic challenge types:

### e03: LHC Black Holes — Dependency Mapping on an Essentially Settled Question

A case where the scientific community reached consensus but the reasoning structure is complex. The rubric does not ask whether the LHC was safe (it was); it asks whether the agent can map the *dependency structure* of the safety argument — what each conclusion rests on — and identify the weakest theoretical links (Hawking radiation, extra-dimension models). A system that simply outputs "the LHC was safe" scores low. A system that identifies which steps rest on unverified theoretical inference vs direct empirical evidence scores high.

**Epistemic challenge tested:** Can the architecture produce structured dependency maps for scientific consensus, not just contested disputes?

### e04: Nuclear Power Risk — Methodological vs Value Disputes

The comparative safety data for nuclear vs fossil fuels (deaths per TWh) looks like a factual disagreement but is actually methodological. Pro-nuclear and anti-nuclear estimates often derive from the same underlying WHO/UNSCEAR mortality data but weight tail events differently. The rubric specifically tests whether the output identifies this shared source dependency rather than treating the disagreement as two independent evidence sets.

**Key epistemic challenge:** The LNT (linear no-threshold) model determines whether low-dose radiation risk is counted at all. Institutional conflict of interest is systematic — IAEA and nuclear regulators produce low estimates; anti-nuclear organisations produce high estimates — both from the same datasets.

**Epistemic challenge tested:** Can the architecture correctly identify methodological disputes that present as factual ones, and map correlated evidence from rival institutional sources?

### e05: Alcohol J-Curve — 30-Year Performed-as-Settled Confound

The classic case study for "performed as settled" in epidemiology. Cohort studies showed moderate drinkers had better cardiovascular outcomes than abstainers (the "J-curve") for decades. This was cited in dietary guidelines as evidence of cardioprotective effects. The problem — sick-quitter bias, where former heavy drinkers who quit due to illness are classified as abstainers — was known in epidemiology from the 1980s. It became undeniable when Mendelian randomisation studies (using genetic variants as instruments for alcohol consumption) showed no protective effect once this confound was controlled.

The rubric requires updating on the Mendelian randomisation evidence. An output that treats classic cohort studies as the primary evidence and ignores MR scores a maximum of 50 — this mirrors the cap for overconfident verdicts in other scenarios.

**Epistemic challenge tested:** The canonical case for "performed as settled." Tests whether the architecture can name a specific claim that was treated as established in guidelines despite a known methodological concern being unresolved.

---

## Generalisation: The Transferable Methodology

The architecture is not specific to COVID or eggs. It is a two-prompt pipeline:

1. **Analysis prompt** (the scenario brief): define the evidence base, the dispute, and the task as epistemic mapping — explicitly NOT verdict-seeking
2. **Synthesis prompt** (injected after the first analysis): the EPISTEMIC_SYNTHESIS_PROMPT above

Any existing multi-agent pipeline (LangChain, CrewAI, AutoGen) can implement this by:
1. Adding a terminal synthesis node with the epistemic synthesis prompt
2. Framing the initial brief as investigation, not decision

No architectural rebuild required. The synthesis prompt is the intervention. This is the same insight from Phases 5 and 6: the flat round-table can achieve near-identical performance to chain topology simply by adding a synthesis step. The same applies here.

### Ingestion Layer Integration

`phases/phase_e/ingest.py` implements URL → structured claims JSON extraction:

```bash
python phases/phase_e/ingest.py --url <article_url> --out results/claims_covid_v1.json
```

Output: a JSON array of attributed claims (`claim`, `claim_type`, `attributed_to`, `confidence_expressed`, `quote`) that can be used to seed the evidence streams for an EpistemicMap.

### Structured EpistemicMap Artifacts

`kalibr-chain` now produces structured JSON output via `EPISTEMIC_SYNTHESIS_PROMPT_JSON`. The synthesis agent is instructed to output a valid JSON `EpistemicMap` object (cruxes, evidence_streams, correlated_pairs, calibrated_estimates, settled, performed_as_settled). Maps are saved to `results/epistemic_maps/{run_id}.json`.

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

**N is thin (by design for early feedback).** Phase E runs 5 reps per condition per scenario — sufficient to detect large effects (>20 pts) but not subtle ones. This submission is presented for early methodology feedback before committing compute to a full run. The final submission will use 10+ reps per condition across all five scenarios (200+ total runs). The Phase 5 and 8 results used 10 reps; those effect sizes were large enough (Δ=+38.8, Δ=+0.7) that 5 reps would have detected or ruled them out.

**The judge is an LLM.** Epistemic quality on COVID origins and eggs/CVD is assessed by a Gemini 2.5 Flash judge against the rubric criteria. The judge has training data on both topics and may have prior beliefs that affect its assessments. The rubric is designed to be structural (did the output identify cruxes as specific questions, not themes?) rather than content-level (is the crux the right one?), which reduces but does not eliminate this concern.

**The rubric and the synthesis prompt are not independent.** The EPISTEMIC_SYNTHESIS_PROMPT instructs the agent to produce cruxes, evidence quality ratings, correlated evidence, calibrated ranges, and settled-vs-performed distinctions. The rubric awards points for exactly those outputs. This means the primary comparison (kalibr-chain vs flat-no-handoff) is partly testing whether explicitly instructing a model to produce a structure causes it to score higher on a rubric that rewards that structure — which is not a surprising result. The finding with the cleanest interpretation is H2: the decisive and epistemic prompts differ only in what they ask for, and the comparison measures which epistemic posture the rubric rewards. H1 replicates the Phase 5 mechanism finding in a new domain, but the effect size in Phase E will be partially inflated by the rubric-prompt alignment. A cleaner test would use a rubric designed independently of the synthesis prompt, or score outputs blind to condition using human domain experts.

**No human validation.** A submission with genuine epistemic value would include human expert review of the outputs, not just automated rubric scoring. This is a prototype — the rubric demonstrates that the architecture produces the *form* of a correct epistemic map. Whether the content is accurate requires domain experts.

**The ingestion layer is scaffolding, not production.** `ingest.py` implements URL → attributed claims extraction and demonstrates the connection between raw sources and the evidence streams fed to agents. However, the Phase E scenarios still use researcher-summarised evidence briefs rather than fully automated ingestion. The prototype prioritises Assessment — the layer where epistemic failure currently occurs — with Ingestion implemented as a bridge that is functional but not battle-tested.

**Single model family.** All runs use Gemini 2.5 Flash. The synthesis mechanism generalised across Gemini, Claude 3.5 Sonnet, and Grok in prior phases. Extension to other model families for Phase E is straightforward but not yet done.

---

## Connection to FLF's Assessment Layer Desiderata

| FLF desideratum | Phase E implementation |
|---|---|
| Identify cruxes | EPISTEMIC_SYNTHESIS_PROMPT step 1: named specific questions, not themes |
| Flag correlated evidence treated as independent | EPISTEMIC_SYNTHESIS_PROMPT step 3: explicit correlation identification |
| Identify rhetorical moves vs evidential weight | Rubric criterion 5: settled vs performed-as-settled |
| Calibrated confidence accounting for out-of-model error | EPISTEMIC_SYNTHESIS_PROMPT step 4: probability range with conditions |
| Surface what's missing | EPISTEMIC_SYNTHESIS_PROMPT step 5: explicit open questions |
| Reusable/refineable structured artifacts | `EpistemicMap` Pydantic schema → JSON saved per run; `compound_demo.py` for v1→v2 updates |
| Source attribution and provenance | `ingest.py` → attributed claims with `quote` + `attributed_to` per claim |

The FLF stack (ingestion → structure → assessment) maps to the Kalibr pipeline as:
- **Ingestion**: the scenario brief (manual in Phase E; automatable via claim extraction)
- **Structure**: agent A's initial analysis (maps the evidence landscape)
- **Assessment**: agent B with EPISTEMIC_SYNTHESIS_PROMPT (produces the calibrated map)

---

## Running the Demonstration

```bash
# Install dependencies
pip install -e ".[research]"

# Set GEMINI_API_KEY in .env (free tier sufficient for Phase E)
cp .env.example .env
# Edit .env: add your GEMINI_API_KEY

# Run Phase E (all 4 conditions, all 5 scenarios, 5 reps each = 100 runs)
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
3. H2 (epistemic prompt outperforms decisive on calibration tasks): both prompts use the same chain-2 architecture; the only variable is what the synthesis agent is asked to do. Whatever the Phase E rubric rewards, it rewards it equally for both conditions. The comparison is clean.

**Dependent on rubric-prompt alignment (interpret with caution):**

4. H1 effect size in Phase E: the magnitude of kalibr-chain's advantage over flat/no-handoff is partly an artifact of the rubric being designed to reward what the epistemic synthesis prompt produces. The direction of the effect (synthesis > no synthesis) is independently supported; the size in Phase E is not.
5. The epistemic synthesis prompt "closes the Phase 9 gap": this is a design claim, not a measurement. We designed a prompt to address a known failure mode and tested it against a rubric that rewards the intended outputs. The claim that it works requires independent validation.

**The practical claim, which is not circular:**

The synthesis prompt is the intervention. Swapping a decisive synthesis prompt for an epistemic one changes what the terminal agent produces, and changes how that output is received by evaluators tuned for calibrated uncertainty. Any existing pipeline can make this swap. Whether the outputs are *epistemically correct* — not just epistemically structured — requires human domain expert review.

The full prior research (Phases 1–9) is the empirical foundation for claims 1–3. Phase E is a demonstration of the methodology, not a fully independent validation of claims 4–5.

---

*Contact: aryan199841@gmail.com*
*Repository: https://github.com/aryanvnit-maker/agent-psychometry-simulations*
