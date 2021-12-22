from EnvironmentUtils import generate_rand_agents
from time import time
from BFS import generate_rnd_bfs
from RND import generate_rnd_plan
from LNS_PP import generate_lns_rnd_plan


def generate_lns_rnd_example(warehouse, waves_per_warehouse):
    agents = generate_rand_agents(warehouse, waves_per_warehouse)

    t0 = time()
    plan = generate_lns_rnd_plan(warehouse, agents)
    t1 = time()
    return plan, t0, t1


def generate_rnd_example(warehouse, waves_per_warehouse):
    agents = generate_rand_agents(warehouse, waves_per_warehouse)

    t0 = time()
    plan = generate_rnd_plan(warehouse, agents)
    t1 = time()
    return plan, t0, t1


def generate_bfs_example(warehouse):
    bfs = generate_rnd_bfs(warehouse)

    t0 = time()
    plan = bfs.generate_plan()
    t1 = time()
    return plan, t0, t1


def generate_example(warehouse, waves_per_warehouse, algorithm_name):
    if algorithm_name == "BFS":
        plan, t0, t1 = generate_bfs_example(warehouse)

    elif algorithm_name == "RND":
        plan, t0, t1 = generate_rnd_example(warehouse, waves_per_warehouse)

    elif algorithm_name == "LNS_RND":
        plan, t0, t1 = generate_lns_rnd_example(warehouse, waves_per_warehouse)

    else:
        print("Unsupported algorithm_name.\n", "Currently supports:", "BFS, RND")
        return [[]], -1

    running_time = round(t1 - t0, 4)
    return plan, running_time
