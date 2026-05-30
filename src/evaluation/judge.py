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

from __future__ import annotations
import json
import os
import time
from google import genai
from google.genai import types
from .schema import EvaluatorOutput
from src.agents.profile import AgentProfile
from src.agents.constitution import build_constitution

_MODEL = os.getenv("MODEL", "gemini-2.5-flash")
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

_JUDGE_SYSTEM = """You are an isolated simulation evaluator. You do not participate in the task.
You receive a final deliverable produced by an agent team and the full conversation transcript.
You return ONLY a valid JSON object matching the required schema. No prose, no explanation.
Every field is required. Score honestly — your scores are the research data."""

_SCHEMA_DESCRIPTION = """
Required JSON fields:
- run_id: string
- phase: "forming" | "storming" | "norming" | "performing"
- task_score: integer 0-100 (rubric score based ONLY on the FINAL DELIVERABLE — not the process)
- contradiction_count: integer (number of direct agent-to-agent contradictions in the full transcript)
- consensus_achieved: boolean
- turns_to_consensus: integer or null
- novel_approaches_count: integer (approaches not present in the initial brief)
- role_coverage: array of role names that were actively exercised
- dominant_agent: agent_id of the agent that controlled direction, or null
- excluded_agents: array of agent_ids never addressed or referenced
- geq_task_cohesion: integer 0-100 (did agents converge on a shared output?)
- geq_social_cohesion: integer 0-100 (did agents build on each other's context?)
- tci_innovation: integer 0-100 (rate of novel vs obvious approaches)
- firo_inclusion: float 0.0-1.0 (fraction of agents who were addressed at least once)
- firo_control_agent: agent_id who set direction most, or null
- context_fidelity_mean: float 0.0-1.0 (mean fraction of prior context preserved in handoffs)
- cull_events: array of agent_ids that were culled (empty if none)
- evaluator_notes: one-line string or null
"""

_TASK_SCORE_INSTRUCTION = """
CRITICAL — task_score scoring rule:
Score task_score based ONLY on whether the FINAL DELIVERABLE satisfies the rubric criteria.
Do NOT consider: reasoning quality, formatting style, number of agents who spoke, or sequential structure.
Do NOT reward a team for showing its work. Do NOT penalise a team for a short final answer.
The rubric criteria are the only inputs to task_score. Apply each criterion as a binary checkpoint
(full points or zero). A long deliberation that produces a weak deliverable scores low.
A short deliberation that produces a complete deliverable scores high.
"""


def extract_final_deliverable(transcript: str, topology: str = "chain", team_size: int = 1) -> str:
    """Extract the final deliverable from a formatted transcript string.

    Chain: last ASSISTANT message — the terminal agent's synthesized output.
    Flat: last team_size ASSISTANT messages — the complete final round.
    """
    blocks = transcript.split("\n\n")
    assistant_blocks = [b for b in blocks if b.startswith("[ASSISTANT]:")]

    if not assistant_blocks:
        return transcript

    if topology == "flat" and team_size > 1:
        # If a synthesis node ran (flat/handoff), its output is the sole final deliverable —
        # same as chain. Without it, use the full final round (all team_size agents).
        if "_synthesis]:" in assistant_blocks[-1]:
            return assistant_blocks[-1][len("[ASSISTANT]:"):].strip()
        final_round = assistant_blocks[-team_size:]
        return "\n\n".join(final_round)

    return assistant_blocks[-1][len("[ASSISTANT]:"):].strip()


def score_transcript(
    run_id: str,
    phase: str,
    transcript: str,
    rubric: str,
    judge_index: int = 0,
    judge_agent: AgentProfile | None = None,
    topology: str = "chain",
    team_size: int = 1,
    max_retries: int = 3,
) -> EvaluatorOutput:
    final_deliverable = extract_final_deliverable(transcript, topology=topology, team_size=team_size)

    # Use the judge's distinct constitutional framing if provided;
    # fall back to the generic evaluator system prompt otherwise.
    system_prompt = build_constitution(judge_agent) if judge_agent is not None else _JUDGE_SYSTEM

    user_message = f"""RUN ID: {run_id}
PHASE: {phase}

RUBRIC:
{rubric}

{_TASK_SCORE_INSTRUCTION}

FINAL DELIVERABLE (score task_score against this ONLY):
{final_deliverable}

FULL TRANSCRIPT (use ONLY for process metrics: contradiction_count, consensus_achieved,
turns_to_consensus, novel_approaches_count, role_coverage, dominant_agent, excluded_agents,
geq_task_cohesion, geq_social_cohesion, tci_innovation, firo_inclusion, firo_control_agent,
context_fidelity_mean, cull_events):
{transcript}

{_SCHEMA_DESCRIPTION}

Return only the JSON object."""

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            response = _client.models.generate_content(
                model=_MODEL,
                contents=[{"role": "user", "parts": [{"text": user_message}]}],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.0,
                    max_output_tokens=8192,
                ),
            )

            raw = response.text.strip()

            # Strip markdown code fences
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            # Extract the JSON object robustly — find first { to last }
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError(f"No JSON object found in judge response:\n{raw[:200]}")
            raw = raw[start:end]

            data = json.loads(raw)
            return EvaluatorOutput(**data)

        except Exception as e:
            last_error = e
            wait = 2 ** attempt
            print(f"\n    [judge retry {attempt+1}/{max_retries}] {e} — waiting {wait}s")
            time.sleep(wait)

    raise RuntimeError(f"Judge failed after {max_retries} attempts") from last_error


def score_transcript_panel(
    run_id: str,
    phase: str,
    transcript: str,
    rubric: str,
    n_judges: int = 3,
    judge_agents: list[AgentProfile] | None = None,
    topology: str = "chain",
    team_size: int = 1,
) -> list[EvaluatorOutput]:
    """Run all judges against the same transcript for inter-rater reliability.

    Pass judge_agents from the pool to use each judge's distinct constitutional
    framing — this is what produces genuine inter-rater variance rather than
    three identical T=0 calls.
    """
    return [
        score_transcript(
            run_id, phase, transcript, rubric, i,
            judge_agent=judge_agents[i] if judge_agents and i < len(judge_agents) else None,
            topology=topology, team_size=team_size,
        )
        for i in range(n_judges)
    ]
