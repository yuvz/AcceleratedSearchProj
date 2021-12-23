from time import time
from random import sample
from EnvironmentUtils import generate_rand_routing_requests, generate_rand_routing_request
from BFS import generate_bfs_plan_for_first_routing_request
from RND import generate_rnd_plan
from LNS_PP import generate_lns_rnd_plan
from RouteGeneration import generate_random_obstacles_restricted_plan

K_SAMPLE_SIZE = 5


def generate_plan(warehouse, routing_requests, plan_generation_algorithm):
    t0 = time()
    plan = plan_generation_algorithm(warehouse, routing_requests)
    t1 = time()
    return plan, t0, t1


def generate_random_obstacles_restricted_example(warehouse):
    routing_requests = generate_rand_routing_request(warehouse)

    obstacle_patterns = ["cross", "square", "vertical_line", "horizontal_line", "dot"]
    # obstacle_patterns = ["horizontal_line"]
    t0 = time()
    plan = generate_random_obstacles_restricted_plan(warehouse, routing_requests[0], obstacle_patterns)
    t1 = time()
    return plan, t0, t1


def generate_lns_rnd_example(warehouse, waves_per_warehouse):
    routing_requests = generate_rand_routing_requests(warehouse, waves_per_warehouse)
    return generate_plan(warehouse, routing_requests, generate_lns_rnd_plan)


def generate_rnd_example(warehouse, waves_per_warehouse):
    routing_requests = generate_rand_routing_requests(warehouse, waves_per_warehouse)
    return generate_plan(warehouse, routing_requests, generate_rnd_plan)


def generate_bfs_example(warehouse):
    routing_requests = generate_rand_routing_request(warehouse)
    return generate_plan(warehouse, routing_requests, generate_bfs_plan_for_first_routing_request)


def generate_example(warehouse, waves_per_warehouse, algorithm_name):
    if algorithm_name == "BFS":
        plan, t0, t1 = generate_bfs_example(warehouse)

    elif algorithm_name == "RND":
        plan, t0, t1 = generate_rnd_example(warehouse, waves_per_warehouse)

    elif algorithm_name == "LNS_RND":
        plan, t0, t1 = generate_lns_rnd_example(warehouse, waves_per_warehouse)

    elif algorithm_name == "ROR":
        plan, t0, t1 = generate_random_obstacles_restricted_example(warehouse)

    elif algorithm_name == "K-ROR":
        plan, t0, t1 = generate_random_obstacles_restricted_example(warehouse)
        plan = sample(plan, K_SAMPLE_SIZE)

    else:
        print("Unsupported algorithm_name.\n", "Currently supports:", "BFS, RND, LNS_RND")
        return [[]], -1

    running_time = round(t1 - t0, 4)
    return plan, running_time
