from __future__ import annotations
import json
import os
from google import genai
from google.genai import types
from .schema import EvaluatorOutput

_MODEL = os.getenv("MODEL", "gemini-2.5-flash")
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

_JUDGE_SYSTEM = """You are an isolated simulation evaluator. You do not participate in the task.
You receive a transcript of an agent team simulation and a run context.
You return ONLY a valid JSON object matching the required schema. No prose, no explanation.
Every field is required. Score honestly — your scores are the research data."""

_SCHEMA_DESCRIPTION = """
Required JSON fields:
- run_id: string
- phase: "forming" | "storming" | "norming" | "performing"
- task_score: integer 0-100 (overall output quality against the rubric)
- contradiction_count: integer (number of direct agent-to-agent contradictions)
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


def score_transcript(
    run_id: str,
    phase: str,
    transcript: str,
    rubric: str,
    judge_index: int = 0,
) -> EvaluatorOutput:
    user_message = f"""RUN ID: {run_id}
PHASE: {phase}

RUBRIC:
{rubric}

TRANSCRIPT:
{transcript}

{_SCHEMA_DESCRIPTION}

Return only the JSON object."""

    response = _client.models.generate_content(
        model=_MODEL,
        contents=[{"role": "user", "parts": [{"text": user_message}]}],
        config=types.GenerateContentConfig(
            system_instruction=_JUDGE_SYSTEM,
            temperature=0.0,
            max_output_tokens=4096,
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
        raise ValueError(f"No JSON object found in judge response:\n{raw}")
    raw = raw[start:end]

    data = json.loads(raw)
    return EvaluatorOutput(**data)


def score_transcript_panel(
    run_id: str,
    phase: str,
    transcript: str,
    rubric: str,
    n_judges: int = 3,
) -> list[EvaluatorOutput]:
    """Run all judges against the same transcript for inter-rater reliability."""
    return [score_transcript(run_id, phase, transcript, rubric, i) for i in range(n_judges)]
