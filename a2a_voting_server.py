"""Minimal A2A server that wraps the electoral-vote `Coordinator`.

Run this module to expose a single endpoint (default: http://localhost:5000)
that conforms to Google's **Agent-to-Agent (A2A)** protocol.  Remote agents –
or the `a2a` CLI – can then delegate arbitrary tasks and receive the winning
agent's answer.

Example
-------
$ uv pip install -r requirements.txt   # or: pip install -r requirements.txt
$ export OPENAI_API_KEY="sk-..."       # optional, for GPT-4o backing
$ uv run a2a_voting_server.py

You can now inspect the agent card or send a task:

$ curl http://localhost:5000/.well-known/agent.json | jq
$ a2a send http://localhost:5000 "Design a data warehouse for e-commerce"
"""

from __future__ import annotations

import os
from typing import Dict, List
from python_a2a import A2AServer, run_server, skill
import socket  # NEW: for dynamic port picking

from agent_voting_system import Coordinator, Elector
from chatgpt_agent import ChatGPTAgent

def _build_demo_coordinator() -> Coordinator:
    """Return a demo coordinator populated with GPT-4o-backed agents."""

    # You can customise counts / weights via env-vars if you like.
    data_count = int(os.getenv("DATA_AGENT_COUNT", "2"))
    plan_count = int(os.getenv("PLANNING_AGENT_COUNT", "3"))
    sec_count = int(os.getenv("SECURITY_AGENT_COUNT", "1"))

    def make_agents(prefix: str, n: int, domain: str) -> List[ChatGPTAgent]:
        return [ChatGPTAgent(f"{prefix}{i+1}", domain) for i in range(n)]

    data_agents = make_agents("DataAgent", data_count, "Data Engineering")
    planning_agents = make_agents("Planner", plan_count, "Infrastructure Planning")
    security_agents = make_agents("SecurityAgent", sec_count, "Cyber-Security")

    electors = [
        Elector("DataState", 5, data_agents),
        Elector("PlanningState", 10, planning_agents),
        Elector("SecurityState", 3, security_agents),
    ]
    return Coordinator(electors)


# ---------------------------------------------------------------------------
# A2A server wrapper around the Coordinator
# ---------------------------------------------------------------------------


class VotingCoordinatorAgent(A2AServer):
    """Expose the `decide` method of `Coordinator` as an A2A skill."""

    def __init__(self, coordinator: Coordinator):
        super().__init__(
            name="ElectoralVotingCoordinator",
            description=(
                "Coordinator that uses a US-style electoral college among "
                "GPT-4o-backed agents to choose the single best proposal "
                "for a given task."
            ),
            version="0.1.0",
        )
        self._coordinator = coordinator

    # Define a single skill – other skills (metrics, etc.) could be added.
    @skill(
        name="decide_task",
        description="Run an electoral vote and return the winning agent's answer."
    )
    def decide_task(self, task: str) -> Dict[str, str]:
        """Return a structured response containing the winning agent and answer."""

        winning_agent = self._coordinator.decide(task)
        return {
            "agent": winning_agent.name,
            "domain": winning_agent.domain,
            "task": task,
        }


if __name__ == "__main__":
    coordinator = _build_demo_coordinator()

    agent_server = VotingCoordinatorAgent(coordinator)

    # Allow custom port via env-var; fall back to the next free one if occupied
    def _find_free_port(start: int = 5000, limit: int = 50) -> int:
        """Return the first free TCP port >= *start* (max *limit* ports checked)."""

        for p in range(start, start + limit):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    sock.bind(("", p))
                except OSError:
                    continue  # already in use – try next
                return p
        raise RuntimeError("No free ports available in range.")

    port_env = os.getenv("PORT")
    base_port = int(port_env) if port_env else 5000
    port = _find_free_port(base_port)

    if port != base_port:
        print(f"[⚠️] Port {base_port} busy – switching to {port}.")

    run_server(agent_server, host="0.0.0.0", port=port) 