# Hacker News Submission — All Phases Combined

## Title (89 characters)

```
Show HN: 2,400+ evals — the multi-agent performance gap is one prompt. Here's the proof.
```

---

## Body

Nine experiments, 2,400+ evaluations, temperature=0.0 throughout.

The core finding started as "chain topology beats flat by 46 points" (Phase 1, 118 simulations, cross-model replicated on Gemini 2.5 Flash and Claude 3.5 Sonnet). Four follow-on experiments later, we know the 46-point gap was almost entirely caused by a single synthesis prompt embedded in the chain handoff — not the topology itself.

**The mechanism (Phase 5, 160 runs, 2×2 factorial):**

We ran chain vs flat, each with and without an explicit synthesis instruction at the terminal step. Results:

| Condition | Mean score |
|---|---|
| chain/handoff | 86.3 |
| flat/handoff | 76.5 |
| chain/no-handoff | 50.9 |
| flat/no-handoff | 34.3 |

Handoff effect: **+38.8 pts**. Topology effect (no handoff): **+16.6 pts**. The synthesis step is the dominant variable by more than 2:1. The industry default (flat/no-handoff) sits at 34.3. Adding a synthesis step to flat topology takes it to 76.5. Adding it to chain takes it to 86.3.

**The synthesis prompt** overrides role function constraints, demands identification of gaps in prior analysis, and requires a committed final answer. Without it, agents with oversight or evaluation roles suppress primary output delivery.

**Does agent count matter? Phase 8 (79 runs, compute-matched):**

Chain-2 (two agents, 2 API calls) vs single-agent-refine (one agent, 2 API calls, self-synthesis). Same synthesis prompt. Same judge panel.

- kalibr-chain: 86.5 (n=39)
- single-agent-refine: 85.7 (n=40)
- **Δ = +0.7, p = 0.854**

Not significant. A single agent running draft → synthesize matches a diverse multi-agent team compute-for-compute. Agent diversity adds zero measurable value over structured self-refinement.

**Objective validation (Phase 6, ~750 benchmark instances):**

HumanEval and GSM8K on Gemini 2.5 Flash. All conditions with a synthesis step cluster at 94–98% and 85–92%. Flat/no-handoff (no synthesis, role constitution conflict): **~28% HumanEval, ~57% GSM8K**. Same agents, same topology, synthesis override removed. Complete performance collapse.

**Prior findings (Phases 2–4):**
- Role labels degrade execution: ALGORITHMIST → IMPLEMENTER costs 4pp pass@1 vs generic chain-2
- Flat topology collapses under adversarial input: 4 complete NoCode failures on poisoned flat-2 vs 0 across 100 poisoned chain-2 runs
- Mixed workloads: a 5-line task classifier routing between two configs achieves per-domain maximum on both judgment and execution simultaneously

**The actionable summary:**

1. Add a synthesis step before anything else. One agent, 2 calls, commit-forcing prompt: this closes 85% of the gap between broken and optimal multi-agent.
2. Do not add agents to improve quality. Phase 8 proves this directly.
3. Flat topology under adversarial or ambiguous input is a safety issue, not just a performance one.

Full write-up with all results, mechanisms, and limitations: [`docs/lesswrong-post-combined.md`]
GitHub (code, constitutions, raw results): [GitHub URL]

---

## First Comment

Anticipated objections:

**"Judge agents are circular evaluation."** Judges scored only the final extracted deliverable against binary rubric criteria, not the transcript. Three independent judges per run with distinct constitutional framings (strict/balanced/charitable). Phase 2/3/6 use objective ground truth — no judge involved. The Phase 5 and Phase 8 findings use the same judge panel for both conditions in each run, so inter-condition bias cancels.

**"86.3 vs 76.5 for chain vs flat with handoff — that's still a meaningful topology gap."** Correct. Topology is not irrelevant — it has a real +9.8 pt residual effect with synthesis, and +16.6 pts without. The claim is that synthesis dominates (>2:1 effect size). The Phase 1 claim ("topology determines everything") was partially revised by Phase 5. We're reporting the self-correction.

**"p=0.854 in Phase 8 — maybe you're underpowered."** n=39/40 per condition with sd ~17. To detect a 10-point gap at 80% power requires n≈47 per condition. We're close but not there for small effects. What Phase 8 rules out is large effects (>10 pts). It cannot definitively rule out a 5-point diversity signal. The per-scenario breakdown (3 of 4 tied at <1.2 pts) makes a meaningful systematic effect unlikely.

**"Ceiling effect in Phase 6."** Agreed. Gemini 2.5 Flash scores 94–98% on HumanEval — there is no room to discriminate. Phase 6's primary finding is the flat/no-handoff collapse (~28%), not relative rankings among working configurations. Hard benchmarks (Phase 2, Codeforces Div. 1 C/D) show more discrimination at lower absolute performance.

**"Real systems use heterogeneous model families."** Phase 8 used same-model agents with different Kalibr dimension profiles. If agent A and agent B are genuinely different model families, the diversity null result may not hold — their training distributions differ in ways that prompt-based constitutions cannot replicate. This is listed as the most important open question.

**"118 Phase 1 runs is thin."** Agreed. Phase B (code review replication) and Phase 5 (160 runs, 2×2 factorial) provide the replication. The topology direction is robust; the original 46-point magnitude was partially confounded by the synthesis prompt and should be read as "synthesis + topology" rather than "topology alone."

Temperature=0.0, seed-controlled, fully deterministic. All code, constitutions, datasets, and raw result files in the repo.
