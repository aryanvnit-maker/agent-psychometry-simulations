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

_MODEL = os.getenv("MODEL", "gemini-2.5-flash")
_TOKEN_BUDGET = int(os.getenv("AGENT_TOKEN_BUDGET", "800"))

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class SimState(TypedDict):
    run_id: str
    phase: str
    scenario_brief: str
    messages: Annotated[list[dict], add_messages]
    turn_count: int
    token_usage: dict[str, int]       # agent_id -> cumulative tokens used
    cull_events: list[dict]           # {agent_id, turn, reason}
    active_agent_ids: list[str]
    routing_log: list[dict]           # {from, to, turn} for coalition detection
    state_snapshot: dict | None       # saved on deadlock


def _to_gemini_contents(messages) -> list[dict]:
    """Convert LangGraph messages (dicts or LangChain objects) to Gemini contents format."""
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


def _call_agent(agent: AgentProfile, messages: list[dict], scenario_brief: str) -> tuple[str, int]:
    system = build_constitution(agent)
    contents = _to_gemini_contents(messages)
    response = _client.models.generate_content(
        model=_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.0,
            max_output_tokens=_TOKEN_BUDGET,
        ),
    )
    text = response.text
    usage = response.usage_metadata
    tokens_used = (usage.prompt_token_count or 0) + (usage.candidates_token_count or 0)
    return text, tokens_used


def _cull_check(state: SimState, agent: AgentProfile, tokens_this_turn: int) -> bool:
    """Return True if this agent should be culled."""
    cumulative = state["token_usage"].get(agent.agent_id, 0) + tokens_this_turn
    state["token_usage"][agent.agent_id] = cumulative
    return cumulative > _TOKEN_BUDGET * 3


def build_chain_graph(agents: list[AgentProfile], scenario_brief: str) -> StateGraph:
    """Sequential chain topology: agent[0] → agent[1] → ... → END."""
    graph = StateGraph(SimState)

    for i, agent in enumerate(agents):
        node_name = agent.agent_id

        def make_node(a: AgentProfile, idx: int):
            def node_fn(state: SimState) -> SimState:
                if a.agent_id not in state["active_agent_ids"]:
                    return state

                text, tokens = _call_agent(a, state["messages"], state["scenario_brief"])

                if _cull_check(state, a, tokens):
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


def run_simulation(
    agents: list[AgentProfile],
    scenario_brief: str,
    phase: str,
    topology: str = "chain",
) -> SimState:
    run_id = str(uuid.uuid4())

    initial_state: SimState = {
        "run_id": run_id,
        "phase": phase,
        "scenario_brief": scenario_brief,
        "messages": [{"role": "user", "content": scenario_brief}],
        "turn_count": 0,
        "token_usage": {},
        "cull_events": [],
        "active_agent_ids": [a.agent_id for a in agents],
        "routing_log": [],
        "state_snapshot": None,
    }

    if topology == "chain":
        graph = build_chain_graph(agents, scenario_brief)
    else:
        raise NotImplementedError(f"Topology '{topology}' not yet implemented. Build flat and hub_spoke next.")

    compiled = graph.compile()
    final_state = compiled.invoke(initial_state)
    return final_state
