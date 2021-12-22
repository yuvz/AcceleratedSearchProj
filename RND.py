import random
from EnvironmentUtils import find_route_using_Astar
from Utils import update_plan


def generate_rnd_plan(warehouse, agents, sequential_exit=False):
    num_of_agents = len(agents)
    priority_order = random.sample(range(num_of_agents), num_of_agents)
    plan = [[] for _ in range(len(agents))]
    route_number = 0

    for route_number, i in enumerate(priority_order):
        route = find_route_using_Astar(warehouse, plan, agents[i], route_number == 0,
                                       route_number if sequential_exit else 0)
        update_plan(plan, i, route)
        if route_number % 5 == 0:
            print("Found route for", route_number + 1, "out of", num_of_agents, "agents")

    print("***")
    print("Done: Found route for", route_number + 1, "out of", num_of_agents, "agents")
    return plan
