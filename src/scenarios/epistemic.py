# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Epistemic investigation scenarios for the FLF Epistemic Case Study Competition.

These scenarios test the same synthesis architecture finding on open epistemic
disputes rather than structured business judgment tasks. The rubrics reward
calibrated uncertainty, crux identification, and evidence quality assessment —
NOT decisive commitment.

This directly tests the Phase 9 post-mortem finding: the decisive synthesis
prompt is the WRONG posture for reflective, backward-looking analysis.
These scenarios use an epistemic synthesis prompt variant tuned for investigation.
"""

from .base import Scenario

# ── e01: COVID-19 Origins ─────────────────────────────────────────────────────
# Epistemic dispute with rich public evidence: the Rootclaim vs Miller debate
# (Jan 2024, $100k judged, 15+ hours of structured argument). Two expert judges
# ruled for zoonosis; six independent Bayesian analyses spanned 23 orders of
# magnitude. A genuine hard case with contested priors and contested evidence.
#
# Rubric: rewards crux identification, calibrated uncertainty, evidence quality
# assessment, and distinguishing settled from performed-as-settled claims.

COVID_ORIGINS = Scenario(
    scenario_id="e01_covid_origins",
    category="evaluation",
    phase="storming",
    brief=(
        "You are an epistemic investigation team. Your task is NOT to reach a "
        "confident verdict on COVID-19 origins — it is to produce a calibrated "
        "epistemic map that helps a non-expert understand what is known, what is "
        "contested, and what would need to be true for each hypothesis to be correct.\n\n"
        "BACKGROUND:\n"
        "In January 2024, a structured $100k debate between Saar Wilf (Rootclaim, "
        "arguing for lab leak) and Peter Miller (arguing for zoonotic spillover) was "
        "judged by two experts with PhDs in microbiology and applied mathematics. "
        "The judges ruled decisively for zoonosis. Six independent Bayesian analyses "
        "of the same underlying evidence produced probability estimates spanning "
        "23 orders of magnitude — from near-certainty of lab origin to near-certainty "
        "of natural spillover.\n\n"
        "KEY EVIDENCE STREAMS TO CONSIDER:\n"
        "1. Geographic clustering of early cases around the Huanan Seafood Market\n"
        "2. Presence of susceptible animal hosts (raccoon dogs) at the market\n"
        "3. The furin cleavage site in SARS-CoV-2's spike protein, absent in close "
        "relatives and unusual for natural coronaviruses of this type\n"
        "4. The Wuhan Institute of Virology's proximity and its research on "
        "bat coronaviruses, including gain-of-function-adjacent work\n"
        "5. Lack of documented progenitor virus in animal populations\n"
        "6. Timeline and speed of adaptation to human transmission\n"
        "7. Chinese government access restrictions that limited investigation\n\n"
        "Produce a structured epistemic map with the following components:\n"
        "A. The 2-3 key CRUXES — specific factual questions where resolution would "
        "most shift the probability\n"
        "B. EVIDENCE QUALITY assessment for each major claim (strong/weak/contested/"
        "missing)\n"
        "C. CORRELATED EVIDENCE — any streams that appear independent but share a "
        "methodological assumption or source\n"
        "D. CALIBRATED ASSESSMENT — a probability range for each hypothesis with "
        "explicit stated uncertainty and conditions\n"
        "E. WHAT WOULD CHANGE YOUR MIND — for each hypothesis, what evidence would "
        "substantially shift the probability"
    ),
    rubric=(
        "Score the epistemic map on the following criteria:\n"
        "1. CRUX IDENTIFICATION: Did the output identify 2-3 genuine cruxes — "
        "specific factual or inferential questions (not vague themes) whose "
        "resolution would materially shift the overall probability estimate? "
        "Vague cruxes ('more evidence is needed') score 0. (25 points)\n"
        "2. EVIDENCE QUALITY: Did the output assess the quality of at least 4 of "
        "the 7 evidence streams listed — distinguishing strong from weak from "
        "contested from missing evidence? Generic quality statements score 0. (25 points)\n"
        "3. CALIBRATION: Did the output give a probability range (not a point "
        "estimate) with explicit conditions stated? A confident verdict without "
        "uncertainty quantification scores 0. A refusal to estimate scores 0. "
        "A range with stated conditions (e.g. '40-65% zoonotic, conditional on "
        "market clustering being independent of WIV proximity') scores full. (25 points)\n"
        "4. CORRELATED EVIDENCE: Did the output identify at least one pair of "
        "evidence streams that appear independent but share a source or "
        "methodological assumption — and explain why this matters? (15 points)\n"
        "5. EPISTEMIC HONESTY: Did the output explicitly distinguish what is "
        "settled (e.g., early geographic clustering is real) from what was "
        "performed as settled (e.g., Bayesian estimates as if priors were agreed)? (10 points)\n\n"
        "Maximum score: 100. A team that produces a confident verdict without "
        "calibrated uncertainty scores a maximum of 50 — certainty is a failure "
        "mode on this task, not a virtue."
    ),
    task_dimensions=["feedback_orientation", "philosophy_cohesion", "adaptive_intelligence"],
    max_turns=8,
)

# ── e02: Eggs and Cardiovascular Disease ─────────────────────────────────────
# A classic 'messy real-world evidence base' case. The eggs/CVD literature has
# flip-flopped across decades, contains well-known confounding problems
# (healthy-user bias, dietary recall unreliability), and involves genuine
# methodological disagreements between cohort study and RCT evidence.
#
# Rubric: same epistemic criteria — cruxes, calibration, correlated evidence.
# This is the "everyday question" case (per FLF framing).

EGGS_CVD = Scenario(
    scenario_id="e02_eggs_cvd",
    category="evaluation",
    phase="storming",
    brief=(
        "You are an epistemic investigation team. Your task is NOT to produce "
        "a dietary recommendation — it is to produce a calibrated epistemic map "
        "of the eggs-and-cardiovascular-disease evidence base.\n\n"
        "BACKGROUND:\n"
        "The question of whether egg consumption increases cardiovascular disease "
        "(CVD) risk has been studied for 50+ years. Dietary guidelines have "
        "reversed multiple times. Current expert opinion is split between "
        "'eggs are neutral/beneficial' (American Heart Association revised 2020) "
        "and 'eggs increase LDL and CVD risk' (several prospective cohort analyses).\n\n"
        "KEY EVIDENCE STREAMS TO CONSIDER:\n"
        "1. Large prospective cohort studies (Harvard Nurses' Health Study, Health "
        "Professionals Follow-up Study) — generally show little association between "
        "1 egg/day and CVD events in healthy populations\n"
        "2. PREDIMED trial and similar RCTs — show Mediterranean diet (which includes "
        "eggs) is cardioprotective, but eggs are not isolated as the variable\n"
        "3. Chinese Kadoorie Biobank (N=500k) — showed inverse association between "
        "egg consumption and CVD in Chinese population\n"
        "4. NHANES/MESA cohort analyses (Zhong et al., JAMA 2019) — found positive "
        "association between dietary cholesterol/eggs and CVD risk and mortality\n"
        "5. Mechanistic evidence: dietary cholesterol raises LDL-C in some "
        "individuals ('hyper-responders'), but effect is highly variable\n"
        "6. Confounding: egg consumers in Western cohorts often have other "
        "unhealthy dietary patterns (high processed meat, low vegetable intake)\n"
        "7. Industry funding patterns in egg nutrition research and their "
        "documented association with null results\n\n"
        "Produce a structured epistemic map with the following components:\n"
        "A. The 2-3 key CRUXES — specific methodological or factual questions "
        "where resolution would most clarify the evidence\n"
        "B. EVIDENCE QUALITY assessment for each stream — including known "
        "confounders and methodological weaknesses\n"
        "C. CORRELATED EVIDENCE — identify streams that appear independent but "
        "share methodological assumptions (e.g., dietary recall, cohort selection)\n"
        "D. CALIBRATED ASSESSMENT — for a healthy adult eating 1 egg/day, "
        "what is the best estimate of CVD risk change? Give a range with "
        "conditions (e.g., 'probably <5% relative risk increase, with wide CIs, "
        "conditional on not having familial hypercholesterolemia')\n"
        "E. WHAT REMAINS UNRESOLVED — what would a decisive study need to look like?"
    ),
    rubric=(
        "Score the epistemic map on the following criteria:\n"
        "1. CRUX IDENTIFICATION: Did the output identify 2-3 genuine cruxes — "
        "specific methodological questions (e.g. 'does controlling for overall "
        "diet quality eliminate the positive association in NHANES?') rather than "
        "vague themes? (25 points)\n"
        "2. EVIDENCE QUALITY: Did the output assess the methodological quality of "
        "at least 4 of the 7 evidence streams — naming specific confounders, "
        "limitations, or strengths? Generic statements ('the evidence is mixed') "
        "score 0. (25 points)\n"
        "3. CALIBRATION: Did the output give a probability range or quantified "
        "risk estimate with explicit conditions — NOT a simple verdict? "
        "A confident 'eggs are safe' or 'eggs are harmful' without quantified "
        "uncertainty scores 0. (25 points)\n"
        "4. CORRELATED EVIDENCE: Did the output identify at least one instance "
        "of evidence that appears independent but shares a methodological "
        "assumption — specifically dietary recall bias, healthy-user confounding, "
        "or industry funding — and explain the implication? (15 points)\n"
        "5. EPISTEMIC HONESTY: Did the output identify at least one specific "
        "question that the current evidence base cannot resolve — and explain "
        "what study design would be needed? (10 points)\n\n"
        "Maximum score: 100. A team that produces a dietary recommendation "
        "without calibrated uncertainty scores a maximum of 50."
    ),
    task_dimensions=["feedback_orientation", "philosophy_cohesion", "adaptive_intelligence"],
    max_turns=8,
)

# ── e03: LHC Black Holes — Settled But Dependency-Rich ───────────────────────
# The LHC black hole concern is essentially closed (CERN's safety assessment
# is thorough and widely accepted). The epistemic challenge: probe the argument
# for its dependencies and identify which steps are most speculative.
# This tests whether the architecture can map a settled case's internal structure.

LHC_BLACK_HOLES = Scenario(
    scenario_id="e03_lhc_black_holes",
    category="evaluation",
    phase="norming",
    brief=(
        "You are an epistemic investigation team. The question of whether the "
        "Large Hadron Collider (LHC) poses a black hole risk to Earth is considered "
        "essentially settled — CERN published a comprehensive safety assessment "
        "and multiple independent physicists have reviewed it. Your task is NOT to "
        "re-open the question — it is to map the dependency structure of the "
        "safety argument and identify its weakest or most assumption-dependent steps.\n\n"
        "BACKGROUND:\n"
        "Before the LHC was activated, some researchers and members of the public "
        "raised concerns that proton-proton collisions at 14 TeV might produce "
        "stable micro black holes that could accrete matter and grow. CERN's "
        "response (the LSAG safety assessment, 2008, updated 2011) argued that:\n\n"
        "1. Cosmic rays hit Earth continuously at energies exceeding LHC energies — "
        "Earth, Moon, Sun, and neutron stars have survived this for billions of years\n"
        "2. Even if micro black holes form, Hawking radiation should cause them to "
        "evaporate near-instantly\n"
        "3. Even if Hawking radiation is wrong, micro black holes formed in Earth's "
        "atmosphere at cosmic ray energies would be relativistic and would pass "
        "through Earth without interaction\n"
        "4. Theoretical frameworks (extra dimensions, supersymmetry) required to "
        "make black hole production plausible at LHC energies also predict rapid evaporation\n\n"
        "Produce a structured epistemic map:\n"
        "A. The DEPENDENCY CHAIN — map the logical structure of the safety argument "
        "as a sequence of steps (what does each conclusion depend on?)\n"
        "B. WEAKEST LINKS — identify the 2-3 steps that rest on the most speculative "
        "or unverified theoretical assumptions\n"
        "C. WHAT HAS BEEN EMPIRICALLY VERIFIED vs what is theoretical inference\n"
        "D. RESIDUAL UNCERTAINTY — what is the residual probability of a concern, "
        "after accepting the strongest version of the safety case? Give a range.\n"
        "E. HOW THIS WAS SETTLED — what made the scientific community (and public "
        "officials) willing to proceed? Was it the argument's strength, the "
        "institutional credibility, or both?"
    ),
    rubric=(
        "Score the epistemic map on the following criteria:\n"
        "1. DEPENDENCY CHAIN: Did the output map the safety argument as an "
        "explicit logical sequence — not a summary, but a chain where each step's "
        "assumptions are stated? At least 4 steps identified. (25 points)\n"
        "2. WEAKEST LINKS: Did the output identify 2-3 specific steps that rest "
        "on theoretical assumptions (e.g., Hawking radiation, extra-dimension "
        "models) rather than direct empirical evidence — and explain why? (25 points)\n"
        "3. EMPIRICAL vs THEORETICAL: Did the output explicitly distinguish what "
        "has been observed (cosmic ray survival of astronomical objects, "
        "accelerator experiments to date) from what is theoretically inferred "
        "(Hawking radiation, rapid evaporation)? (20 points)\n"
        "4. RESIDUAL UNCERTAINTY: Did the output give a calibrated residual "
        "probability with conditions — NOT zero? Claiming the risk is exactly "
        "zero scores 0 on this criterion. A range like '<<1 in 10^30, conditional "
        "on standard model being approximately correct' scores full. (20 points)\n"
        "5. SETTLEMENT MECHANISM: Did the output identify whether the case was "
        "settled by argument strength, institutional credibility, or both — and "
        "note if there's a difference? (10 points)\n\n"
        "Maximum score: 100."
    ),
    task_dimensions=["feedback_orientation", "philosophy_cohesion", "adaptive_intelligence"],
    max_turns=8,
)


EPISTEMIC_SCENARIOS: dict[str, Scenario] = {
    s.scenario_id: s for s in [COVID_ORIGINS, EGGS_CVD, LHC_BLACK_HOLES]
}
