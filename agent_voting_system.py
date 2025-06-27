# agent_voting_system.py

from typing import List, Dict
import random

class Agent:
    def __init__(self, name: str, domain: str):
        self.name = name
        self.domain = domain

    def propose(self, task: str) -> str:
        return f"{self.name} proposes solution for '{task}'"

    def vote(self, proposals: List[str]) -> str:
        return random.choice(proposals)  # Simplified voting logic


class Elector:
    def __init__(self, state_name: str, weight: int, agents: List[Agent]):
        self.state_name = state_name
        self.weight = weight
        self.agents = agents

    def conduct_state_vote(self, task: str) -> Dict[str, int]:
        proposals = [agent.propose(task) for agent in self.agents]
        votes = [agent.vote(proposals) for agent in self.agents]
        result = {}
        for vote in votes:
            result[vote] = result.get(vote, 0) + 1
        # Return the winning proposal with state weight
        winning = max(result.items(), key=lambda x: x[1])[0]
        return {winning: self.weight}


class Coordinator:
    def __init__(self, electors: List[Elector]):
        self.electors = electors

    def decide(self, task: str) -> str:
        tally: Dict[str, int] = {}
        for elector in self.electors:
            result = elector.conduct_state_vote(task)
            for proposal, weight in result.items():
                tally[proposal] = tally.get(proposal, 0) + weight
        winner = max(tally.items(), key=lambda x: x[1])[0]
        return winner


# Example setup
if __name__ == "__main__":
    data_agents = [Agent(f"DataAgent{i+1}", "Data") for i in range(2)]
    planning_agents = [Agent(f"Planner{i+1}", "Planning") for i in range(3)]
    security_agents = [Agent(f"SecurityAgent{i+1}", "Security") for i in range(1)]

    electors = [
        Elector("DataState", 5, data_agents),
        Elector("PlanningState", 10, planning_agents),
        Elector("SecurityState", 3, security_agents),
    ]

    coordinator = Coordinator(electors)
    final_decision = coordinator.decide("Select best infrastructure plan")
    print("\n🏛️ Final Decision:", final_decision)
