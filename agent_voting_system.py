from typing import List, Dict
import random
import os

class Agent:
    def __init__(self, name: str, domain: str):
        self.name = name
        self.domain = domain

    def propose(self, task: str) -> str:
        """Return a human-readable proposal description for the given task."""
        return f"{self.name} proposes solution for '{task}'"

    def vote(self, proposals: List[str]) -> str:
        """Vote for one of the proposal descriptions. This is currently random for demo purposes."""
        return random.choice(proposals)  # Simplified voting logic

    def perform(self, task: str) -> None:
        """Placeholder for executing the assigned task once this agent wins the vote."""
        print(f"{self.name} is now executing the task: '{task}'\n")


class Elector:
    def __init__(self, state_name: str, weight: int, agents: List[Agent]):
        self.state_name = state_name
        self.weight = weight
        self.agents = agents

    def conduct_state_vote(self, task: str) -> Dict["Agent", int]:
        """Conduct an intra-state vote among this state's agents.

        Returns a mapping of the winning *Agent* to this state's electoral weight.
        """

        # Each agent comes up with a proposal description. We keep a mapping so that we
        # can recover the originating agent after the vote.
        proposal_to_agent = {agent.propose(task): agent for agent in self.agents}

        proposals = list(proposal_to_agent.keys())

        # Each agent votes for one of the proposal descriptions.
        votes = [agent.vote(proposals) for agent in self.agents]

        # Count votes per proposal description
        tally: Dict[str, int] = {}
        for v in votes:
            tally[v] = tally.get(v, 0) + 1

        # Determine winning proposal description
        winning_proposal = max(tally.items(), key=lambda x: x[1])[0]

        winning_agent = proposal_to_agent[winning_proposal]

        # Return mapping of winning agent → state weight
        return {winning_agent: self.weight}


class Coordinator:
    def __init__(self, electors: List[Elector]):
        self.electors = electors

    def decide(self, task: str) -> "Agent":
        """Run the electoral college voting process and return the winning *Agent*."""

        tally: Dict[Agent, int] = {}
        vote_detail: Dict[Agent, List[str]] = {}

        for elector in self.electors:
            state_result = elector.conduct_state_vote(task)
            for agent, weight in state_result.items():
                tally[agent] = tally.get(agent, 0) + weight
                vote_detail.setdefault(agent, []).append(elector.state_name)

        # Determine overall winner by electoral weight
        winner_agent = max(tally.items(), key=lambda x: x[1])[0]

        # --- Evaluation metrics ---------------------------------------------------------
        total_votes = sum(tally.values())
        consensus_ratio = tally[winner_agent] / total_votes if total_votes else 0

        print("Evaluation:")
        print("Total electoral votes:", total_votes)
        print("Winning agent:", winner_agent.name)
        print("Votes received:", tally[winner_agent])
        print("States supporting:", vote_detail[winner_agent])
        print("Consensus ratio:", round(consensus_ratio, 2))

        # Delegate the task to the winning agent
        winner_agent.perform(task)

        return winner_agent


if __name__ == "__main__":
    try:
        # Import lazily to avoid dependency issues if OpenAI isn't installed.
        from chatgpt_agent import ChatGPTAgent  # noqa: WPS433

        _USE_GPT = bool(os.getenv("OPENAI_API_KEY"))
    except ModuleNotFoundError:
        _USE_GPT = False

    Base = ChatGPTAgent if _USE_GPT else Agent

    data_agents = [Base(f"DataAgent{i+1}", "Data") for i in range(2)]
    planning_agents = [Base(f"Planner{i+1}", "Planning") for i in range(3)]
    security_agents = [Base(f"SecurityAgent{i+1}", "Security") for i in range(1)]

    electors = [
        Elector("DataState", 5, data_agents),
        Elector("PlanningState", 10, planning_agents),
        Elector("SecurityState", 3, security_agents),
    ]

    coordinator = Coordinator(electors)
    winning_agent = coordinator.decide("Select best infrastructure plan")
    print("Task has been delegated to:", winning_agent.name)
