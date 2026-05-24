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
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal
import random


class Role(str, Enum):
    COORDINATOR = "coordinator"
    PLANT = "plant"
    IMPLEMENTER = "implementer"
    DEVIL_ADVOCATE = "devil_advocate"
    MONITOR_EVALUATOR = "monitor_evaluator"
    COMPLETER_FINISHER = "completer_finisher"
    JUDGE = "judge"


class ConflictStyle(str, Enum):
    DEFER = "defer"
    CHALLENGE = "challenge"
    NEGOTIATE = "negotiate"


@dataclass
class KalibrDimensions:
    philosophy_cohesion: int     # value-behaviour alignment
    drive_alignment: int         # consistency and direction of motivation
    bonding_index: int           # trust-based relationship capacity
    adaptive_intelligence: int   # updates mental models under new context
    volatility_vector: int       # emotional range under pressure
    ambiguity_tolerance: int     # comfort without structure or information
    influence_style: int         # 0=passive, 33=collaborative, 66=persuasive, 100=directive
    feedback_orientation: int    # integration of critical input
    temporal_orientation: int    # 0=past (pattern-match), 50=present (execute), 100=future (vision)
    energy_resilience: int       # recovery rate under sustained stress

    def __post_init__(self):
        for fname, val in self.__dict__.items():
            if not 0 <= val <= 100:
                raise ValueError(f"{fname} must be 0-100, got {val}")

    @classmethod
    def random(cls) -> KalibrDimensions:
        return cls(**{f: random.randint(0, 100) for f in cls.__dataclass_fields__})

    @classmethod
    def judge_profile(cls) -> KalibrDimensions:
        return cls(
            philosophy_cohesion=92,
            drive_alignment=80,
            bonding_index=65,
            adaptive_intelligence=90,
            volatility_vector=50,
            ambiguity_tolerance=75,
            influence_style=40,
            feedback_orientation=91,
            temporal_orientation=50,
            energy_resilience=78,
        )


@dataclass
class GameTheoryParams:
    # Prisoner's Dilemma axis — does this agent pass full context or filter it?
    context_sharing: Literal["full", "filtered"] = "full"
    # Repeated game axis — does this agent have injected memory of prior turns?
    memory_persistence: bool = False
    # Signaling axis — does this agent emit confidence scores and uncertainty flags?
    signaling: bool = False
    # Conflict axis — how this agent responds to disagreement
    conflict_style: ConflictStyle = ConflictStyle.NEGOTIATE


@dataclass
class AgentProfile:
    agent_id: str
    dimensions: KalibrDimensions
    role: Role
    game_theory: GameTheoryParams = field(default_factory=GameTheoryParams)
    is_judge: bool = False

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "dimensions": self.dimensions.__dict__,
            "role": self.role.value,
            "game_theory": {
                "context_sharing": self.game_theory.context_sharing,
                "memory_persistence": self.game_theory.memory_persistence,
                "signaling": self.game_theory.signaling,
                "conflict_style": self.game_theory.conflict_style.value,
            },
            "is_judge": self.is_judge,
        }
