import random
from math import floor, sqrt
from sys import maxsize
from typing import List, Tuple, Dict, Set
import AStar
from RoutingRequest import RoutingRequest
from Warehouse import Warehouse

RANDOM_MIDPOINTS_MAX_TRIES = 5


def generate_rand_routing_requests(warehouse, waves_per_warehouse):
    sources = warehouse.sources
    num_of_sources = len(sources)
    num_of_waves = waves_per_warehouse[warehouse.warehouse_id - 1]
    routing_requests = []
    for i in range(num_of_waves):
        destinations = random.choices(warehouse.destinations, k=num_of_sources)
        for j in range(num_of_sources):
            routing_requests.append(RoutingRequest(i * num_of_sources + j, sources[j], destinations[j]))
    return routing_requests


def generate_rand_routing_request(warehouse, *unused_variables):
    source_id = random.randint(0, warehouse.number_of_sources - 1)
    destination_id = random.randint(0, warehouse.number_of_destinations - 1)
    source = warehouse.sources[source_id]
    destination = warehouse.destinations[destination_id]

    return [RoutingRequest(0, source, destination)]


def find_route_using_Astar(warehouse, plan, routing_request, is_first_routing_request=False, wait_at_source_left=0,
                           constraints: Dict[int, Set[Tuple[int, int]]] = None) -> List[Tuple[int, int]]:
    routing_request_vertex = routing_request.source
    source_node = AStar.AStar.Node(routing_request_vertex, routing_request_vertex.destination_distance[routing_request.destination.destination_id], 0,
                             None, True)
    destination_node = AStar.AStar.Node(routing_request.destination, 0, maxsize, None, False)
    a_star_framework = AStar.AStar(source_node, destination_node)
    route = a_star_framework.space_time_search(warehouse, routing_request, plan, is_first_routing_request, wait_at_source_left, constraints)
    return route


def order_routing_requests_by_key(routing_requests, value_function):
    sorted_routing_requests = sorted(routing_requests, key=value_function)
    sorted_routing_request_ids = [routing_request.routing_request_id for routing_request in sorted_routing_requests]

    return sorted_routing_request_ids


def order_routing_requests_by_destination_id(routing_requests):
    return order_routing_requests_by_key(routing_requests, RoutingRequest.get_destination_id)


def order_routing_requests_by_source_id(routing_requests):
    return order_routing_requests_by_key(routing_requests, RoutingRequest.get_source_id)


def order_routing_requests_by_source_then_destination_id(routing_requests):
    sorted_routing_requests = sorted(routing_requests, key=RoutingRequest.get_destination_id)
    sorted_routing_requests = sorted(sorted_routing_requests, key=RoutingRequest.get_source_id)

    sorted_routing_request_ids = [routing_request.routing_request_id for routing_request in sorted_routing_requests]
    return sorted_routing_request_ids


def get_destination_id_from_route(warehouse, route):
    routing_request_final_coordinates = route[-1]
    routing_request_destination = warehouse.vertices[routing_request_final_coordinates[0]][routing_request_final_coordinates[1]]
    return routing_request_destination.destination_id


def get_source_id_from_route(warehouse, route):
    routing_request_initial_coordinates = route[0]
    routing_request_source = warehouse.vertices[routing_request_initial_coordinates[0]][routing_request_initial_coordinates[1]]
    return routing_request_source.source_id


def get_warehouse_grid(warehouse):
    x_indices, y_indices = [], []

    x_step_size, y_step_size = floor(sqrt(warehouse.length)), floor(sqrt(warehouse.width))
    i = 0
    while i * x_step_size < warehouse.length:
        x_indices.append(i * x_step_size)
        i += 1
    if warehouse.length - 1 not in x_indices:
        x_indices.append(warehouse.length - 1)

    i = 0
    while i * y_step_size < warehouse.width:
        y_indices.append(i * y_step_size)
        i += 1
    if warehouse.width - 1 not in y_indices:
        y_indices.append(warehouse.width - 1)

    return x_indices, y_indices


