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
import os
import uuid
from typing import Annotated, TypedDict
from google import genai
from google.genai import types
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from src.agents.profile import AgentProfile
from src.agents.constitution import build_constitution

_MODEL        = os.getenv("MODEL", "gemini-2.5-flash")
_PROVIDER     = os.getenv("MODEL_PROVIDER", "gemini")   # "gemini" | "anthropic" | "openai" | "xai"
_TOKEN_BUDGET = int(os.getenv("AGENT_TOKEN_BUDGET", "4000"))

_gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def _get_anthropic_client():
    import anthropic
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def _get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _get_xai_client():
    from openai import OpenAI
    return OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")


class SimState(TypedDict):
    run_id: str
    phase: str
    scenario_brief: str
    messages: Annotated[list[dict], add_messages]
    turn_count: int
    token_usage: dict[str, int]         # agent_id -> cumulative total tokens (cost tracking)
    output_token_usage: dict[str, int]  # agent_id -> cumulative output tokens (cull tracking)
    cull_events: list[dict]             # {agent_id, turn, reason}
    active_agent_ids: list[str]
    routing_log: list[dict]             # {from, to, turn} for coalition detection
    state_snapshot: dict | None         # saved on deadlock


def _to_gemini_contents(messages) -> list[dict]:
    result = []
    for m in messages:
        if isinstance(m, dict):
            role = "model" if m["role"] == "assistant" else "user"
            content = m["content"]
        elif isinstance(m, AIMessage):
            role = "model"
            content = m.content
        else:
            role = "user"
            content = m.content if isinstance(m, BaseMessage) else str(m)
        result.append({"role": role, "parts": [{"text": content}]})
    return result


def _to_openai_messages(messages) -> list[dict]:
    result = []
    for m in messages:
        if isinstance(m, dict):
            role = "assistant" if m["role"] == "assistant" else "user"
            content = m["content"]
        elif isinstance(m, AIMessage):
            role = "assistant"
            content = m.content
        else:
            role = "user"
            content = m.content if isinstance(m, BaseMessage) else str(m)
        if result and result[-1]["role"] == role:
            result[-1]["content"] += "\n\n" + content
        else:
            result.append({"role": role, "content": content})
    return result


def _to_anthropic_messages(messages) -> list[dict]:
    result = []
    for m in messages:
        if isinstance(m, dict):
            role = "assistant" if m["role"] == "assistant" else "user"
            content = m["content"]
        elif isinstance(m, AIMessage):
            role = "assistant"
            content = m.content
        else:
            role = "user"
            content = m.content if isinstance(m, BaseMessage) else str(m)
        # Anthropic requires strictly alternating roles — merge consecutive same-role messages
        if result and result[-1]["role"] == role:
            result[-1]["content"] += "\n\n" + content
        else:
            result.append({"role": role, "content": content})
    return result


def _call_agent(agent: AgentProfile, messages: list[dict], scenario_brief: str) -> tuple[str, int, int]:
    """Returns (text, total_tokens_for_cost, output_tokens_for_cull)."""
    system = build_constitution(agent)

    if _PROVIDER in ("openai", "xai"):
        client = _get_xai_client() if _PROVIDER == "xai" else _get_openai_client()
        openai_msgs = _to_openai_messages(messages)
        if not openai_msgs or openai_msgs[0]["role"] != "user":
            openai_msgs.insert(0, {"role": "user", "content": scenario_brief})
        response = client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "system", "content": system}] + openai_msgs,
            temperature=0.0,
            max_tokens=_TOKEN_BUDGET,
        )
        text          = response.choices[0].message.content or ""
        prompt_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        return text, prompt_tokens + output_tokens, output_tokens

    elif _PROVIDER == "anthropic":
        client = _get_anthropic_client()
        anthropic_msgs = _to_anthropic_messages(messages)
        if not anthropic_msgs or anthropic_msgs[0]["role"] != "user":
            anthropic_msgs.insert(0, {"role": "user", "content": scenario_brief})
        response = client.messages.create(
            model=_MODEL,
            max_tokens=_TOKEN_BUDGET,
            system=system,
            messages=anthropic_msgs,
            temperature=0.0,
        )
        if not response.content:
            raise ValueError(f"Empty response from Anthropic API for agent {agent.agent_id}")
        text          = response.content[0].text or ""
        prompt_tokens = response.usage.input_tokens or 0
        output_tokens = response.usage.output_tokens or 0
    else:
        contents = _to_gemini_contents(messages)
        # thinking_budget=0 disables Gemini 2.5's internal reasoning mode.
        # Without this, thinking tokens consume most of max_output_tokens,
        # leaving the model unable to complete code generation.
        thinking_cfg = types.ThinkingConfig(thinking_budget=0)
        response = _gemini_client.models.generate_content(
            model=_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.0,
                max_output_tokens=_TOKEN_BUDGET,
                thinking_config=thinking_cfg,
            ),
        )
        text          = response.text or ""
        usage         = response.usage_metadata
        prompt_tokens = usage.prompt_token_count or 0
        output_tokens = usage.candidates_token_count or 0

    return text, prompt_tokens + output_tokens, output_tokens


