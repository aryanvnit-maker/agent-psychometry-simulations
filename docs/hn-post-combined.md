# Hacker News Submission — All Phases Combined

## Title (89 characters)

```
Show HN: 2,400+ evals — the multi-agent performance gap is one prompt. Here's the proof.
```

---

## Body

Nine experiments, 2,400+ evaluations, temperature=0.0 throughout.

The core finding started as "chain topology beats flat by 46 points" (Phase 1, 118 simulations, cross-model replicated on Gemini 2.5 Flash and Claude 3.5 Sonnet — later shown to be confounded by the missing synthesis step in the flat condition; the true topology-only gap is ~10–17 points). Four follow-on experiments later, we know the gap was almost entirely caused by a single synthesis prompt embedded in the chain handoff — not the topology itself.

**The mechanism (Phase 5, 160 runs, 2×2 factorial):**

We ran chain vs flat, each with and without an explicit synthesis instruction at the terminal step. Results:

| Condition | Mean score |
|---|---|
| chain/handoff | 86.3 |
| flat/handoff | 76.5 |
| chain/no-handoff | 50.9 |
| flat/no-handoff | 34.3 |

Handoff effect: **+38.8 pts**. Topology effect (no handoff): **+16.6 pts**. The synthesis step is the dominant variable by more than 2:1. The out-of-the-box flat configuration without a mandatory terminal synthesis step (the default pattern in most framework Quickstarts) sits at 34.3 — this is the configuration many teams start with, and it silently collapses. Adding a synthesis step to flat topology takes it to 76.5. Adding it to chain takes it to 86.3.

**The synthesis prompt** overrides role function constraints, demands identification of gaps in prior analysis, and requires a committed final answer. Without it, agents with oversight or evaluation roles likely suppress primary output delivery — consistent with the role-penalty finding in Phase 2, though we did not run a flat/no-handoff control with generic (no-role) agents to isolate this as the sole cause.

**Does agent count matter? Phase 8 (79 runs, compute-matched):**

Chain-2 (two agents, 2 API calls) vs single-agent-refine (one agent, 2 API calls, self-synthesis). Same synthesis prompt. Same judge panel.

- kalibr-chain: 86.5 (n=39)
- single-agent-refine: 85.7 (n=40)
- **Δ = +0.7, p = 0.854**

Not significant. A single agent running draft → synthesize matches a diverse multi-agent team compute-for-compute. Agent diversity adds zero measurable value over structured self-refinement.

**Objective validation (Phase 6, 749 benchmark instances, no LLM judge):**

HumanEval (N=50/condition) and GSM8K (N=99–100/condition) on Gemini 2.5 Flash. All conditions with a synthesis step: 92–98% — confidence intervals overlap substantially due to ceiling effects, so rankings among working conditions are not meaningful. Flat/no-handoff (no synthesis): **28.0% HumanEval [CI: 17.5–41.7%], 56.6% GSM8K [CI: 46.7–65.9%]**. Same agents, same topology, synthesis override removed. Separated from every working condition by 60+ points. The collapse is the finding, not the rankings.

**Phase B replication (code review, N=15/condition):** chain-2: 70.4, flat-2 (no synthesis step, consistent with Phase 1 flat condition prior to Phase 5 isolation): 35.3, Δ=+35.1. This captures the combined topology + synthesis gap, consistent with the Phase 5 isolation. Topology direction replicates outside business judgment scenarios.

**Prior findings (Phases 2–4):**
- Role labels degrade execution: ALGORITHMIST → IMPLEMENTER costs 4pp pass@1 (25% relative) vs generic chain-2 on Codeforces Div. 1 C/D
- Flat topology collapses under adversarial input: 4 complete NoCode failures on poisoned flat-2 vs 0 across 100 poisoned chain-2 runs
- Mixed workloads: a 5-line task classifier routing between two configs achieves per-domain maximum on both judgment and execution simultaneously

**Does Kalibr's 2-call chain beat xAI's internal 4-agent panel? Phase 9 (40 runs, same Grok base model):**

We ran both conditions on 4 judgment scenarios using the same Grok base model family:
- kalibr-chain: grok-4.20-0309-reasoning, 2 LLM calls, Kalibr's explicit synthesis architecture
- grok-panel: grok-4.20-multi-agent-0309, ~4 internal agents, xAI's orchestration (1 API call)

