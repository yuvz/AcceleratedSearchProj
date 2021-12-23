import random
from time import time
from EnvironmentUtils import generate_rand_routing_requests, generate_rand_routing_request
from BFS import generate_bfs_plan_for_first_routing_request
from RND import generate_rnd_plan
from LNS_PP import generate_lns_rnd_plan
from RouteGeneration import generate_ideal_path_with_splits_plan_for_first_routing_request, \
    generate_midpoints_restricted_plan_for_first_routing_request, \
    generate_random_obstacles_restricted_plan_for_first_routing_request

WAVES_PER_WAREHOUSE = [10, 1, 10, 1]
K_SAMPLE_SIZE = 5


def generate_plan(warehouse, routing_requests, plan_generation_algorithm, optional_argument=None):
    """
    is_split_at_midpoint used for midpoints_restricted only
    """
    t0 = time()
    if optional_argument:
        plan = plan_generation_algorithm(warehouse, routing_requests, optional_argument)
    else:
        plan = plan_generation_algorithm(warehouse, routing_requests)
    t1 = time()
    return plan, t0, t1


def generate_midpoints_restricted_example(warehouse, is_split_at_midpoint=False):
    routing_requests = generate_rand_routing_request(warehouse)

    return generate_plan(warehouse, routing_requests, generate_midpoints_restricted_plan_for_first_routing_request,
                         is_split_at_midpoint)


def generate_midpoints_restricted_with_splits_example(warehouse):
    return generate_midpoints_restricted_example(warehouse, True)


def generate_ideal_path_with_splits_example(warehouse):
    routing_requests = generate_rand_routing_request(warehouse)

    return generate_plan(warehouse, routing_requests, generate_ideal_path_with_splits_plan_for_first_routing_request)


def generate_random_obstacles_restricted_example(warehouse):
    routing_requests = generate_rand_routing_request(warehouse)
    obstacle_patterns = ["cross", "square", "vertical_line", "horizontal_line", "dot"]

    return generate_plan(warehouse, routing_requests,
                         generate_random_obstacles_restricted_plan_for_first_routing_request, obstacle_patterns)


def generate_lns_rnd_example(warehouse, waves_per_warehouse):
    routing_requests = generate_rand_routing_requests(warehouse, waves_per_warehouse)
    return generate_plan(warehouse, routing_requests, generate_lns_rnd_plan)


def generate_rnd_example(warehouse, waves_per_warehouse):
    routing_requests = generate_rand_routing_requests(warehouse, waves_per_warehouse)
    return generate_plan(warehouse, routing_requests, generate_rnd_plan)


def generate_bfs_example(warehouse):
    routing_requests = generate_rand_routing_request(warehouse)
    return generate_plan(warehouse, routing_requests, generate_bfs_plan_for_first_routing_request)


def generate_example(warehouse, algorithm_name):
    if algorithm_name == "BFS":
        plan, t0, t1 = generate_bfs_example(warehouse)

    elif algorithm_name == "RND":
        plan, t0, t1 = generate_rnd_example(warehouse, WAVES_PER_WAREHOUSE)

    elif algorithm_name == "LNS_RND":
        plan, t0, t1 = generate_lns_rnd_example(warehouse, WAVES_PER_WAREHOUSE)

    elif algorithm_name == "ROR":
        plan, t0, t1 = generate_random_obstacles_restricted_example(warehouse)

    elif algorithm_name == "k-ROR":
        plan, t0, t1 = generate_random_obstacles_restricted_example(warehouse)
        plan = random.sample(plan, K_SAMPLE_SIZE)

    elif algorithm_name == "IPWS":
        plan, t0, t1 = generate_ideal_path_with_splits_example(warehouse)

    elif algorithm_name == "k-IPWS":
        plan, t0, t1 = generate_ideal_path_with_splits_example(warehouse)
        plan = random.sample(plan, K_SAMPLE_SIZE)

    elif algorithm_name == "MPR":
        plan, t0, t1 = generate_midpoints_restricted_example(warehouse)

    elif algorithm_name == "k-MPR":
        plan, t0, t1 = generate_midpoints_restricted_example(warehouse)
        plan = random.sample(plan, K_SAMPLE_SIZE)

    elif algorithm_name == "MPR_WS":
        plan, t0, t1 = generate_midpoints_restricted_with_splits_example(warehouse)

    elif algorithm_name == "k-MPR_WS":
        plan, t0, t1 = generate_midpoints_restricted_with_splits_example(warehouse)
        plan = random.sample(plan, K_SAMPLE_SIZE)

    else:
        print("Unsupported algorithm_name.\n", "Currently supports:", "BFS, RND, LNS_RND")
        return [[]], -1

    running_time = round(t1 - t0, 4)
    return plan, running_time
