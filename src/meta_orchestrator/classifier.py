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
Task domain classifier.

Classifies an incoming task prompt into one of two empirically-validated domains:

  JUDGMENT  — subjective, bounded convergence, requires recommendation or decision.
              Optimal architecture: chain-2 with balanced Kalibr behavioral profiles.
              (Phase 1 finding: 57.6 vs 10.7 for flat-2 on business judgment tasks)

  EXECUTION — deterministic, binary ground truth, precise technical output required.
              Optimal architecture: chain-2 generic, no role personas.
              (Phase 2 finding: 16% pass@1, role personas drop to 13%)

Uses Gemini Flash with few-shot prompting. Cheap single call per task (~50 tokens).
"""
from __future__ import annotations
import os
from google import genai
from google.genai import types

DOMAIN_JUDGMENT  = "judgment"
DOMAIN_EXECUTION = "execution"

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

_CLASSIFY_PROMPT = """\
Classify the following task into exactly one domain.

JUDGMENT — The task requires subjective analysis, strategic recommendation, or convergence \
on a decision. Output is evaluated against qualitative rubric criteria. \
Examples: business strategy, legal analysis, investment decisions, post-mortem analysis, \
crisis response, policy evaluation.

EXECUTION — The task requires deterministic, precise output with binary correctness. \
Output is evaluated against objective criteria (tests pass/fail, output matches exactly). \
Examples: competitive programming, code generation, SQL queries, mathematical proofs, \
data transformation with exact expected output.

Respond with exactly one word: judgment or execution.

Task:
{prompt}"""


def classify(prompt: str) -> str:
    """Classify a task prompt into 'judgment' or 'execution'.

    Returns DOMAIN_JUDGMENT or DOMAIN_EXECUTION.
    Falls back to DOMAIN_JUDGMENT on any error (safer default for ambiguous cases).
    """
    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[{"role": "user", "parts": [{"text": _CLASSIFY_PROMPT.format(
                prompt=prompt[:1500]
            )}]}],
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=10,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
        result = (response.text or "").strip().lower()
        if DOMAIN_EXECUTION in result:
            return DOMAIN_EXECUTION
        return DOMAIN_JUDGMENT
    except Exception:
        return DOMAIN_JUDGMENT


def classify_batch(prompts: list[str]) -> list[str]:
    """Classify a list of prompts. Returns list of domain strings."""
    return [classify(p) for p in prompts]
