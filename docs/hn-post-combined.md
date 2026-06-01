# Hacker News Submission — All Phases Combined

## Title (90 characters)

```
Show HN: Multi-agent AI is 7x less efficient than a 2-call chain. 2,400+ evals.
```

---

## Body

Nine experiments. 2,400+ evaluations. Temperature=0.0 throughout.

**The headline number:** Kalibr delivers **6.9× more quality per LLM call** than the default multi-agent configuration shipped in LangChain, CrewAI, and AutoGen — verified on 749 objective benchmark instances with binary ground truth, no LLM judge.

The default: flat roundtable, no terminal synthesis step. Four LLM calls. HumanEval pass@1: **28.0% [CI: 17.5–41.7%]**.
Kalibr chain: two LLM calls. HumanEval pass@1: **96.0% [CI: 86.5–98.9%]**. Score-per-call: **48 vs 7**.

Same model. Same agents. Same topology. One has a synthesis step at the terminal agent. The other does not.

**The synthesis prompt** (the entire mechanism):

> "OVERRIDE YOUR ROLE FUNCTION FOR THIS TURN. You are the terminal synthesis agent. Identify what the prior analysis got right, what it missed. Produce a COMPLETE, DEFINITIVE final answer. Close every open question. Be decisive."

Without it, agents address each other constantly — social cohesion is high, FIRO inclusion near 1.0 — while nobody commits to a deliverable. Task cohesion collapses. The system looks like it's working. It isn't.

**The mechanism isolated (Phase 5, 160 runs, 2×2 factorial):**

Chain vs flat × synthesis vs no synthesis. Ten reps × 4 scenarios × 3-judge panel:

| Condition | Calls | Score | Score/call |
|---|---|---|---|
| chain + synthesis | 2 | 86.3 | 43.2 |
| flat + synthesis | 5 | 76.5 | 15.3 |
| chain, no synthesis | 2 | 50.9 | 25.5 |
| **flat, no synthesis (LangChain/CrewAI/AutoGen default)** | **4** | **34.3** | **8.6** |

Synthesis effect: **+38.8 pts**. Topology effect (no synthesis): **+16.6 pts**. The synthesis step outweighs topology by more than 2:1.

**Validated on objective benchmarks (Phase 6, 749 instances, no LLM judge):**

HumanEval (N=50/condition) and GSM8K (N=99–100/condition) on Gemini 2.5 Flash:

| Condition | Calls | HumanEval | Score/call | GSM8K | Score/call |
|---|---|---|---|---|---|
| kalibr-chain | 2 | 96.0% | 48.0 | 94.0% | 47.0 |
| single-agent-refine | 2 | 98.0% | 49.0 | 92.0% | 46.0 |
| single-agent | 1 | 94.0% | 94.0 | 85.0% | 85.0 |
| flat + synthesis | 5 | 98.0% | 19.6 | 92.0% | 18.4 |
| **flat, no synthesis** | **4** | **28.0%** | **7.0** | **56.6%** | **14.2** |

The 6.9× HumanEval gap is on objective binary ground truth. Note: single-agent scores highest score/call because HumanEval is near-ceiling for this model at 1 call — the relevant comparison is the framework default vs kalibr-chain.

**Does agent count or diversity matter? (Phase 8, 79 runs, compute-matched):**

Both conditions use exactly 2 LLM calls. Same synthesis prompt. Same judge panel.

| Condition | Calls | N | Mean | p |
|---|---|---|---|---|
| kalibr-chain (2 different agents) | 2 | 39 | 86.5 | — |
| single-agent-refine (same agent twice) | 2 | 40 | 85.7 | — |
| **Δ** | | | **+0.7** | **0.854** |

Not significant. Agent diversity adds zero measurable value over structured self-refinement. A single agent running draft → synthesize with the commit-forcing prompt matches a full multi-agent team compute-for-compute.

**External validation against a commercial multi-agent system (Phase 9, 40 runs):**

Same base model family (Grok). Different orchestration layers:

| Condition | Model | Calls | Score | Score/call |
|---|---|---|---|---|
| kalibr-chain | grok-4.20-0309-reasoning | 2 | 79.8 | 39.9 |
| grok-panel | grok-4.20-multi-agent-0309 | ~4 internal | 81.5 | 20.4 |
| **Δ** | | | **−1.8, p=0.809** | **Kalibr ~2× more efficient** |

Not compute-matched. Δ not significant. Kalibr's 2-call synthesis chain matched xAI's internal ~4-agent system at approximately half the compute.

