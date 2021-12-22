from typing import List, Set, Tuple
from Definitions import Agent


class CBS:
    def __init__(self, agents: List[Agent]):
        self.agents: List[Agent] = agents

    def solve(self, agents, random_wait_at_source=False, sequential_exit=False):
        plan: List[List[Tuple[int, int]]] = []
        solutions = []
        return plan
