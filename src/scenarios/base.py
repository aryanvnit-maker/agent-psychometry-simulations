from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Scenario:
    scenario_id: str
    category: str          # matches telemetry ENUM: strategic/crisis/resource/evaluation/creative
    phase: str             # forming/storming/norming/performing
    brief: str             # injected as the first user message
    rubric: str            # passed to the God Mode Evaluator
    task_dimensions: list[str]  # Kalibr dimensions weighted for captain selection
    max_turns: int = 6
