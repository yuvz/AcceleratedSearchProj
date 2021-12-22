import random

from EnvironmentUtils import get_agent_and_framework
from Utils import update_plan


def generate_rnd_plan(warehouse, agents, sequential_exit=False):
    num_of_agents = len(agents)
    priority_order = random.sample(range(num_of_agents), num_of_agents)
    plan = [[] for _ in range(len(agents))]
    route_number = 0

    for route_number, i in enumerate(priority_order):
        agent, a_star_framework = get_agent_and_framework(agents, i)
        route = a_star_framework.space_time_search(warehouse, agent, plan, route_number == 0,
                                                   route_number if sequential_exit else 0)
        update_plan(plan, i, route)
        if route_number % 5 == 0:
            print("Found route for", route_number + 1, "out of", num_of_agents, "agents")

    print("***")
    print("Done: Found route for", route_number + 1, "out of", num_of_agents, "agents")
    return plan