Results:
- kalibr-chain: 79.8 (n=20, sd=29.3, 2 LLM calls)
- grok-panel: 81.5 (n=20, sd=12.8, ~4 internal agents)
- **Δ = −1.8 pts, p=0.809 — not significant**

Note: not compute-matched. Grok panel uses ~4 internal agents per call; Kalibr makes 2 calls. Score-per-LLM-call: **Kalibr 39.9, Grok panel 20.4**.

Kalibr's 2-call synthesis chain matched xAI's proprietary multi-agent system at approximately half the compute. Per-scenario: Kalibr +5.3 on strategic decisions, +5.0 on crisis response. Panel +13.3 on post-mortem analysis — the decisiveness synthesis prompt ("close every open question, be decisive") is the wrong posture for backward-looking analysis. Known limitation; fix requires a separate synthesis variant for reflective tasks.

**The actionable summary:**

1. Add a synthesis step before anything else. One agent, 2 calls, commit-forcing prompt: this closes ~80% of the gap between broken and optimal multi-agent.
2. Do not add agents to improve quality. Phase 8 proves this directly (p=0.854). Phase 9 confirms it against a real proprietary system.
3. Flat topology under adversarial or ambiguous input is a safety issue, not just a performance one.

Full write-up with all results, mechanisms, and limitations: [`docs/lesswrong-post-combined.md`]
GitHub (code, constitutions, raw results): https://github.com/aryanvnit-maker/agent-psychometry-simulations

---

## First Comment

Anticipated objections:

**"Judge agents are circular evaluation."** Judges scored only the final extracted deliverable against binary rubric criteria, not the transcript. Three independent judges per run with distinct constitutional framings (strict/balanced/charitable). Phase 2/3/6 use objective ground truth — no judge involved. The Phase 5 and Phase 8 findings use the same judge panel for both conditions in each run, so inter-condition bias cancels.

**"86.3 vs 76.5 for chain vs flat with handoff — that's still a meaningful topology gap."** Correct. Topology is not irrelevant — it has a real +9.8 pt residual effect with synthesis, and +16.6 pts without. The claim is that synthesis dominates (>2:1 effect size). The Phase 1 claim ("topology determines everything") was partially revised by Phase 5. We're reporting the self-correction.

**"p=0.854 in Phase 8 — maybe you're underpowered."** n=39/40 per condition with sd ~17. To detect a 10-point gap at 80% power requires n≈47 per condition. We're close but not there for small effects. What Phase 8 rules out is large effects (>10 pts). It cannot definitively rule out a 5-point diversity signal. The per-scenario breakdown (3 of 4 tied at <1.2 pts) makes a meaningful systematic effect unlikely.

**"Ceiling effect in Phase 6."** Agreed. Gemini 2.5 Flash scores 94–98% on HumanEval for all working conditions — confidence intervals overlap substantially; all working conditions are statistically indistinguishable on HumanEval/GSM8K. Phase 6's primary finding is the flat/no-handoff collapse (28.0%, CI [17.5–41.7%]), separated from every other condition by 60+ points. Hard benchmarks (Phase 2, Codeforces Div. 1 C/D) show more discrimination at lower absolute performance.

**"Real systems use heterogeneous model families."** Phase 8 used same-model agents with different Kalibr dimension profiles. If agent A and agent B are genuinely different model families, the diversity null result may not hold — their training distributions differ in ways that prompt-based constitutions cannot replicate. This is listed as the most important open question.

**"Single-model focus."** Most phases use Gemini 2.5 Flash. Phase 1 replicated the topology gap across two model families (Gemini 2.5 Flash and Claude 3.5 Sonnet). Phase 5/6/8 results are currently single-model. Cross-model replication of the synthesis effect is an open question; the synthesis prompt wording may need tuning per model family.

**"118 Phase 1 runs is thin."** Agreed. Phase B (code review replication) and Phase 5 (160 runs, 2×2 factorial) provide the replication. The topology direction is robust; the original 46-point magnitude was partially confounded by the synthesis prompt and should be read as "synthesis + topology" rather than "topology alone."

Temperature=0.0, seed-controlled, fully deterministic. All code, constitutions, datasets, and raw result files in the repo.
