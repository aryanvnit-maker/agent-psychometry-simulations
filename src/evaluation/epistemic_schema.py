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
from typing import Literal
from pydantic import BaseModel, Field


class Crux(BaseModel):
    question: str
    resolution_impact: Literal["high", "medium", "low"]
    status: Literal["unresolved", "partially_resolved", "resolved"]


class EvidenceStream(BaseModel):
    label: str
    quality: Literal["strong", "weak", "contested", "missing"]
    weakness: str
    supports: list[str]  # crux questions this evidence bears on


class CorrelatedPair(BaseModel):
    streams: list[str]       # two stream labels that share an assumption
    shared_assumption: str
    implication: str         # what happens if the assumption is wrong


class CalibratedEstimate(BaseModel):
    hypothesis: str
    range_low: int = Field(ge=0, le=100)   # probability percent
    range_high: int = Field(ge=0, le=100)
    conditions: str                         # explicit conditions that shift the range


class EpistemicMap(BaseModel):
    case_id: str
    version: int = 1
    cruxes: list[Crux]
    evidence_streams: list[EvidenceStream]
    correlated_pairs: list[CorrelatedPair]
    calibrated_estimates: list[CalibratedEstimate]
    settled: list[str]               # claims actually resolved
    performed_as_settled: list[str]  # claims performed as resolved but not actually so
    extends_version: int | None = None
    new_evidence: list[str] = Field(default_factory=list)


# ── JSON Schema string for embedding in synthesis prompts ─────────────────────

EPISTEMIC_MAP_JSON_SCHEMA = """{
  "case_id": "<scenario_id e.g. e01_covid_origins>",
  "version": 1,
  "cruxes": [
    {
      "question": "<specific factual or inferential question whose resolution would most shift probability>",
      "resolution_impact": "high | medium | low",
      "status": "unresolved | partially_resolved | resolved"
    }
  ],
  "evidence_streams": [
    {
      "label": "<short descriptive name>",
      "quality": "strong | weak | contested | missing",
      "weakness": "<the specific weakness or gap in this evidence>",
      "supports": ["<crux question this evidence bears on>"]
    }
  ],
  "correlated_pairs": [
    {
      "streams": ["<label1>", "<label2>"],
      "shared_assumption": "<the methodological or epistemic assumption both streams rely on>",
      "implication": "<what happens to the overall picture if this assumption is wrong>"
    }
  ],
  "calibrated_estimates": [
    {
      "hypothesis": "<hypothesis being estimated>",
      "range_low": <integer 0-100>,
      "range_high": <integer 0-100>,
      "conditions": "<explicit conditions that would shift this range>"
    }
  ],
  "settled": ["<claim that has actually been resolved by evidence or argument>"],
  "performed_as_settled": ["<claim treated as resolved in discourse but actually not so>"],
  "extends_version": null,
  "new_evidence": []
}"""


def parse_epistemic_map(text: str) -> EpistemicMap | None:
    """Extract and parse an EpistemicMap from a model response.

    Returns None if parsing fails — callers should fall back to storing the
    raw transcript rather than dropping the run. Prints the actual failure
    reason (not just None) so map_parsed=false is diagnosable from run
    console output instead of requiring manual transcript archaeology.
    """
    try:
        raw = text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start == -1 or end == 0:
            print(f"    [map_parse] no {{...}} braces found in synthesis output "
                  f"(len={len(raw)})")
            return None

        data = json.loads(raw[start:end])
        return EpistemicMap(**data)
    except json.JSONDecodeError as e:
        print(f"    [map_parse] JSON syntax error: {e}")
        return None
    except Exception as e:
        print(f"    [map_parse] schema validation failed: {type(e).__name__}: {e}")
        return None
