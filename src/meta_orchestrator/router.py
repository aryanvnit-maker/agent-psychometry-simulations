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
Meta-orchestrator router.

Maps classified task domain → agent configuration + evaluation method.

Routing table (empirically derived):
  judgment  → chain-2 with Kalibr dimension profiles, IMPLEMENTER × 2, judge panel evaluation
  execution → chain-2 generic, IMPLEMENTER → SOLVER, subprocess evaluation

Both configs use IMPLEMENTER role so constitutions generate primary content.
The sole differentiator between configs is:
  - Kalibr dimension scores (judgment agents have higher adaptive_intelligence,
    feedback_orientation, drive_alignment vs balanced execution baselines)
  - Handoff prompt (JUDGMENT_HANDOFF vs EXECUTION_HANDOFF)
"""
from __future__ import annotations
from src.agents.profile import AgentProfile, KalibrDimensions, GameTheoryParams, Role, ConflictStyle
from .classifier import DOMAIN_JUDGMENT, DOMAIN_EXECUTION

# ---------------------------------------------------------------------------
# Handoff prompts
# ---------------------------------------------------------------------------

JUDGMENT_HANDOFF = (
    "Based on the analysis above, synthesize the final recommendation now. "
    "Be definitive: state the recommendation, the two or three variables that drove it, "
    "and the primary downside. No hedging. Commit to a position."
)

EXECUTION_HANDOFF = (
    "Based on the algorithmic analysis above, implement the complete Python solution. "
    "Output exactly one ```python code block with the full runnable solution. "
    "No explanation outside the code block."
)

# ---------------------------------------------------------------------------
# Agent factories
# ---------------------------------------------------------------------------

def _judgment_analyst() -> AgentProfile:
    """Analysis agent for judgment tasks. High adaptability, high feedback orientation."""
    return AgentProfile(
        agent_id="judgment_analyst",
        dimensions=KalibrDimensions(
            philosophy_cohesion=80,
            drive_alignment=75,
            bonding_index=65,
            adaptive_intelligence=90,
            volatility_vector=30,
            ambiguity_tolerance=80,
            influence_style=55,
            feedback_orientation=85,
            temporal_orientation=60,
            energy_resilience=80,
        ),
        role=Role.IMPLEMENTER,
        game_theory=GameTheoryParams(
            context_sharing="full",
            memory_persistence=False,
            signaling=False,
            conflict_style=ConflictStyle.NEGOTIATE,
        ),
    )


def _judgment_synthesizer() -> AgentProfile:
    """Synthesis agent for judgment tasks. High drive alignment forces committed output."""
    return AgentProfile(
        agent_id="judgment_synthesizer",
        dimensions=KalibrDimensions(
            philosophy_cohesion=85,
            drive_alignment=90,
            bonding_index=55,
            adaptive_intelligence=75,
            volatility_vector=40,
            ambiguity_tolerance=65,
            influence_style=70,
            feedback_orientation=70,
            temporal_orientation=70,
            energy_resilience=85,
        ),
        role=Role.IMPLEMENTER,
        game_theory=GameTheoryParams(
            context_sharing="full",
            memory_persistence=False,
            signaling=False,
            conflict_style=ConflictStyle.NEGOTIATE,
        ),
    )


def _execution_agent(agent_id: str, role: Role = Role.IMPLEMENTER) -> AgentProfile:
    """Generic balanced execution agent. No elaborated persona."""
    return AgentProfile(
        agent_id=agent_id,
        dimensions=KalibrDimensions(
            philosophy_cohesion=75,
            drive_alignment=80,
            bonding_index=50,
            adaptive_intelligence=75,
            volatility_vector=50,
            ambiguity_tolerance=70,
            influence_style=50,
            feedback_orientation=70,
            temporal_orientation=50,
            energy_resilience=75,
        ),
        role=role,
        game_theory=GameTheoryParams(
            context_sharing="full",
            memory_persistence=False,
            signaling=False,
            conflict_style=ConflictStyle.NEGOTIATE,
        ),
    )

# ---------------------------------------------------------------------------
# Routing configs
# ---------------------------------------------------------------------------

def get_judgment_config() -> dict:
    """Agent config optimised for judgment/convergence tasks."""
    return {
        "agents": [_judgment_analyst(), _judgment_synthesizer()],
        "topology": "chain",
        "evaluation": DOMAIN_JUDGMENT,
        "handoff_prompts": {1: JUDGMENT_HANDOFF},
    }


def get_execution_config() -> dict:
    """Agent config optimised for execution/deterministic tasks."""
    return {
        "agents": [
            _execution_agent("exec_analyzer", role=Role.IMPLEMENTER),
            _execution_agent("exec_solver",   role=Role.SOLVER),
        ],
        "topology": "chain",
        "evaluation": DOMAIN_EXECUTION,
        "handoff_prompts": {1: EXECUTION_HANDOFF},
    }


def route(domain: str) -> dict:
    """Return the agent config for a classified domain."""
    if domain == DOMAIN_EXECUTION:
        return get_execution_config()
    return get_judgment_config()