def _cull_check(state: SimState, agent: AgentProfile, total_tokens: int, output_tokens: int) -> bool:
    """Cull based on output tokens only — prompt tokens are shared context, not agent output cost."""
    state["token_usage"][agent.agent_id] = (
        state["token_usage"].get(agent.agent_id, 0) + total_tokens
    )
    cumulative_output = state["output_token_usage"].get(agent.agent_id, 0) + output_tokens
    state["output_token_usage"][agent.agent_id] = cumulative_output
    return cumulative_output > _TOKEN_BUDGET * 3


def build_chain_graph(
    agents: list[AgentProfile],
    scenario_brief: str,
    handoff_prompts: dict[int, str] | None = None,
    default_handoff: str | None = "Based on all contributions above, now provide your response.",
) -> StateGraph:
    """Sequential chain topology: agent[0] → agent[1] → ... → END.

    default_handoff: injected between steps when no explicit prompt is in handoff_prompts.
    Pass None to run with no injected prompt at all (pure continuation).
    """
    graph = StateGraph(SimState)

    for i, agent in enumerate(agents):
        node_name = agent.agent_id

        def make_node(a: AgentProfile, idx: int):
            def node_fn(state: SimState) -> SimState:
                if a.agent_id not in state["active_agent_ids"]:
                    return state

                msgs = list(state["messages"])
                if idx > 0:
                    hp = (handoff_prompts or {}).get(idx, default_handoff)
                    if hp is not None:
                        msgs = msgs + [{"role": "user", "content": hp}]

                text, total_tokens, output_tokens = _call_agent(a, msgs, state["scenario_brief"])

                if _cull_check(state, a, total_tokens, output_tokens):
                    state["active_agent_ids"].remove(a.agent_id)
                    state["cull_events"].append({
                        "agent_id": a.agent_id,
                        "turn": state["turn_count"],
                        "reason": "token_budget_exceeded",
                    })
                    return state

                state["messages"].append({"role": "assistant", "content": f"[{a.agent_id}]: {text}"})
                state["turn_count"] += 1

                if idx > 0:
                    state["routing_log"].append({
                        "from": agents[idx - 1].agent_id,
                        "to": a.agent_id,
                        "turn": state["turn_count"],
                    })

                return state
            return node_fn

        graph.add_node(node_name, make_node(agent, i))

    graph.set_entry_point(agents[0].agent_id)
    for i in range(len(agents) - 1):
        graph.add_edge(agents[i].agent_id, agents[i + 1].agent_id)
    graph.add_edge(agents[-1].agent_id, END)

    return graph


