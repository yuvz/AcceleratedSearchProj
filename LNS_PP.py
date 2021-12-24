import random
from math import sqrt
from EnvironmentUtils import find_route_using_Astar
from RND import generate_rnd_plan
from Utils import update_plan
import numpy as np

LNS_ITERATIONS = 5
NEIGHBORHOOD_SIZE = 15
AGENT_BASED_NEIGHBORHOOD_ITERATIONS = 100
INTERSECTION_THRESHOLD = 3
WEIGHTS_FACTOR = 0.01


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


def random_walk(warehouse, plan, neighborhood, chosen_routing_request_index, routing_requests):
    """
    tries to make random steps that will reduce the length of the route of chosen_agent_id and adds the agents
    that are in the way to neighborhood.
    :param warehouse:
    :param plan:
    :param neighborhood:
    :param chosen_routing_request_index:
    :param routing_requests:
    :return:
    """
    time = random.randrange(len(plan[chosen_routing_request_index]))
    curr_coordinates = plan[chosen_routing_request_index][time]
    chosen_routing_request_destination_id = routing_requests[chosen_routing_request_index].destination.destination_id
    while len(neighborhood) < NEIGHBORHOOD_SIZE:
        coordinates_to_vertex = warehouse.vertices[curr_coordinates[0]][curr_coordinates[1]]
        neighbors_to_consider = [neighbor for neighbor in coordinates_to_vertex.neighbors if
                                 time + 1 + neighbor.get_destination_distance(chosen_routing_request_destination_id) < len(
                                  plan[chosen_routing_request_index])]
        if len(neighbors_to_consider) == 0:
            break
        neighbor = random.choice(neighbors_to_consider)
        for i in range(len(routing_requests)):
            if len(plan[i]) > time + 1:
                if plan[i][time + 1] == neighbor.coordinates or (
                        plan[i][time] == neighbor.coordinates and plan[i][time + 1] == curr_coordinates):
                    neighborhood.add(i)
        curr_coordinates = neighbor.coordinates
        time += 1


def agent_based_neighborhood(routing_requests, warehouse, plan):
    """
    huristic to find a good neighborhood to replan its routes.
    Finds the route with max delay (the gap between bfs time to actual route time) that isn't in the global tabu list
    and picks a random step and tries to make progress through neighbors with less time to destination.
    it finds the agents that are in the way and generates the neghborhood.
    :param warehouse:
    :param routing_requests:
    :param plan:
    :return:
    """
    shortest_routs_list = [routing_request.source.get_destination_distance(routing_request.destination.destination_id) for routing_request in routing_requests]
    delays_list = [len(route) - shortest_routs_list[i] for i, route in enumerate(plan)]
    global tabu_list
    delays_list_without_tabu = [delays_list[i] for i in range(len(routing_requests)) if i not in tabu_list]
    max_delay = max(delays_list_without_tabu)
    if len(tabu_list) == len(routing_requests) or max_delay == 0:
        tabu_list = []
        max_delay = max(delays_list)
    routing_requests_max_delay_indexes = [i for i in range(len(routing_requests)) if delays_list[i] == max_delay and i not in tabu_list]
    chosen_routing_request_index = random.choice(routing_requests_max_delay_indexes)
    tabu_list.append(chosen_routing_request_index)
    neighborhood = set()
    neighborhood.add(chosen_routing_request_index)
    for i in range(AGENT_BASED_NEIGHBORHOOD_ITERATIONS):
        if len(neighborhood) == NEIGHBORHOOD_SIZE:
            break
        random_walk(warehouse, plan, neighborhood, chosen_routing_request_index, routing_requests)
        chosen_routing_request_index = random.choice(list(neighborhood))
        set(neighborhood)
    return list(neighborhood)


def get_intersection_routing_requests(neighborhood, plan, chosen_vertex):
    """
    Finds all the routs that are passing through chosen_vertex.
    """
    routs_with_chosen_vertex = [route for route in plan if chosen_vertex.coordinates in route]
    if routs_with_chosen_vertex == []:
        return
    max_time_of_chosen_vertex = max([len(route) - route[::-1].index(chosen_vertex.coordinates) - 1 for route in
                                    routs_with_chosen_vertex])
    time = random.randint(0, max_time_of_chosen_vertex)
    delta = 0
    while len(neighborhood) < NEIGHBORHOOD_SIZE and delta <= max([time, max_time_of_chosen_vertex-time]):
        for route_id, route in enumerate(plan):
            start_index = max([0, time-delta])
            end_index = min([len(route)-1, time+delta])
            sliced_route = route[start_index:end_index]
            if chosen_vertex.coordinates in sliced_route:
                neighborhood.add(route_id)
        delta += 1


