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
