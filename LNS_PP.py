import random
from math import sqrt
from EnvironmentUtils import find_route_using_Astar
from RND import generate_rnd_plan
from Utils import update_plan

LNS_ITERATIONS = 5
NEIGHBORHOOD_SIZE = 15
AGENT_BASED_NEIGHBORHOOD_ITERATIONS = 100


def neighborhood_sum_of_costs(plan, neighborhood):
    return sum([len(plan[i]) for i in neighborhood])


def pick_lower_sum_of_costs_plan(plan, backup_plan, neighborhood):
    plan_cost = neighborhood_sum_of_costs(plan, neighborhood)
    backup_plan_cost = neighborhood_sum_of_costs(backup_plan, neighborhood)

    if plan_cost < backup_plan_cost:
        print("cost was", backup_plan_cost, "and is now", plan_cost)
        return plan
    return backup_plan


def replan(warehouse, plan, neighborhood, routing_requests):
    for route_number, i in enumerate(neighborhood):
        route = find_route_using_Astar(warehouse, plan, routing_requests[i], route_number == 0)
        update_plan(plan, i, route)
    return plan


def erase_routes(plan, neighborhood):
    for i in neighborhood:
        plan[i] = []


def pick_random_neighborhood(routing_requests, *unused_variables):
    num_of_routing_requests = len(routing_requests)
    neighborhood = random.sample(range(num_of_routing_requests), round(sqrt(num_of_routing_requests)))

    random.shuffle(neighborhood)
    return neighborhood


# global variable for agent_based_neighborhood function.
tabu_list = []


def random_walk(warehouse, plan, neighborhood, chosen_agent_id, agents):
    """
    tries to make random steps that will reduce the length of the route of chosen_agent_id and adds the agents
    that are in the way to neighborhood.
    :param warehouse:
    :param plan:
    :param neighborhood:
    :param chosen_agent_id:
    :param agents:
    :return:
    """
    time = random.randrange(len(plan[chosen_agent_id]))
    curr_coordinates = plan[chosen_agent_id][time]
    chosen_agent_dest = agents[chosen_agent_id].destination.destination_id
    coordinates_to_vertex = warehouse.vertices[curr_coordinates[0]][curr_coordinates[1]]
    neighbors_to_consider = [neighbor for neighbor in coordinates_to_vertex.neighbors if
                             time + 1 + neighbor.get_destination_distance(chosen_agent_dest) < len(
                                 plan[chosen_agent_id])]
    while len(neighbors_to_consider) > 0 and len(neighborhood) < NEIGHBORHOOD_SIZE:
        neighbor = random.choice(neighbors_to_consider)
        for i in range(len(agents)):
            if len(plan[i]) > time + 1:
                if plan[i][time + 1] == neighbor.coordinates or (
                        plan[i][time] == neighbor.coordinates and plan[i][time + 1] == curr_coordinates):
                    neighborhood.add(i)
        coordinates = neighbor.coordinates
        coordinates_to_vertex = warehouse.vertices[coordinates[0]][coordinates[1]]
        time += 1
        neighbors_to_consider = [neighbor for neighbor in coordinates_to_vertex.neighbors if
                                 time + 1 + neighbor.get_destination_distance(chosen_agent_dest) < len(
                                     plan[chosen_agent_id])]


def agent_based_neighborhood(agents, warehouse, plan):
    """
    huristic to find a good neighborhood to replan its routes.
    Finds the route with max delay (the gap between bfs time to actual route time) that isn't in the global tabu list
    and picks a random step and tries to make progress through neighbors with less time to destination.
    it finds the agents that are in the way and generates the neghborhood.
    :param warehouse:
    :param agents:
    :param plan:
    :return:
    """
    bfs_list = [agent.source.get_destination_distance(agent.destination.destination_id) for agent in agents]
    delays_list = [len(route) - bfs_list[i] for i, route in enumerate(plan)]
    global tabu_list
    delays_list_without_tabu = [delays_list[i] for i in range(len(agents)) if i not in tabu_list]
    max_delay = max(delays_list_without_tabu)
    if len(tabu_list) == len(agents) or max_delay == 0:
        tabu_list = []
        max_delay = max(delays_list)
    agents_max_delay_ids = [i for i in range(len(agents)) if delays_list[i] == max_delay and i not in tabu_list]
    chosen_agent_id = random.choice(agents_max_delay_ids)
    tabu_list.append(chosen_agent_id)
    neighborhood = set()
    neighborhood.add(chosen_agent_id)
    for i in range(AGENT_BASED_NEIGHBORHOOD_ITERATIONS):
        if len(neighborhood) == NEIGHBORHOOD_SIZE:
            break
        random_walk(warehouse, plan, neighborhood, chosen_agent_id, agents)
        chosen_agent_id = random.choice(list(neighborhood))
        set(neighborhood)
    return list(neighborhood)


def generate_lns_rnd_plan(warehouse, routing_requests, neighborhood_picking_function=agent_based_neighborhood):
    """
    Supported neighborhood_picking_function: [pick_random_neighborhood, agent_based_neighborhood]
    """
    plan = generate_rnd_plan(warehouse, routing_requests, True)

    for _ in range(LNS_ITERATIONS):
        plan_backup = plan.copy()

        # neighborhood contains the list of indexes of routing_requests to replan for
        neighborhood = neighborhood_picking_function(routing_requests, warehouse, plan)
        erase_routes(plan, neighborhood)
        plan = replan(warehouse, plan, neighborhood, routing_requests)
        plan = pick_lower_sum_of_costs_plan(plan, plan_backup, neighborhood)

    return plan

# TODO: change RND to PP by adding rapid-random-restarts
