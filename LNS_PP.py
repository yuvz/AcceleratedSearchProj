import random
from math import sqrt
from EnvironmentUtils import find_route_using_Astar
from RND import generate_rnd_plan
from Utils import update_plan

LNS_ITERATIONS = 1


#   No longer in use    #
# def neighborhood_makespan(plan, neighborhood):
#     return max([len(plan[i]) for i in neighborhood])
#
# def get_worst_makespan_agents(plan):
#     worst_makespan = max(len(route) for route in plan)
#     return [i for i in range(len(plan)) if len(plan[i]) == worst_makespan]


def neighborhood_sum_of_costs(plan, neighborhood):
    return sum([len(plan[i]) for i in neighborhood])


def pick_lower_sum_of_costs_plan(plan, backup_plan, neighborhood):
    plan_cost = neighborhood_sum_of_costs(plan, neighborhood)
    backup_plan_cost = neighborhood_sum_of_costs(backup_plan, neighborhood)

    if plan_cost < backup_plan_cost:
        print("cost was", backup_plan_cost, "and is now", plan_cost)
        return plan
    return backup_plan


def replan(warehouse, plan, neighborhood, agents):
    for route_number, i in enumerate(neighborhood):
        route = find_route_using_Astar(warehouse, plan, agents[i], route_number == 0, True)
        update_plan(plan, i, route)
    return plan


def erase_routes(plan, neighborhood):
    for i in neighborhood:
        plan[i] = []


def pick_random_neighborhood(agents):
    num_of_agents = len(agents)
    neighborhood = random.sample(range(num_of_agents), round(sqrt(num_of_agents)))

    random.shuffle(neighborhood)
    return neighborhood


def generate_lns_rnd_plan(warehouse, agents, neighborhood_picking_function=pick_random_neighborhood):
    plan = generate_rnd_plan(warehouse, agents, False)

    for _ in range(LNS_ITERATIONS):
        plan_backup = plan.copy()

        # neighborhood contains the list of indexes of agents to replan for
        neighborhood = neighborhood_picking_function(agents)
        erase_routes(plan, neighborhood)
        plan = replan(warehouse, plan, neighborhood, agents)
        plan = pick_lower_sum_of_costs_plan(plan, plan_backup, neighborhood)

    return plan

# TODO: change RND to PP by adding rapid-random-restarts
