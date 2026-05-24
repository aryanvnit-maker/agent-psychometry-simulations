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

from pydantic import BaseModel, Field
from typing import Literal


class EvaluatorOutput(BaseModel):
    run_id: str
    phase: Literal["forming", "storming", "norming", "performing"]
    task_score: int = Field(ge=0, le=100)
    contradiction_count: int = Field(ge=0)
    consensus_achieved: bool
    turns_to_consensus: int | None
    novel_approaches_count: int = Field(ge=0)
    role_coverage: list[str]
    dominant_agent: str | None
    excluded_agents: list[str]
    geq_task_cohesion: int = Field(ge=0, le=100, description="GEQ proxy: shared output convergence")
    geq_social_cohesion: int = Field(ge=0, le=100, description="GEQ proxy: context build-on rate")
    tci_innovation: int = Field(ge=0, le=100, description="TCI proxy: novel approach rate")
    firo_inclusion: float = Field(ge=0.0, le=1.0, description="FIRO-B proxy: fraction of agents addressed")
    firo_control_agent: str | None = Field(description="FIRO-B proxy: agent that set direction most often")
    context_fidelity_mean: float | None = Field(default=None, ge=0.0, le=1.0, description="Phase 9: mean context fidelity across agents")
    cull_events: list[str] = Field(default_factory=list, description="Agent IDs culled during this run")
    evaluator_notes: str | None = None