def get_random_points_throughout_warehouse(warehouse):
    midpoints = set()
    x_indices, y_indices = get_warehouse_grid(warehouse)

    for i in range(len(x_indices) - 1):
        for j in range(len(y_indices) - 1):
            for _ in range(RANDOM_MIDPOINTS_MAX_TRIES):
                sampled_vertex = (random.randrange(x_indices[i], x_indices[i + 1]),
                                  random.randrange(y_indices[j], y_indices[j + 1]))
                if warehouse.is_valid_vertex(sampled_vertex[0], sampled_vertex[1]):
                    midpoints.add(sampled_vertex)
                    break

    return midpoints


def generate_warehouse(warehouse_id):
    # First warehouse in original paper
    if warehouse_id == 1:
        length = 100
        width = 150
        number_of_sources = 14
        number_of_destinations = 9
        obstacle_length = round(0.1 * length)
        obstacle_width = round(0.1 * width)

        return Warehouse(warehouse_id, length, width, number_of_sources, number_of_destinations, obstacle_length,
                         obstacle_width)

    # Toy warehouse
    if warehouse_id == 2:
        length = 10
        width = 10
        number_of_sources = 3
        number_of_destinations = 2
        obstacle_length = round(0.1 * length)
        obstacle_width = round(0.1 * width)

        return Warehouse(warehouse_id, length, width, number_of_sources, number_of_destinations, obstacle_length,
                         obstacle_width)

    # small warehouse
    if warehouse_id == 3:
        length = 40
        width = 40
        number_of_sources = 7
        number_of_destinations = 7
        obstacle_length = round(0.1 * length)
        obstacle_width = round(0.1 * width)

        return Warehouse(warehouse_id, length, width, number_of_sources, number_of_destinations, obstacle_length,
                         obstacle_width)

    # mid warehouse
    if warehouse_id == 4:
        length = 40
        width = 40
        number_of_sources = 9
        number_of_destinations = 1
        obstacle_length = round(0.1 * length)
        obstacle_width = round(0.1 * width)

        return Warehouse(warehouse_id, length, width, number_of_sources, number_of_destinations, obstacle_length,
                         obstacle_width)


def is_energy_cost_valid(warehouse, energy_cost):
    return energy_cost < warehouse.length + warehouse.width


def is_valid_route_length(warehouse, route):
    return is_energy_cost_valid(warehouse, len(route))


def get_all_source_and_destination_combinations(warehouse):
    combinations = []
    for i in range(len(warehouse.sources)):
        for j in range(len(warehouse.destinations)):
            combinations.append((i, j))

    return combinations


def count_edge_conflicts(plan):
    count = 0
    for i in range(len(plan)):
        for j in range(len(plan)):
            if i <= j:
                continue

            for time in range(min(len(plan[i]), len(plan[j])) - 1):
                is_agent_at_source = plan[i][time] == plan[i][0]
                is_agent_at_destination = plan[i][time] == plan[i][-1]

                if is_agent_at_source or is_agent_at_destination:
                    continue

                if plan[i][time + 1] == plan[j][time] and plan[i][time] == plan[j][time + 1]:
                    count += 1
    return count


def count_vertex_conflicts(plan):
    count = 0
    for i in range(len(plan)):
        for j in range(len(plan)):
            if i <= j:
                continue

            for time in range(min(len(plan[i]), len(plan[j]))):
                is_agent_at_source = plan[i][time] == plan[i][0]
                is_agent_at_destination = plan[i][time] == plan[i][-1]

                if is_agent_at_source or is_agent_at_destination:
                    continue

                if plan[i][time] == plan[j][time]:
                    count += 1
    return count


def count_plan_conflicts(plan):
    vertex_conflicts = count_vertex_conflicts(plan)
    edge_conflicts = count_edge_conflicts(plan)

    return vertex_conflicts, edge_conflicts