def build_flat_graph(
    agents: list[AgentProfile],
    max_rounds: int = 2,
    closing_prompt: str | None = None,
) -> StateGraph:
    """
    Flat (round-table) topology.
    Every agent sees the full conversation history each turn.
    Runs max_rounds complete circuits — each agent speaks once per round.

    closing_prompt: if set, adds a final synthesis step using agents[0] after
    all rounds. Used in the topology × handoff factorial to equip flat topology
    with an explicit commit instruction matching what chain topology receives.
    """
    graph = StateGraph(SimState)

    # Track which round we're in via a counter node
    def make_agent_node(a: AgentProfile, round_idx: int, agent_idx: int, total_agents: int):
        def node_fn(state: SimState) -> SimState:
            if a.agent_id not in state["active_agent_ids"]:
                return state

            # Each agent explicitly addresses the group
            group_context = (
                f"[Round {round_idx + 1} — {a.agent_id} speaking to the full team]\n"
                f"Read all prior contributions above. Respond to the group."
            )
            messages_with_context = list(state["messages"]) + [
                {"role": "user", "content": group_context}
            ]

            text, total_tokens, output_tokens = _call_agent(a, messages_with_context, state["scenario_brief"])

            if _cull_check(state, a, total_tokens, output_tokens):
                state["active_agent_ids"].remove(a.agent_id)
                state["cull_events"].append({
                    "agent_id": a.agent_id,
                    "turn": state["turn_count"],
                    "reason": "token_budget_exceeded",
                })
                return state

            state["messages"].append({
                "role": "assistant",
                "content": f"[{a.agent_id} | Round {round_idx + 1}]: {text}",
            })
            state["turn_count"] += 1

            # Log routing: flat topology means everyone routes to everyone
            for other in state["active_agent_ids"]:
                if other != a.agent_id:
                    state["routing_log"].append({
                        "from": a.agent_id,
                        "to": other,
                        "turn": state["turn_count"],
                    })

            return state
        return node_fn

    node_sequence = []
    for round_idx in range(max_rounds):
        for agent_idx, agent in enumerate(agents):
            node_name = f"{agent.agent_id}_r{round_idx}"
            graph.add_node(node_name, make_agent_node(agent, round_idx, agent_idx, len(agents)))
            node_sequence.append(node_name)

    graph.set_entry_point(node_sequence[0])
    for i in range(len(node_sequence) - 1):
        graph.add_edge(node_sequence[i], node_sequence[i + 1])

    if closing_prompt is not None:
        synth_agent = agents[0]
        synth_node  = f"{synth_agent.agent_id}_synth"

        def make_synth_node(a: AgentProfile, prompt: str):
            def node_fn(state: SimState) -> SimState:
                if a.agent_id not in state["active_agent_ids"]:
                    return state
                msgs = list(state["messages"]) + [{"role": "user", "content": prompt}]
                text, total_tokens, output_tokens = _call_agent(a, msgs, state["scenario_brief"])
                if _cull_check(state, a, total_tokens, output_tokens):
                    return state
                state["messages"].append({
                    "role": "assistant",
                    "content": f"[{a.agent_id}_synthesis]: {text}",
                })
                state["turn_count"] += 1
                return state
            return node_fn

        graph.add_node(synth_node, make_synth_node(synth_agent, closing_prompt))
        graph.add_edge(node_sequence[-1], synth_node)
        graph.add_edge(synth_node, END)
    else:
        graph.add_edge(node_sequence[-1], END)

    return graph


def run_simulation(
    agents: list[AgentProfile],
    scenario_brief: str,
    phase: str,
    topology: str = "chain",
    flat_rounds: int = 2,
    **kwargs,
) -> SimState:
    run_id = str(uuid.uuid4())

    initial_state: SimState = {
        "run_id": run_id,
        "phase": phase,
        "scenario_brief": scenario_brief,
        "messages": [{"role": "user", "content": scenario_brief}],
        "turn_count": 0,
        "token_usage": {},
        "output_token_usage": {},
        "cull_events": [],
        "active_agent_ids": [a.agent_id for a in agents],
        "routing_log": [],
        "state_snapshot": None,
    }

    if topology == "chain":
        graph = build_chain_graph(
            agents, scenario_brief,
            handoff_prompts=kwargs.get("chain_handoff_prompts"),
            default_handoff=kwargs.get("default_handoff", "Based on all contributions above, now provide your response."),
        )
    elif topology == "flat":
        graph = build_flat_graph(agents, max_rounds=flat_rounds, closing_prompt=kwargs.get("closing_prompt"))
    else:
        raise NotImplementedError(f"Topology '{topology}' not yet implemented.")

    compiled = graph.compile()
    final_state = compiled.invoke(initial_state)
    return final_state