def map_based_neighborhood(routing_requests, warehouse, plan):
    """
    heuristic to find a good neighborhood to replan its routes.
    Picks a random intersection vertex and collects all the routs are passing through the vertex.
    :param warehouse:
    :param routing_requests:
    :param plan:
    :return:
    """
    vertices = [vertex for vertices_list in warehouse.vertices for vertex in vertices_list]
    intersection_vertices = [vertex for vertex in vertices if len(vertex.neighbors) >= INTERSECTION_THRESHOLD]
    random_vertex = random.choice(intersection_vertices)
    queue = [random_vertex]
    neighborhood = set()
    visited = []
    while len(queue) > 0 and len(neighborhood) < NEIGHBORHOOD_SIZE:
        vertex = queue.pop(0)
        visited.append(vertex)
        if len(vertex.neighbors) >= INTERSECTION_THRESHOLD:
            get_intersection_routing_requests(neighborhood, plan, vertex)
        for neighbor in vertex.neighbors:
            if neighbor not in queue and neighbor not in visited:
                queue.append(neighbor)
    return list(neighborhood)


# global weights for adaptive heuristic
agent_based_neighborhood_weight = 1
map_based_neighborhood_weight = 1
pick_random_neighborhood_weight = 1
current_pick_func_name = None


def adaptive_neighborhood(routing_requests, warehouse, plan):
    """
    heuristic to find a good neighborhood to replan its routes.
    chooses one of the following heuristics according to their weights.
    The heuristics to choose from:
    pick_random_neighborhood,
    agent_based_neighborhood,
    map_based_neighborhoo
    """
    sum_weights = agent_based_neighborhood_weight+map_based_neighborhood_weight+pick_random_neighborhood_weight
    pick_neighborhood_functions = [agent_based_neighborhood, map_based_neighborhood, pick_random_neighborhood]
    probabilities = [agent_based_neighborhood_weight/sum_weights, map_based_neighborhood_weight/sum_weights,
                     pick_random_neighborhood_weight/sum_weights]
    pick_neighborhood_func = np.random.choice(pick_neighborhood_functions, 1, probabilities)[0]
    neighborhood = pick_neighborhood_func(routing_requests, warehouse, plan)
    global current_pick_func_name
    current_pick_func_name = pick_neighborhood_func
    return neighborhood


def update_weight(new_plan, old_plan, neighborhood):
    """
    Updates the weight of the heuristic neighborhood function according to the relative improvement.
    """
    global agent_based_neighborhood_weight
    global map_based_neighborhood_weight
    global pick_random_neighborhood_weight
    new_plan_neighborhood_cost = neighborhood_sum_of_costs(new_plan, neighborhood)
    old_plan_neighborhood_cost = neighborhood_sum_of_costs(old_plan, neighborhood)
    new_weight_comp_one = WEIGHTS_FACTOR*(max([0, old_plan_neighborhood_cost-new_plan_neighborhood_cost]))
    if current_pick_func_name == agent_based_neighborhood:
        agent_based_neighborhood_weight = new_weight_comp_one+agent_based_neighborhood_weight*(1-WEIGHTS_FACTOR)
    if current_pick_func_name == map_based_neighborhood:
        map_based_neighborhood_weight = new_weight_comp_one+map_based_neighborhood_weight*(1-WEIGHTS_FACTOR)
    if current_pick_func_name == pick_random_neighborhood:
        pick_random_neighborhood_weight = new_weight_comp_one+pick_random_neighborhood_weight*(1-WEIGHTS_FACTOR)


def generate_lns_rnd_plan(warehouse, routing_requests, neighborhood_picking_function=adaptive_neighborhood):
    """
    Supported neighborhood_picking_function: [pick_random_neighborhood, agent_based_neighborhood, map_based_neighborhood,
     adaptive_neighborhood]
    """
    plan = generate_rnd_plan(warehouse, routing_requests, True)

    for _ in range(LNS_ITERATIONS):
        plan_backup = plan.copy()

        # neighborhood contains the list of indexes of routing_requests to replan for
        neighborhood = neighborhood_picking_function(routing_requests, warehouse, plan)
        erase_routes(plan, neighborhood)
        plan = replan(warehouse, plan, neighborhood, routing_requests)
        if neighborhood_picking_function == adaptive_neighborhood:
            update_weight(plan, plan_backup, neighborhood)
        plan = pick_lower_sum_of_costs_plan(plan, plan_backup, neighborhood)

    return plan

# TODO: change RND to PP by adding rapid-random-restarts
