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
Code block extractor for agent transcripts.

Extraction rules by topology:
  chain — last complete ```python...``` block in the final agent's message
  flat  — last complete ```python...``` block from the final agent's final round

Returns empty string (never None) on extraction failure so callers can
safely call .strip() without guards.
"""
from __future__ import annotations
import re

# Matches complete fenced blocks: ```python ... ```
_CODE_BLOCK_RE = re.compile(r"```(?:python3?|py)?\s*\n(.*?)```", re.DOTALL)
# Matches unclosed blocks: ```python ... <end of string> (token budget cutoff)
_CODE_BLOCK_OPEN_RE = re.compile(r"```(?:python3?|py)?\s*\n(.*?)$", re.DOTALL)


def _last_code_block(text: str) -> str:
    """Return the last code block body, complete or truncated, or ''."""
    matches = _CODE_BLOCK_RE.findall(text)
    if matches:
        return matches[-1]
    # Fallback: model ran out of tokens before closing the fence
    m = _CODE_BLOCK_OPEN_RE.search(text)
    return m.group(1) if m else ""


def extract_chain(transcript: list[dict]) -> str:
    """Extract submitted code from a chain-topology transcript.

    Chain rule: the final agent's last output contains the deliverable.
    The last ```python block in that message is the submitted solution.

    Args:
        transcript: List of message dicts with at least 'role' and 'content' keys.
                    Expected roles: 'agent_1', 'agent_2', ..., or 'assistant'.

    Returns:
        Python source string, or '' if no code block found.
    """
    final_message = _last_agent_message(transcript)
    if not final_message:
        return ""
    return _last_code_block(final_message)


def extract_flat(transcript: list[dict], n_agents: int) -> str:
    """Extract submitted code from a flat-topology transcript.

    Flat rule: in round-table format the last agent to speak in the final round
    synthesizes the deliverable. Return the last ```python block from that message.

    Args:
        transcript: List of message dicts.
        n_agents: Number of agents in the flat topology (used to identify final-round speaker).

    Returns:
        Python source string, or '' if no code block found.
    """
    # Find the last message from any agent role that contains a code block.
    # In flat topologies the synthesis agent writes the final answer; we scan
    # backward for the last code block across all agent messages in the
    # final round (defined as the last n_agents messages from agent roles).
    agent_messages = [
        m for m in transcript
        if _is_agent_role(_msg_role(m))
    ]

    # Take the last n_agents messages as the "final round"
    final_round = agent_messages[-n_agents:] if len(agent_messages) >= n_agents else agent_messages

    # Search backward through final round for a code block
    for msg in reversed(final_round):
        code = _last_code_block(_msg_content(msg))
        if code:
            return code

    # Fallback: search entire transcript backward
    for msg in reversed(transcript):
        if _is_agent_role(_msg_role(msg)):
            code = _last_code_block(_msg_content(msg))
            if code:
                return code

    return ""


def extract(transcript: list[dict], topology: str, n_agents: int = 1) -> str:
    """Dispatch to topology-appropriate extractor.

    Args:
        transcript: Agent transcript as list of message dicts.
        topology: 'chain' or 'flat'.
        n_agents: Number of agents (used for flat extraction).

    Returns:
        Python source string, or '' on failure.
    """
    if topology == "chain":
        return extract_chain(transcript)
    elif topology == "flat":
        return extract_flat(transcript, n_agents)
    else:
        raise ValueError(f"Unknown topology: {topology!r}. Expected 'chain' or 'flat'.")


def _msg_role(msg) -> str:
    """Extract role string from either a dict or a LangChain message object."""
    if isinstance(msg, dict):
        return msg.get("role", "")
    return getattr(msg, "type", "") or getattr(msg, "role", "")


def _msg_content(msg) -> str:
    """Extract content string from either a dict or a LangChain message object."""
    if isinstance(msg, dict):
        return msg.get("content", "")
    return getattr(msg, "content", "") or ""


def _last_agent_message(transcript: list) -> str:
    """Return content of the last message from an agent role."""
    for msg in reversed(transcript):
        if _is_agent_role(_msg_role(msg)):
            return _msg_content(msg)
    return ""


def _is_agent_role(role: str) -> bool:
    """True for agent/assistant roles, false for user/system/human."""
    role = role.lower()
    return role not in ("user", "system", "human", "tool", "function", "")
