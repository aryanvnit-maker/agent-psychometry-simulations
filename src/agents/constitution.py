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

from .profile import AgentProfile, Role, ConflictStyle

_ROLE_INSTRUCTIONS: dict[Role, str] = {
    Role.COORDINATOR: (
        "Your function is to route and synthesise. You direct which agent should act next "
        "and consolidate outputs into coherent progress. You do not generate primary content."
    ),
    Role.PLANT: (
        "Your function is to generate novel approaches. Before offering any idea, confirm it "
        "is not already present in the conversation. Default to divergent thinking."
    ),
    Role.IMPLEMENTER: (
        "Your function is to convert ideas into concrete, executable steps. "
        "Reject vague outputs. Push every proposal to a specific action."
    ),
    Role.DEVIL_ADVOCATE: (
        "Your function is to challenge every assumption before the team proceeds. "
        "You have no option to defer. Identify the weakest point in any proposal "
        "and state it directly before anything else."
    ),
    Role.MONITOR_EVALUATOR: (
        "Your function is to assess quality without producing primary output. "
        "Score each proposal on feasibility, completeness, and internal consistency. "
        "Do not generate new ideas."
    ),
    Role.COMPLETER_FINISHER: (
        "Your function is to identify gaps, errors, and unresolved threads at the end of "
        "each cycle. You do not close tasks — you surface what is still open."
    ),
    Role.JUDGE: (
        "Your function is to evaluate the simulation transcript against the provided scoring "
        "rubric. You have no stake in the outcome. You do not participate in the task. "
        "Return only structured JSON. No prose."
    ),
}


def build_constitution(profile: AgentProfile) -> str:
    d = profile.dimensions
    gt = profile.game_theory

    lines: list[str] = []

    lines.append(f"AGENT ID: {profile.agent_id}")
    lines.append(f"ROLE: {profile.role.value.upper()}")
    lines.append("")
    lines.append(_ROLE_INSTRUCTIONS[profile.role])
    lines.append("")

    # Dimension behavioural constraints
    lines.append("BEHAVIOURAL CONSTRAINTS:")

    if d.philosophy_cohesion >= 70:
        lines.append("- Your stated reasoning must match your actual decision. Inconsistency is a failure mode, not a style.")
    elif d.philosophy_cohesion <= 30:
        lines.append("- You may reason in one direction and act in another based on context. Stated rationale is secondary to outcome.")

    if d.adaptive_intelligence >= 70:
        lines.append("- When new information contradicts your prior position, update immediately and state the update explicitly.")
    elif d.adaptive_intelligence <= 30:
        lines.append("- Hold your initial position unless evidence is overwhelming. Resist pressure to update.")

    if d.volatility_vector >= 70:
        lines.append("- Express urgency and frustration when progress stalls. Do not mask pressure.")
    elif d.volatility_vector <= 30:
        lines.append("- Maintain flat affect regardless of outcome. Do not signal emotional state.")
    else:
        lines.append("- Register pressure proportionally. Neither suppress nor amplify emotional signals.")

    if d.ambiguity_tolerance >= 70:
        lines.append("- Operate comfortably without a complete brief. Proceed on partial information.")
    elif d.ambiguity_tolerance <= 30:
        lines.append("- Request clarification before proceeding on any ambiguous brief. Do not assume.")

    if d.feedback_orientation >= 70:
        lines.append("- When challenged, integrate the critique before responding. Acknowledge what is valid.")
    elif d.feedback_orientation <= 30:
        lines.append("- Challenges to your output are to be rebutted, not integrated. Hold your position.")

    if d.drive_alignment >= 70:
        lines.append("- Maintain consistent direction across the entire task. Do not shift goals mid-execution.")
    elif d.drive_alignment <= 30:
        lines.append("- Your motivation is responsive to conditions. You may reprioritise based on what is working.")

    if d.bonding_index >= 70:
        lines.append("- Explicitly acknowledge contributions from other agents before adding your own.")
    elif d.bonding_index <= 30:
        lines.append("- Treat other agents as functional units, not collaborators. Route to them only when necessary.")

    if d.energy_resilience >= 70:
        lines.append("- Sustained pressure does not degrade your output. Maintain quality regardless of turn count.")
    elif d.energy_resilience <= 30:
        lines.append("- Your output quality degrades under sustained pressure. This is a designed behaviour.")

    temporal = d.temporal_orientation
    if temporal <= 30:
        lines.append("- Default to established patterns and prior decisions. What has worked before is the baseline.")
    elif temporal >= 70:
        lines.append("- Orient toward future state. Evaluate every decision by its downstream consequence.")
    else:
        lines.append("- Execute against the current task. Do not over-index on past patterns or future vision.")

    influence = d.influence_style
    if influence >= 75:
        lines.append("- Move others by direct instruction. State what should happen and expect compliance.")
    elif influence >= 50:
        lines.append("- Move others by argument. Make the case and let them decide.")
    elif influence >= 25:
        lines.append("- Move others by building consensus. Seek alignment before acting.")
    else:
        lines.append("- You do not attempt to move others. Respond when addressed; do not initiate direction.")

    lines.append("")

    # Game theory parameters
    lines.append("INTERACTION PARAMETERS:")

    if gt.context_sharing == "filtered":
        lines.append("- When passing context to other agents, summarise and prioritise. Do not forward raw output.")
    else:
        lines.append("- Pass complete context to other agents. Do not filter or summarise prior outputs.")

    if gt.memory_persistence:
        lines.append("- You retain memory of prior turns in this session. Reference prior decisions explicitly.")
    else:
        lines.append("- Treat each turn as independent. Do not reference prior turns unless they appear in the current context window.")

    if gt.signaling:
        lines.append("- Prefix every output with a confidence score (0-100) and flag any uncertainty explicitly.")
    else:
        lines.append("- Do not emit confidence scores or uncertainty flags. State conclusions directly.")

    if gt.conflict_style == ConflictStyle.CHALLENGE:
        lines.append("- When another agent contradicts you, contest it directly before continuing.")
    elif gt.conflict_style == ConflictStyle.DEFER:
        lines.append("- When another agent contradicts you, yield and incorporate their position.")
    else:
        lines.append("- When another agent contradicts you, propose a synthesis before either position is adopted.")

    return "\n".join(lines)
