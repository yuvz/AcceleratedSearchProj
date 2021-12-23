import random
from EnvironmentUtils import find_route_using_Astar
from Utils import update_plan


def generate_rnd_plan(warehouse, routing_requests, sequential_exit=False):
    num_of_routing_requests = len(routing_requests)
    priority_order = random.sample(range(num_of_routing_requests), num_of_routing_requests)
    plan = [[] for _ in range(len(routing_requests))]
    route_number = 0

    for route_number, i in enumerate(priority_order):
        route = find_route_using_Astar(warehouse, plan, routing_requests[i], route_number == 0,
                                       route_number if sequential_exit else 0)
        update_plan(plan, i, route)
        if route_number % 5 == 0:
            print("Found route for", route_number + 1, "out of", num_of_routing_requests, "routing_requests")

    print("***")
    print("Done: Found route for", route_number + 1, "out of", num_of_routing_requests, "routing_requests")
    return plan