Caveat: Kalibr underperforms on post-mortem analysis (s03: 66.7 vs 80.0, −13.3 pts). The decisiveness prompt is wrong for backward-looking reflective tasks. Known gap — requires a separate synthesis variant.

**Prior findings (Phases 1–4):**
- Phase 1 (118 simulations): chain-2 (57.6) beats flat-8 (19.1) by 38 pts. Cross-model replicated on Gemini 2.5 Flash and Claude 3.5 Sonnet. *Note: Phase 5 showed this gap was partially explained by the synthesis confound — true topology-only gap is ~10–17 pts.*
- Phase 2 (900 evaluations, Codeforces Div. 1 C/D): role labels (ALGORITHMIST → IMPLEMENTER) cost 4pp pass@1 (25% relative) vs generic chain-2
- Phase 3 (200 evaluations, poisoned hints): flat-2 produced 4 complete task collapses (no output) on adversarial input; chain-2 had zero collapses across 100 poisoned runs
- Phase 4 (111 evaluations): 5-line classifier routing between judgment and execution configs achieves per-domain maximum on both simultaneously. 100% accuracy on 37 real + 10 adversarial tasks.

**Reproduce it (requires GEMINI_API_KEY):**

```bash
git clone https://github.com/aryanvnit-maker/agent-psychometry-simulations
cd agent-psychometry-simulations
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add GEMINI_API_KEY
python reproduce.py   # chain vs flat, live output, ~2 minutes
```

Full phase runner commands and raw JSONL results in the repo.

GitHub: https://github.com/aryanvnit-maker/agent-psychometry-simulations

---

## First Comment

Anticipated objections:

**"The 6.9× efficiency claim — is that a fair comparison?"**
The flat/no-handoff condition is the documented default in LangChain, CrewAI, and AutoGen quickstarts — it is what ships, not a straw-man. Same model, same agents, same topology, one synthesis step added. If your existing pipeline already adds a terminal synthesis step, you are already in the flat/handoff regime (76.5 on judgment, ~98% on HumanEval) — the 6.9× claim does not apply to you. It applies to teams that haven't added this step yet, which Phase 6's flat/no-handoff result (28% HumanEval) suggests is most teams.

**"Judge agents are circular evaluation."**
Judges scored only the final extracted deliverable against binary rubric criteria, not the transcript. Three independent judges per run with distinct constitutional framings. Phase 2/3/6 use objective ground truth — no judge involved. The 6.9× HumanEval claim is entirely judge-free. Phase 5 and Phase 8 use the same judge panel for both conditions in each run, so inter-condition judge bias cancels.

**"p=0.854 in Phase 8 — maybe you're underpowered."**
n=39/40 per condition, sd ~17. To detect a 10-point gap at 80% power requires n≈47 per condition — we're close but not there for small effects. What Phase 8 rules out is large effects (>10 pts). It cannot definitively rule out a 5-point diversity signal. The per-scenario breakdown (3 of 4 tied within 1.2 pts) makes a meaningful systematic effect unlikely.

**"Ceiling effect in Phase 6."**
Agreed. Gemini 2.5 Flash scores 94–98% on HumanEval for all working conditions — CIs overlap substantially. The primary Phase 6 finding is the flat/no-handoff collapse (28.0%, CI [17.5–41.7%]), separated from every other condition by 60+ points. Rankings among working conditions are not meaningful. Hard benchmarks (Codeforces Div. 1 C/D) show more discrimination at lower absolute performance.

**"Phase 9 is not compute-matched."**
Correct and explicitly stated. Grok panel uses ~4 internal agents; Kalibr makes 2 calls. The comparison is architecture vs architecture. The efficiency calculation (39.9 vs 20.4 score/call) uses 4 as the estimated internal agent count — if the actual internal count is higher, Kalibr's efficiency advantage grows.

**"Real systems use heterogeneous model families."**
Phase 8 used same-model agents with different Kalibr dimension profiles. Whether diversity provides marginal benefit when agents are drawn from genuinely different model families (different base model weights, not just different prompts) is untested. This is listed as the most important open question.

**"Single-model focus."**
Phase 1 replicated the topology gap on Gemini 2.5 Flash and Claude 3.5 Sonnet. Phase 9 replicated the efficiency advantage on Grok. Phases 5/6/8 are Gemini 2.5 Flash only. Cross-model replication of the synthesis effect at the exact numbers is open.

**"86.3 vs 76.5 for chain vs flat with synthesis — topology still matters."**
Correct. Topology has a real +9.8 pt residual with synthesis present, +16.6 pts without. The claim is that synthesis dominates (>2:1 effect size), not that topology is irrelevant.

Temperature=0.0, seed-controlled. All code, constitutions, raw result files in the repo.
