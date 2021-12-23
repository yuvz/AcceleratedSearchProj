from copy import deepcopy
from itertools import combinations
from typing import List, Tuple, Dict, Set
import numpy as np

from CBS import constraints
from CBS.constraint_tree import CTNode
from CBS.constraints import Constraints
from RoutingRequest import RoutingRequest
from EnvironmentUtils import find_route_using_Astar
from heapq import heappush, heappop


class CBS:
    def __init__(self, warehouse, agents: List[RoutingRequest]):
        self.warehouse = warehouse
        self.agents: List[RoutingRequest] = agents

    '''
        You can use your own assignment function, the default algorithm greedily assigns
        the closest goal to each start.
    '''

    def solve(self, debug: bool = False, max_iter=100):
        plan = [[] for _ in range(len(self.agents))]

        # Compute path for each agent using space-time Astar
        agent_to_route_dict = dict((agent, find_route_using_Astar(self.warehouse, plan, agent)) for agent in self.agents)

        # Build conflict tree
        open = []
        if all(len(path) != 0 for path in agent_to_route_dict.values()):
            # Make root node
            node = CTNode(constraints, agent_to_route_dict)
            # Min heap for quick extraction
            open.append(node)

        iter_ = 0
        while open and iter_ < max_iter:
            iter_ += 1

            results = []

            self.search_node(heappop(open), results)

            for result in results:
                if len(result) == 1:
                    if debug:
                        print('CBS_MAPF: Paths found after about {0} iterations'.format(4 * iter_))
                    return result[0]
                if result[0]:
                    heappush(open, result[0])
                if result[1]:
                    heappush(open, result[1])

        if debug:
            print('CBS-MAPF: Open set is empty, no paths found.')

        return np.array([])

        return plan

    def search_node(self, best: CTNode, results):
        agent_i, agent_j, time_of_conflict = self.validate_paths(self.agents, best)

        # If there is no conflict, validate_paths returns (None, None, -1)
        if agent_i is None:
            results.append((self.reformat(self.agents, best.solution),))
            return
        # Calculate new constraints
        agent_i_constraint = self.calculate_constraints(best, agent_i, agent_j, time_of_conflict)
        agent_j_constraint = self.calculate_constraints(best, agent_j, agent_i, time_of_conflict)

        # Calculate new paths
        agent_i_path = self.calculate_path(agent_i,
                                           agent_i_constraint,
                                           self.calculate_goal_times(best, agent_i, self.agents))
        agent_j_path = self.calculate_path(agent_j,
                                           agent_j_constraint,
                                           self.calculate_goal_times(best, agent_j, self.agents))

        # Replace old paths with new ones in solution
        solution_i = best.solution
        solution_j = deepcopy(best.solution)
        solution_i[agent_i] = agent_i_path
        solution_j[agent_j] = agent_j_path

        node_i = None
        if all(len(path) != 0 for path in solution_i.values()):
            node_i = CTNode(agent_i_constraint, solution_i)

        node_j = None
        if all(len(path) != 0 for path in solution_j.values()):
            node_j = CTNode(agent_j_constraint, solution_j)

        results.append((node_i, node_j))

    '''
    Pair of agent, point of conflict
    '''
    def validate_paths(self, agents, node: CTNode):
        # Check collision pair-wise
        for agent_i, agent_j in combinations(agents, 2):
            time_of_conflict = self.safe_distance(node.solution, agent_i, agent_j)
            # time_of_conflict=1 if there is not conflict
            if time_of_conflict == -1:
                continue
            return agent_i, agent_j, time_of_conflict
        return None, None, -1


    def safe_distance(self, solution: Dict[RoutingRequest, np.ndarray], agent_i: RoutingRequest, agent_j: RoutingRequest) -> int:
        for idx, (point_i, point_j) in enumerate(zip(solution[agent_i], solution[agent_j])):
            if self.dist(point_i, point_j) > 2*self.robot_radius:
                continue
            return idx
        return -1

    @staticmethod
    def dist(point1: np.ndarray, point2: np.ndarray) -> int:
        return int(np.linalg.norm(point1-point2, 2))  # L2 norm

    def calculate_constraints(self, node: CTNode,
                                    constrained_agent: RoutingRequest,
                                    unchanged_agent: RoutingRequest,
                                    time_of_conflict: int) -> Constraints:
        contrained_path = node.solution[constrained_agent]
        unchanged_path = node.solution[unchanged_agent]

        pivot = unchanged_path[time_of_conflict]
        conflict_end_time = time_of_conflict
        try:
            while self.dist(contrained_path[conflict_end_time], pivot) < 2*self.robot_radius:
                conflict_end_time += 1
        except IndexError:
            pass
        return node.constraints.fork(constrained_agent, tuple(pivot.tolist()), time_of_conflict, conflict_end_time)

    def calculate_goal_times(self, node: CTNode, agent: RoutingRequest, agents: List[RoutingRequest]):
        solution = node.solution
        goal_times = dict()
        for other_agent in agents:
            if other_agent == agent:
                continue
            time = len(solution[other_agent]) - 1
            goal_times.setdefault(time, set()).add(tuple(solution[other_agent][time]))
        return goal_times

    '''
    Calculate the paths for all agents with space-time constraints
    '''
    def calculate_path(self, agent: RoutingRequest,
                       constraints: Constraints,
                       goal_times: Dict[int, Set[Tuple[int, int]]]) -> np.ndarray:
        return self.st_planner.plan(agent.start,
                                    agent.goal,
                                    constraints.setdefault(agent, dict()),
                                    semi_dynamic_obstacles=goal_times,
                                    max_iter=self.low_level_max_iter,
                                    debug=self.debug)

    '''
    Reformat the solution to a numpy array
    '''
    @staticmethod
    def reformat(agents: List[RoutingRequest], solution: Dict[RoutingRequest, np.ndarray]):
        solution = CBS.pad(solution)
        reformatted_solution = []
        for agent in agents:
            reformatted_solution.append(solution[agent])
        return np.array(reformatted_solution)

    '''
    Pad paths to equal length, inefficient but well..
    '''
    @staticmethod
    def pad(solution: Dict[RoutingRequest, np.ndarray]):
        max_ = max(len(path) for path in solution.values())
        for agent, path in solution.items():
            if len(path) == max_:
                continue
            padded = np.concatenate([path, np.array(list([path[-1]])*(max_-len(path)))])
            solution[agent] = padded
        return solution
